"""Dashboard statistics router"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import get_current_active_user
from ..models import Request, SLAAlert, RequestStatus, User
from .. import schemas
from ..services.access_control import apply_role_based_filtering

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard statistics"""
    
    # Base query with role-based filtering
    base_query = db.query(Request)
    base_query = apply_role_based_filtering(base_query, current_user)
    
    # Total requests
    total_requests = base_query.count()
    
    # Pending approval
    pending_approval = base_query.filter(
        Request.status == RequestStatus.APPROVAL_PENDING
    ).count()
    
    # In progress
    in_progress = base_query.filter(
        Request.status == RequestStatus.IN_PROGRESS
    ).count()
    
    # Completed
    completed = base_query.filter(
        Request.status == RequestStatus.COMPLETED
    ).count()
    
    # Overdue requests (created more than SLA hours ago and not completed)
    now = datetime.now()
    overdue = 0
    active_requests = base_query.filter(
        Request.status.in_([RequestStatus.PENDING, RequestStatus.APPROVAL_PENDING, RequestStatus.IN_PROGRESS])
    ).all()
    
    for req in active_requests:
        if not req.created_at or not req.sla_response_time_hours:
            continue
        hours_elapsed = (now - req.created_at).total_seconds() / 3600
        if hours_elapsed > req.sla_response_time_hours:
            overdue += 1
    
    # SLA compliance (percentage of requests completed within SLA)
    completed_requests = base_query.filter(
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
    active_alerts_query = db.query(SLAAlert).join(Request).filter(
        SLAAlert.acknowledged_at.is_(None)
    )
    active_alerts_query = apply_role_based_filtering(active_alerts_query, current_user, model=Request)
    active_alerts = active_alerts_query.count()
    
    return {
        "total_requests": total_requests,
        "pending_approval": pending_approval,
        "in_progress": in_progress,
        "completed": completed,
        "overdue": overdue,
        "sla_compliance": sla_compliance,
        "active_alerts": active_alerts
    }
