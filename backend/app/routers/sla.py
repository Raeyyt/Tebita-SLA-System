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
    """Get SLA compliance metrics - INCLUDES active overdue requests"""
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
    
    # Get all requests in period (not just completed)
    query = db.query(Request).filter(Request.created_at >= start)
    query = apply_role_based_filtering(query, current_user)
    
    # Get completed requests
    completed_requests = query.filter(
        Request.status == RequestStatus.COMPLETED,
        Request.sla_completion_time_hours.isnot(None),
        Request.created_at.isnot(None),
        Request.actual_completion_time.isnot(None)
    ).all()
    
    within_sla = 0
    overdue_completed = 0
    total_completion_time = 0
    
    DEFAULT_SLA_HOURS = 96
    
    # Check completed requests
    for req in completed_requests:
        target_hours = req.sla_completion_time_hours or DEFAULT_SLA_HOURS
        deadline = req.created_at + timedelta(hours=target_hours)
        
        if req.actual_completion_time <= deadline:
            within_sla += 1
        else:
            overdue_completed += 1
        
        if req.completed_at and req.created_at:
            total_completion_time += (req.completed_at - req.created_at).total_seconds() / 3600
    
    # Get active overdue requests
    active_requests = query.filter(
        Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS]),
        Request.sla_completion_time_hours.isnot(None),
        Request.created_at.isnot(None)
    ).all()
    
    overdue_active = 0
    for req in active_requests:
        target_hours = req.sla_completion_time_hours or DEFAULT_SLA_HOURS
        deadline = req.created_at + timedelta(hours=target_hours)
        if now > deadline:
            overdue_active += 1
    
    # Total calculations
    total = len(completed_requests) + len(active_requests)
    total_evaluated = within_sla + overdue_completed + overdue_active
    total_overdue = overdue_completed + overdue_active
    compliance_rate = (within_sla / total_evaluated * 100) if total_evaluated > 0 else 100
    avg_time = total_completion_time / len(completed_requests) if completed_requests else 0
    
    return {
        "total_requests": total,
        "within_sla": within_sla,
        "overdue": total_overdue,
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
