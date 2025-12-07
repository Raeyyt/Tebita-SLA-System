"""Dashboard statistics router"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Request, SLAAlert, RequestStatus
from .. import schemas

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    
    # Total requests
    total_requests = db.query(Request).count()
    
    # Pending approval
    pending_approval = db.query(Request).filter(
        Request.status == RequestStatus.APPROVAL_PENDING
    ).count()
    
    # In progress
    in_progress = db.query(Request).filter(
        Request.status == RequestStatus.IN_PROGRESS
    ).count()
    
    # Completed
    completed = db.query(Request).filter(
        Request.status == RequestStatus.COMPLETED
    ).count()
    
    # Overdue requests (created more than SLA hours ago and not completed)
    now = datetime.now()
    overdue = 0
    active_requests = db.query(Request).filter(
        Request.status.in_([RequestStatus.PENDING, RequestStatus.APPROVAL_PENDING, RequestStatus.IN_PROGRESS])
    ).all()
    
    for req in active_requests:
        if not req.created_at or not req.sla_response_time_hours:
            continue
        hours_elapsed = (now - req.created_at).total_seconds() / 3600
        if hours_elapsed > req.sla_response_time_hours:
            overdue += 1
    
    # SLA compliance (percentage of requests completed within SLA)
    completed_requests = db.query(Request).filter(
        Request.status == RequestStatus.COMPLETED,
        Request.completed_at.isnot(None)
    ).all()
    
    compliant = 0
    total_with_sla = 0
    for req in completed_requests:
        if not req.created_at or not req.completed_at or not req.sla_completion_time_hours:
            continue
        total_with_sla += 1
        hours_taken = (req.completed_at - req.created_at).total_seconds() / 3600
        if hours_taken <= req.sla_completion_time_hours:
            compliant += 1
    
    sla_compliance = round((compliant / total_with_sla * 100) if total_with_sla else 0, 1)
    
    # SLA alerts count
    active_alerts = db.query(SLAAlert).filter(
        SLAAlert.acknowledged_at.is_(None)
    ).count()
    
    return {
        "total_requests": total_requests,
        "pending_approval": pending_approval,
        "in_progress": in_progress,
        "completed": completed,
        "overdue": overdue,
        "sla_compliance": sla_compliance,
        "active_alerts": active_alerts
    }
