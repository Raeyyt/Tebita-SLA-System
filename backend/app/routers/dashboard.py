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
    from sqlalchemy import and_, or_, case, String, extract
    
    # Base query with role-based filtering
    base_query = db.query(Request)
    base_query = apply_role_based_filtering(base_query, current_user)
    
    # 1. Get counts in one query
    stats = base_query.with_entities(
        func.count(Request.id).label("total"),
        func.count(case((Request.status == RequestStatus.APPROVAL_PENDING, 1))).label("pending_approval"),
        func.count(case((Request.status == RequestStatus.IN_PROGRESS, 1))).label("in_progress"),
        func.count(case((Request.status == RequestStatus.COMPLETED, 1))).label("completed")
    ).one()
    
    # 2. Overdue requests (SQL-based) - Align with sla.py logic
    overdue = base_query.filter(
        Request.status.in_([RequestStatus.PENDING, RequestStatus.APPROVAL_PENDING, RequestStatus.IN_PROGRESS, RequestStatus.APPROVED]),
        or_(
            # Response overdue
            and_(
                Request.acknowledged_at.is_(None),
                extract('epoch', func.now()) > extract('epoch', Request.created_at) + (func.coalesce(Request.sla_response_time_hours, 2) * 3600)
            ),
            # Resolution overdue
            extract('epoch', func.now()) > extract('epoch', Request.created_at) + (func.coalesce(Request.sla_completion_time_hours, 24) * 3600)
        )
    ).with_entities(func.count(Request.id)).scalar() or 0
    
    # 3. SLA compliance (SQL-based)
    # A request is compliant ONLY if both response and resolution SLAs are met
    # We include active overdue requests in the denominator for a real-time view
    actual_resp = func.coalesce(Request.actual_response_time, Request.acknowledged_at)
    actual_comp = func.coalesce(Request.actual_completion_time, Request.completed_at)
    
    total_completed = stats.completed or 0
    total_evaluated = total_completed + overdue
    
    if total_evaluated == 0:
        sla_compliance = 100.0
    else:
        compliant_count = base_query.filter(
            Request.status == RequestStatus.COMPLETED
        ).with_entities(
            func.count(case((
                and_(
                    actual_resp.isnot(None),
                    actual_comp.isnot(None),
                    # Response SLA met
                    extract('epoch', actual_resp) <= 
                    extract('epoch', Request.created_at) + (func.coalesce(Request.sla_response_time_hours, 2) * 3600),
                    # Resolution SLA met
                    extract('epoch', actual_comp) <= 
                    extract('epoch', Request.created_at) + (func.coalesce(Request.sla_completion_time_hours, 24) * 3600)
                ), 1
            )))
        ).scalar() or 0
        sla_compliance = round((compliant_count / total_evaluated * 100), 1)
    
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
