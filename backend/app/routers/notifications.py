"""Add notification badge component and API endpoint"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..database import get_db
from ..auth import get_current_active_user
from ..models import User, Request, RequestStatus

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get count of unread/pending requests for current user"""
    
    # Count based on role
    if current_user.role == "ADMIN":
        # Admin sees all pending requests
        count = db.query(Request).filter(
            Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS])
        ).count()
    elif current_user.role == "DIVISION_MANAGER":
        # Division managers see pending requests assigned DIRECTLY to their division
        count = db.query(Request).filter(
            and_(
                Request.assigned_division_id == current_user.division_id,
                Request.assigned_department_id.is_(None),
                Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS])
            )
        ).count()
    elif current_user.role == "DEPARTMENT_HEAD":
        # Department heads see pending requests assigned DIRECTLY to their department
        count = db.query(Request).filter(
            and_(
                Request.assigned_department_id == current_user.department_id,
                Request.assigned_subdepartment_id.is_(None),
                Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS])
            )
        ).count()
    else:  # SUB_DEPARTMENT_STAFF
        # Staff see pending requests assigned to their sub-department
        count = db.query(Request).filter(
            and_(
                Request.assigned_subdepartment_id == current_user.subdepartment_id,
                Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS])
            )
        ).count() if current_user.subdepartment_id else 0
    
    return {"count": count}
