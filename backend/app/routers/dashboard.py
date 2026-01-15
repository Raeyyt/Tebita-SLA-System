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

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard statistics using optimized SQL aggregations"""
    from sqlalchemy import and_, or_, case, String
    
    # Base query with role-based filtering
    base_query = db.query(Request)
    base_query = apply_role_based_filtering(base_query, current_user)
    
    # 1. Get counts in one query
    stats = db.query(
        func.count(Request.id).label("total"),
        func.count(case((Request.status == RequestStatus.APPROVAL_PENDING, 1))).label("pending_approval"),
        func.count(case((Request.status == RequestStatus.IN_PROGRESS, 1))).label("in_progress"),
        func.count(case((Request.status == RequestStatus.COMPLETED, 1))).label("completed")
    ).filter(base_query.whereclause).one()
    
    # 2. Overdue requests (SQL-based)
    overdue = db.query(func.count(Request.id)).filter(
        base_query.whereclause,
        Request.status.in_([RequestStatus.PENDING, RequestStatus.APPROVAL_PENDING, RequestStatus.IN_PROGRESS]),
        Request.sla_response_time_hours.isnot(None),
        extract('epoch', func.now()) > extract('epoch', Request.created_at) + (Request.sla_response_time_hours * 3600)
    ).scalar() or 0
    
    # 3. SLA compliance (SQL-based)
    compliance_stats = db.query(
        func.count(Request.id).label("total_completed"),
        func.count(case((
            and_(
                Request.completed_at.isnot(None),
                Request.created_at.isnot(None),
                Request.sla_completion_time_hours.isnot(None),
                (extract('epoch', Request.completed_at) - extract('epoch', Request.created_at)) / 3600 <= Request.sla_completion_time_hours
            ), 1
        ))).label("compliant")
    ).filter(
        base_query.whereclause,
        Request.status == RequestStatus.COMPLETED,
        Request.sla_completion_time_hours.isnot(None)
    ).one()
    
    sla_compliance = round((compliance_stats.compliant / compliance_stats.total_completed * 100) if compliance_stats.total_completed else 0, 1)
    
    # 4. SLA alerts count
    active_alerts_query = db.query(SLAAlert).join(Request).filter(
        SLAAlert.acknowledged_at.is_(None)
    )
    active_alerts_query = apply_role_based_filtering(active_alerts_query, current_user, model=Request)
    active_alerts = active_alerts_query.count()
    
    return {
        "total_requests": stats.total,
        "pending_approval": stats.pending_approval,
        "in_progress": stats.in_progress,
        "completed": stats.completed,
        "overdue": overdue,
        "sla_compliance": sla_compliance,
        "active_alerts": active_alerts
    }
