from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
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
    """M&E Dashboard - Central monitoring hub"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    # Total requests
    total_requests = db.query(Request).count()
    
    # Requests by status
    pending = db.query(Request).filter(Request.status == RequestStatus.PENDING).count()
    approval_pending = db.query(Request).filter(Request.status == RequestStatus.APPROVAL_PENDING).count()
    in_progress = db.query(Request).filter(Request.status == RequestStatus.IN_PROGRESS).count()
    completed = db.query(Request).filter(Request.status == RequestStatus.COMPLETED).count()
    
    # Today's activity
    today_submitted = db.query(Request).filter(Request.created_at >= today_start).count()
    today_completed = db.query(Request).filter(
        Request.status == RequestStatus.COMPLETED,
        Request.completed_at >= today_start
    ).count()
    
    # SLA compliance (this month)
    month_completed = db.query(Request).filter(
        Request.status == RequestStatus.COMPLETED,
        Request.completed_at >= month_start
    ).all()
    
    within_sla = 0
    for req in month_completed:
        if req.completed_at and req.created_at and req.sla_completion_time_hours:
            time_taken = (req.completed_at - req.created_at).total_seconds() / 3600
            if time_taken <= req.sla_completion_time_hours:
                within_sla += 1
    
    sla_compliance = (within_sla / len(month_completed) * 100) if month_completed else 0
    
    # Requests by division (counts)
    division_stats = db.query(
        Division.name,
        func.count(Request.id).label('count')
    ).join(Request, Request.requester_division_id == Division.id).group_by(Division.name).all()

    # Recent request activity (latest 50)
    recent_requests = (
        db.query(Request)
        .join(Division, Request.requester_division_id == Division.id)
        .outerjoin(Department, Request.requester_department_id == Department.id)
        .order_by(Request.created_at.desc())
        .limit(50)
        .all()
    )
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
    
    # Overdue requests
    active_requests = db.query(Request).filter(
        Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS, RequestStatus.APPROVED]),
        Request.sla_completion_time_hours.isnot(None)
    ).all()
    
    overdue_count = 0
    for req in active_requests:
        if req.created_at and req.sla_completion_time_hours:
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


@router.get("/validation-queue")
async def get_validation_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get requests pending M&E validation"""
    # Requests that need validation (completed but not yet validated)
    # This is a placeholder - you can add a validation status field later
    completed_requests = db.query(Request).filter(
        Request.status == RequestStatus.COMPLETED
    ).order_by(Request.completed_at.desc()).limit(20).all()
    
    return completed_requests


@router.get("/activity-log")
async def get_activity_log(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get recent activity across all requests"""
    recent_requests = db.query(Request).order_by(
        Request.created_at.desc()
    ).limit(limit).all()
    
    return recent_requests
