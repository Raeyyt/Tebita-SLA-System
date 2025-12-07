from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Any, List
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import get_current_active_user
from ..models import User, Request, RequestStatus, Division, Department, SubDepartment

router = APIRouter(prefix="/dashboard", tags=["role-dashboards"])


@router.get("/admin")
async def get_admin_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Full system dashboard for ADMIN users"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # System-wide statistics
    total_requests = db.query(Request).count()
    pending = db.query(Request).filter(Request.status == RequestStatus.PENDING).count()
    in_progress = db.query(Request).filter(Request.status == RequestStatus.IN_PROGRESS).count()
    completed = db.query(Request).filter(Request.status == RequestStatus.COMPLETED).count()
    
    # Division breakdown
    divisions = db.query(Division).all()
    division_stats = []
    for div in divisions:
        div_requests = db.query(Request).filter(
            Request.assigned_division_id == div.id
        ).count()
        division_stats.append({
            "id": div.id,
            "name": div.name,
            "total_requests": div_requests
        })
    
    # Department breakdown
    departments = db.query(Department).all()
    dept_stats = []
    for dept in departments:
        dept_requests = db.query(Request).filter(
            Request.assigned_department_id == dept.id
        ).count()
        dept_stats.append({
            "id": dept.id,
            "name": dept.name,
            "division_id": dept.division_id,
            "total_requests": dept_requests
        })
    
    # Recent activity
    recent_requests = db.query(Request).order_by(Request.created_at.desc()).limit(10).all()
    
    return {
        "role": "ADMIN",
        "summary": {
            "total_requests": total_requests,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed
        },
        "divisions": division_stats,
        "departments": dept_stats,
        "recent_requests": [
            {
                "id": r.id,
                "request_id": r.request_id,
                "status": r.status.value,
                "created_at": r.created_at.isoformat()
            }
            for r in recent_requests
        ]
    }


@router.get("/division-manager")
async def get_division_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Division-specific dashboard for DIVISION_MANAGER users"""
    if current_user.role != "DIVISION_MANAGER":
        raise HTTPException(status_code=403, detail="Division manager access required")
    
    if not current_user.division_id:
        raise HTTPException(status_code=400, detail="User not assigned to a division")
    
    # Division statistics
    division = db.query(Division).filter(Division.id == current_user.division_id).first()
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")
    
    # Requests for this division
    total_requests = db.query(Request).filter(
        Request.assigned_division_id == current_user.division_id
    ).count()
    
    pending = db.query(Request).filter(
        and_(
            Request.assigned_division_id == current_user.division_id,
            Request.status == RequestStatus.PENDING
        )
    ).count()
    
    in_progress = db.query(Request).filter(
        and_(
            Request.assigned_division_id == current_user.division_id,
            Request.status == RequestStatus.IN_PROGRESS
        )
    ).count()
    
    completed = db.query(Request).filter(
        and_(
            Request.assigned_division_id == current_user.division_id,
            Request.status == RequestStatus.COMPLETED
        )
    ).count()
    
    # Department breakdown within division
    departments = db.query(Department).filter(
        Department.division_id == current_user.division_id
    ).all()
    
    dept_stats = []
    for dept in departments:
        dept_requests = db.query(Request).filter(
            Request.assigned_department_id == dept.id
        ).count()
        dept_stats.append({
            "id": dept.id,
            "name": dept.name,
            "total_requests": dept_requests
        })
    
    return {
        "role": "DIVISION_MANAGER",
        "division": {
            "id": division.id,
            "name": division.name,
            "type": division.type.value
        },
        "summary": {
            "total_requests": total_requests,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed
        },
        "departments": dept_stats
    }


@router.get("/department-head")
async def get_department_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Department-specific dashboard for DEPARTMENT_HEAD users"""
    if current_user.role != "DEPARTMENT_HEAD":
        raise HTTPException(status_code=403, detail="Department head access required")
    
    if not current_user.department_id:
        raise HTTPException(status_code=400, detail="User not assigned to a department")
    
    # Department statistics
    department = db.query(Department).filter(Department.id == current_user.department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Requests for this department
    total_requests = db.query(Request).filter(
        Request.assigned_department_id == current_user.department_id
    ).count()
    
    pending = db.query(Request).filter(
        and_(
            Request.assigned_department_id == current_user.department_id,
            Request.status == RequestStatus.PENDING
        )
    ).count()
    
    in_progress = db.query(Request).filter(
        and_(
            Request.assigned_department_id == current_user.department_id,
            Request.status == RequestStatus.IN_PROGRESS
        )
    ).count()
    
    completed = db.query(Request).filter(
        and_(
            Request.assigned_department_id == current_user.department_id,
            Request.status == RequestStatus.COMPLETED
        )
    ).count()
    
    # Sub-department breakdown
    subdepartments = db.query(SubDepartment).filter(
        SubDepartment.department_id == current_user.department_id
    ).all()
    
    subdept_stats = []
    for subdept in subdepartments:
        subdept_requests = db.query(Request).filter(
            Request.assigned_subdepartment_id == subdept.id
        ).count()
        subdept_stats.append({
            "id": subdept.id,
            "name": subdept.name,
            "total_requests": subdept_requests
        })
    
    return {
        "role": "DEPARTMENT_HEAD",
        "department": {
            "id": department.id,
            "name": department.name,
            "division_id": department.division_id
        },
        "summary": {
            "total_requests": total_requests,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed
        },
        "subdepartments": subdept_stats
    }


@router.get("/staff")
async def get_staff_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Simple dashboard for SUB_DEPARTMENT_STAFF users"""
    if current_user.role != "SUB_DEPARTMENT_STAFF":
        raise HTTPException(status_code=403, detail="Staff access required")
    
    # My sent requests
    sent_requests = db.query(Request).filter(
        Request.requester_id == current_user.id
    ).count()
    
    # My received requests
    received_requests = db.query(Request).filter(
        Request.assigned_subdepartment_id == current_user.subdepartment_id
    ).count() if current_user.subdepartment_id else 0
    
    # Pending requests I need to handle
    pending_to_handle = db.query(Request).filter(
        and_(
            Request.assigned_subdepartment_id == current_user.subdepartment_id,
            Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS])
        )
    ).count() if current_user.subdepartment_id else 0
    
    return {
        "role": "SUB_DEPARTMENT_STAFF",
        "summary": {
            "sent_requests": sent_requests,
            "received_requests": received_requests,
            "pending_to_handle": pending_to_handle
        }
    }
