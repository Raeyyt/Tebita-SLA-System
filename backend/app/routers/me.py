from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
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
        
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Helper to apply filtering
        def filter_reqs(query):
            return apply_role_based_filtering(query, current_user)

        # Total requests
        total_requests = filter_reqs(db.query(Request)).count()
        
        # Requests by status
        pending = filter_reqs(db.query(Request).filter(Request.status == RequestStatus.PENDING)).count()
        approval_pending = filter_reqs(db.query(Request).filter(Request.status == RequestStatus.APPROVAL_PENDING)).count()
        in_progress = filter_reqs(db.query(Request).filter(Request.status == RequestStatus.IN_PROGRESS)).count()
        completed = filter_reqs(db.query(Request).filter(Request.status == RequestStatus.COMPLETED)).count()
        
        # Today's activity
        today_submitted = filter_reqs(db.query(Request).filter(Request.created_at >= today_start)).count()
        today_completed = filter_reqs(db.query(Request).filter(
            Request.status == RequestStatus.COMPLETED,
            Request.completed_at >= today_start
        )).count()
        
        # SLA compliance (this month) - FIXED to calculate deadlines properly
        # Uses created_at + sla_completion_time_hours instead of sla_completion_deadline
        now = datetime.utcnow()  # Use timezone-naive to match created_at
        
        # Get completed requests this month with SLA time defined
        month_completed = filter_reqs(db.query(Request).filter(
            Request.status == RequestStatus.COMPLETED,
            Request.completed_at >= month_start,
            Request.sla_completion_time_hours.isnot(None),
            Request.created_at.isnot(None),
            Request.actual_completion_time.isnot(None)
        )).all()
        
        within_sla_completed = 0
        missed_sla_completed = 0
        
        for req in month_completed:
            deadline = req.created_at + timedelta(hours=req.sla_completion_time_hours)
            if req.actual_completion_time <= deadline:
                within_sla_completed += 1
            else:
                missed_sla_completed += 1
        
        # Get currently overdue active requests
        active_requests = filter_reqs(db.query(Request).filter(
            Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS]),
            Request.sla_completion_time_hours.isnot(None),
            Request.created_at.isnot(None)
        )).all()
        
        overdue_active = 0
        for req in active_requests:
            deadline = req.created_at + timedelta(hours=req.sla_completion_time_hours)
            if now > deadline:
                overdue_active += 1
        
        # Total requests to evaluate
        total_evaluated = within_sla_completed + missed_sla_completed + overdue_active
        sla_compliance = (within_sla_completed / total_evaluated * 100) if total_evaluated > 0 else 100
        
        # Requests by division (counts)
        div_stats_query = db.query(
            Division.name,
            func.count(Request.id).label('count')
        ).join(Request, Request.requester_division_id == Division.id)
        
        # Apply filtering to the join
        div_stats_query = apply_role_based_filtering(div_stats_query, current_user, model=Request)
        
        division_stats = div_stats_query.group_by(Division.name).all()

        # Recent request activity (latest 50)
        recent_query = db.query(Request).options(
            joinedload(Request.requester_division),
            joinedload(Request.requester_department)
        ).order_by(Request.created_at.desc())
        
        recent_requests = filter_reqs(recent_query).limit(50).all()
        
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
        
        # Overdue requests - FIXED to calculate deadlines properly
        active_requests = filter_reqs(db.query(Request).filter(
            Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS]),
            Request.sla_completion_time_hours.isnot(None),
            Request.created_at.isnot(None)
        )).all()
        
        overdue_count = 0
        for req in active_requests:
            deadline = req.created_at + timedelta(hours=req.sla_completion_time_hours)
            if now > deadline:
                overdue_count += 1
        
        return {
            "total_requests": total_requests,
            "status_breakdown": {
                "pending": pending,
                "approval_pending": approval_pending,
                "in_progress": in_progress,
                "completed": completed,
            },
            "today": {
                "submitted": today_submitted,
                "completed": today_completed,
            },
            "sla_compliance_month": round(sla_compliance, 2),
            "overdue_requests": overdue_count,
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
