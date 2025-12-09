from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import get_current_active_user
from ..models import Request, RequestStatus, User, SLAAlert, AlertType
from .. import schemas
from ..services.access_control import apply_role_based_filtering

router = APIRouter(prefix="/sla", tags=["sla"])


@router.get("/compliance")
async def get_sla_compliance(
    period: str = "month",  # day, week, month, quarter
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get SLA compliance metrics"""
    # Calculate period start
    now = datetime.utcnow()
    if period == "day":
        start = now - timedelta(days=1)
    elif period == "week":
        start = now - timedelta(weeks=1)
    elif period == "quarter":
        start = now - timedelta(days=90)
    else:  # month
        start = now - timedelta(days=30)
    
    # Get completed requests in period
    query = db.query(Request).filter(
        Request.status == RequestStatus.COMPLETED,
        Request.completed_at >= start
    )
    query = apply_role_based_filtering(query, current_user)
    completed_requests = query.all()
    
    if not completed_requests:
        return {
            "total_requests": 0,
            "within_sla": 0,
            "overdue": 0,
            "compliance_rate": 0,
            "average_completion_time": 0,
        }
    
    # Calculate metrics
    within_sla = 0
    total_completion_time = 0
    
    DEFAULT_SLA_HOURS = 24

    for req in completed_requests:
        if req.completed_at and req.created_at:
            time_taken = (req.completed_at - req.created_at).total_seconds() / 3600
            target_hours = req.sla_completion_time_hours or DEFAULT_SLA_HOURS
            
            if time_taken <= target_hours:
                within_sla += 1
            
            total_completion_time += time_taken
    
    total = len(completed_requests)
    overdue = total - within_sla
    compliance_rate = (within_sla / total * 100) if total > 0 else 0
    avg_time = total_completion_time / total if total > 0 else 0
    
    return {
        "total_requests": total,
        "within_sla": within_sla,
        "overdue": overdue,
        "compliance_rate": round(compliance_rate, 2),
        "average_completion_time": round(avg_time, 2),
        "period": period,
    }


@router.get("/alerts")
async def get_active_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get active SLA alerts"""
    # Get unacknowledged alerts
    query = db.query(SLAAlert).join(Request).filter(
        SLAAlert.acknowledged_at.is_(None)
    )
    query = apply_role_based_filtering(query, current_user, model=Request)
    alerts = query.order_by(SLAAlert.sent_at.desc()).limit(50).all()
    
    return alerts


@router.get("/overdue")
async def get_overdue_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get requests that are overdue"""
    now = datetime.utcnow()
    
    # Get in-progress and pending requests
    query = db.query(Request).filter(
        Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS, RequestStatus.APPROVED]),
        Request.sla_completion_time_hours.isnot(None)
    )
    query = apply_role_based_filtering(query, current_user)
    active_requests = query.all()
    
    overdue = []
    for req in active_requests:
        if req.created_at and req.sla_completion_time_hours:
            deadline = req.created_at + timedelta(hours=req.sla_completion_time_hours)
            if now > deadline:
                time_overdue = (now - deadline).total_seconds() / 3600
                overdue.append({
                    "request": req,
                    "deadline": deadline,
                    "hours_overdue": round(time_overdue, 2),
                })
    
    return overdue


@router.get("/dashboard")
async def get_sla_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get SLA dashboard data"""
    now = datetime.utcnow()
    
    # Active requests
    query = db.query(Request).filter(
        Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS, RequestStatus.APPROVED])
    )
    query = apply_role_based_filtering(query, current_user)
    active_requests = query.all()
    
    # Categorize by SLA status
    on_track = 0
    at_risk_50 = 0  # 50-80% consumed
    critical_80 = 0  # 80%+ consumed
    overdue_count = 0
    
    DEFAULT_SLA_HOURS = 24

    for req in active_requests:
        if req.created_at:
            elapsed = (now - req.created_at).total_seconds() / 3600
            target = req.sla_completion_time_hours or DEFAULT_SLA_HOURS
            percent_consumed = (elapsed / target * 100) if target > 0 else 0
            
            if percent_consumed >= 100:
                overdue_count += 1
            elif percent_consumed >= 80:
                critical_80 += 1
            elif percent_consumed >= 50:
                at_risk_50 += 1
            else:
                on_track += 1
    
    # Today's compliance
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    query = db.query(Request).filter(
        Request.status == RequestStatus.COMPLETED,
        Request.completed_at >= today_start
    )
    query = apply_role_based_filtering(query, current_user)
    today_completed = query.count()
    
    return {
        "active_requests": len(active_requests),
        "on_track": on_track,
        "at_risk_50_percent": at_risk_50,
        "critical_80_percent": critical_80,
        "overdue": overdue_count,
        "completed_today": today_completed,
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Acknowledge an SLA alert"""
    alert = db.get(SLAAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by_user_id = current_user.id
    
    db.commit()
    return {"status": "acknowledged"}
