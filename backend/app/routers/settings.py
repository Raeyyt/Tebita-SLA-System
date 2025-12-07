from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict

from ..database import get_db
from ..auth import get_current_active_user
from ..models import User, SystemSettings

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
    
    return {
        "enabled": setting.setting_value.lower() == "true",
        "updated_at": setting.updated_at.isoformat() if setting.updated_at else None
    }
