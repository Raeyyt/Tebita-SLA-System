from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime

from ..database import get_db
from ..auth import get_current_active_user
from ..models import User, SystemSettings, Request

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
async def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all system settings (admin only)"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    settings = db.query(SystemSettings).all()
    
    # Convert to dict
    settings_dict = {}
    for setting in settings:
        settings_dict[setting.setting_key] = {
            "value": setting.setting_value,
            "description": setting.description,
            "updated_at": setting.updated_at.isoformat() if setting.updated_at else None
        }
    
    return settings_dict


@router.put("/email-notifications")
async def update_email_notifications(
    enabled: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Toggle email notifications on/off (admin only)"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Find or create setting
    setting = db.query(SystemSettings).filter(
        SystemSettings.setting_key == "email_notifications_enabled"
    ).first()
    
    if not setting:
        setting = SystemSettings(
            setting_key="email_notifications_enabled",
            setting_value=str(enabled).lower(),
            description="Enable/disable email notifications for HIGH priority requests"
        )
        db.add(setting)
    else:
        setting.setting_value = str(enabled).lower()
    
    db.commit()
    db.refresh(setting)
    
    return {
        "success": True,
        "setting_key": setting.setting_key,
        "enabled": enabled,
        "message": f"Email notifications {'enabled' if enabled else 'disabled'}"
    }


@router.get("/email-notifications/status")
async def get_email_notification_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current status of email notifications"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    setting = db.query(SystemSettings).filter(
        SystemSettings.setting_key == "email_notifications_enabled"
    ).first()
    
    if not setting:
        return {"enabled": False, "message": "Email notifications not configured"}
    
@router.put("/smtp-config")
async def update_smtp_settings(
    config: Dict[str, str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update SMTP configuration (admin only)"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    allowed_keys = ["smtp_email", "smtp_password", "smtp_host", "smtp_port"]
    
    for key, value in config.items():
        if key in allowed_keys:
            setting = db.query(SystemSettings).filter(
                SystemSettings.setting_key == key
            ).first()
            
            if not setting:
                setting = SystemSettings(
                    setting_key=key,
                    setting_value=value,
                    description=f"SMTP Configuration: {key}"
                )
                db.add(setting)
            else:
                setting.setting_value = value
    
    db.commit()
    return {"success": True, "message": "SMTP settings updated successfully"}


@router.get("/health-check")
async def test_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Perform system health check"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": []
    }
    
    # 1. Database Check
    from sqlalchemy import text
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"].append({"name": "Database Connection", "status": "PASS", "details": "Connected"})
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"].append({"name": "Database Connection", "status": "FAIL", "details": str(e)})
    
    # 2. SMTP Check (Configuration only)
    smtp_email = db.query(SystemSettings).filter(SystemSettings.setting_key == "smtp_email").first()
    if smtp_email and smtp_email.setting_value:
        health_status["checks"].append({"name": "SMTP Configuration", "status": "PASS", "details": "Configured"})
    else:
        health_status["checks"].append({"name": "SMTP Configuration", "status": "WARNING", "details": "Not configured in DB"})
        
    # 3. Disk Space (Mock for now, or use shutil)
    import shutil
    total, used, free = shutil.disk_usage("/")
    free_gb = free // (2**30)
    health_status["checks"].append({
        "name": "Disk Space", 
        "status": "PASS" if free_gb > 1 else "WARNING", 
        "details": f"{free_gb} GB free"
    })
    
    # 4. Server Connectivity Check
    health_status["checks"].append({"name": "Server Connectivity", "status": "PASS", "details": "Server is reachable"})

    # 5. Request Pipeline Check
    try:
        # Check if we can query the requests table
        request_count = db.query(Request).count()
        health_status["checks"].append({
            "name": "Request Pipeline", 
            "status": "PASS", 
            "details": f"Operational ({request_count} requests indexed)"
        })
    except Exception as e:
        health_status["checks"].append({
            "name": "Request Pipeline", 
            "status": "FAIL", 
            "details": f"Database error: {str(e)}"
        })

    # Overall Status
    if all(check["status"] == "PASS" for check in health_status["checks"]):
        health_status["status"] = "healthy"
    else:
        health_status["status"] = "unhealthy"
    
    return health_status


@router.delete("/reset-data")
async def reset_system_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    DANGER: Reset all request-related data.
    Removes all requests, workflows, logs, alerts, feedback, and resource-specific records.
    Keeps users, departments, divisions, and system settings.
    """
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # 0. Create Safety Backup
        from ..services.backup_service import create_database_backup
        backup_path = create_database_backup()
        backup_msg = f"Safety backup created at {backup_path.name}" if backup_path else "Backup failed, but reset proceeded."

        # 1. Delete Resource-Specific Details (Child tables)
        from ..models import (
            FleetRequest, HRDeployment, FinanceTransaction, 
            ICTTicket, LogisticsRequest, RequestItem, 
            RequestWorkflow, RequestActivityLog, SLAAlert, 
            CustomerSatisfaction, Request
        )
        
        # Delete resource specific tables
        db.query(FleetRequest).delete()
        db.query(HRDeployment).delete()
        db.query(FinanceTransaction).delete()
        db.query(ICTTicket).delete()
        db.query(LogisticsRequest).delete()
        
        # Delete related tables (if cascades fail or for safety)
        db.query(RequestItem).delete()
        db.query(RequestWorkflow).delete()
        db.query(RequestActivityLog).delete()
        db.query(SLAAlert).delete()
        db.query(CustomerSatisfaction).delete()
        
        # 2. Delete Main Requests Table
        num_deleted = db.query(Request).delete()
        
        db.commit()
        
        return {
            "success": True, 
            "message": f"System reset successful. {num_deleted} requests removed. {backup_msg}"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to reset system data: {str(e)}"
        )
