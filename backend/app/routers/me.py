from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract, case, and_, or_
from typing import List
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import get_current_active_user
from ..models import Request, User, Division, Department, RequestStatus
from .. import schemas

router = APIRouter(prefix="/me", tags=["me_monitoring"])


@router.get("/dashboard")
async def get_me_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        from ..services.access_control import apply_role_based_filtering
        from sqlalchemy import case, extract, and_
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now - timedelta(days=30)
        
        # Base query with role-based filtering
        base_query = db.query(Request)
        base_query = apply_role_based_filtering(base_query, current_user)
        
        # 1. Get all counts in one query
        stats = db.query(
            func.count(Request.id).label("total"),
            func.count(case((Request.status == RequestStatus.PENDING, 1))).label("pending"),
            func.count(case((Request.status == RequestStatus.APPROVAL_PENDING, 1))).label("approval_pending"),
            func.count(case((Request.status == RequestStatus.IN_PROGRESS, 1))).label("in_progress"),
            func.count(case((Request.status == RequestStatus.COMPLETED, 1))).label("completed"),
            func.count(case((Request.created_at >= today_start, 1))).label("today_submitted"),
            func.count(case((and_(Request.status == RequestStatus.COMPLETED, Request.completed_at >= today_start), 1))).label("today_completed")
        ).filter(base_query.whereclause).one()
        
        # 2. SLA Compliance (SQL-based)
        now_epoch = extract('epoch', func.now())
        created_epoch = extract('epoch', Request.created_at)
        resp_target = func.coalesce(Request.sla_response_time_hours, 2) * 3600
        res_target = func.coalesce(Request.sla_completion_time_hours, 24) * 3600
        
        sla_stats = db.query(
            func.count(case((
                and_(
                    # Response SLA met
                    extract('epoch', Request.actual_response_time) <= created_epoch + resp_target,
                    # Resolution SLA met
                    extract('epoch', Request.actual_completion_time) <= created_epoch + res_target
                ), 1
            ))).label("compliant"),
            func.count(case((
                or_(
                    and_(Request.status == RequestStatus.COMPLETED, Request.completed_at >= month_start),
                    # Response overdue (if not yet acknowledged)
                    and_(
                        Request.acknowledged_at.is_(None),
                        now_epoch > created_epoch + resp_target
                    ),
                    # Resolution overdue
                    now_epoch > created_epoch + res_target
                ), 1
            ))).label("evaluated"),
            func.count(case((
                or_(
                    # Response overdue (if not yet acknowledged)
                    and_(
                        Request.acknowledged_at.is_(None),
                        now_epoch > created_epoch + resp_target
                    ),
                    # Resolution overdue (active only)
                    and_(
                        Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS]),
                        now_epoch > created_epoch + res_target
                    )
                ), 1
            ))).label("overdue_active")
        ).filter(base_query.whereclause).one()
        
        sla_compliance = (sla_stats.compliant / sla_stats.evaluated * 100) if sla_stats.evaluated > 0 else 100
        
        # 3. Requests by division (counts)
        division_stats = db.query(
            Division.name,
            func.count(Request.id).label('count')
        ).join(Request, Request.requester_division_id == Division.id).filter(
            base_query.whereclause
        ).group_by(Division.name).all()

        # 4. Recent request activity (latest 50)
        recent_requests = db.query(Request).options(
            joinedload(Request.requester_division),
            joinedload(Request.requester_department)
        ).filter(base_query.whereclause).order_by(Request.created_at.desc()).limit(50).all()
        
        division_requests = [
            {
                "division": req.requester_division.name if req.requester_division else None,
                "department": req.requester_department.name if req.requester_department else None,
                "request_id": req.request_id,
                "description": req.description,
                "created_at": req.created_at.isoformat() if req.created_at else None,
            }
            for req in recent_requests
        ]
        
        return {
            "total_requests": stats.total or 0,
            "status_breakdown": {
                "pending": stats.pending or 0,
                "approval_pending": stats.approval_pending or 0,
                "in_progress": stats.in_progress or 0,
                "completed": stats.completed or 0,
            },
            "today": {
                "submitted": stats.today_submitted or 0,
                "completed": stats.today_completed or 0,
            },
            "sla_compliance_month": round(sla_compliance, 2),
            "overdue_requests": sla_stats.overdue_active or 0,
            "division_stats": [{"division": name, "count": count} for name, count in division_stats],
            "division_requests": division_requests,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error in ME Dashboard: {str(e)}")


@router.get("/validation-queue")
async def get_validation_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get requests pending M&E validation"""
    from ..services.access_control import apply_role_based_filtering
    
    # Requests that need validation (completed but not yet validated)
    query = db.query(Request).filter(
        Request.status == RequestStatus.COMPLETED
    ).order_by(Request.completed_at.desc())
    
    query = apply_role_based_filtering(query, current_user)
    
    return query.limit(20).all()


@router.get("/activity-log")
async def get_activity_log(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get recent activity across all requests"""
    from ..services.access_control import apply_role_based_filtering
    
    query = db.query(Request).order_by(Request.created_at.desc())
    query = apply_role_based_filtering(query, current_user)
    
    return query.limit(limit).all()
