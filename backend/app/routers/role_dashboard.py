from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, extract
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
    """Full system dashboard for ADMIN users using optimized SQL"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from sqlalchemy import case
    
    # 1. System-wide statistics in one query
    stats = db.query(
        func.count(Request.id).label("total"),
        func.count(case((Request.status == RequestStatus.PENDING, 1))).label("pending"),
        func.count(case((Request.status == RequestStatus.IN_PROGRESS, 1))).label("in_progress"),
        func.count(case((Request.status == RequestStatus.COMPLETED, 1))).label("completed")
    ).one()
    
    # 2. Division breakdown in one query
    division_results = db.query(
        Division.id,
        Division.name,
        func.count(Request.id).label('count')
    ).outerjoin(Request, Request.assigned_division_id == Division.id).group_by(Division.id, Division.name).all()
    
    division_stats = [
        {"id": r.id, "name": r.name, "total_requests": r.count}
        for r in division_results
    ]
    
    # 3. Department breakdown in one query
    department_results = db.query(
        Department.id,
        Department.name,
        Department.division_id,
        func.count(Request.id).label('count')
    ).outerjoin(Request, Request.assigned_department_id == Department.id).group_by(Department.id, Department.name, Department.division_id).all()
    
    dept_stats = [
        {"id": r.id, "name": r.name, "division_id": r.division_id, "total_requests": r.count}
        for r in department_results
    ]
    
    # 4. Recent activity
    recent_requests = db.query(Request).order_by(Request.created_at.desc()).limit(10).all()
    
    return {
        "role": "ADMIN",
        "summary": {
            "total_requests": stats.total or 0,
            "pending": stats.pending or 0,
            "in_progress": stats.in_progress or 0,
            "completed": stats.completed or 0
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
    """Division-specific dashboard for DIVISION_MANAGER users using optimized SQL"""
    if current_user.role != "DIVISION_MANAGER":
        raise HTTPException(status_code=403, detail="Division manager access required")
    
    if not current_user.division_id:
        raise HTTPException(status_code=400, detail="User not assigned to a division")
    
    from sqlalchemy import case
    
    # Division statistics
    division = db.query(Division).filter(Division.id == current_user.division_id).first()
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")
    
    # 1. Requests for this division in one query
    stats = db.query(
        func.count(Request.id).label("total"),
        func.count(case((Request.status == RequestStatus.PENDING, 1))).label("pending"),
        func.count(case((Request.status == RequestStatus.IN_PROGRESS, 1))).label("in_progress"),
        func.count(case((Request.status == RequestStatus.COMPLETED, 1))).label("completed")
    ).filter(Request.assigned_division_id == current_user.division_id).one()
    
    # 2. Department breakdown within division in one query
    department_results = db.query(
        Department.id,
        Department.name,
        func.count(Request.id).label('count')
    ).outerjoin(Request, Request.assigned_department_id == Department.id).filter(
        Department.division_id == current_user.division_id
    ).group_by(Department.id, Department.name).all()
    
    dept_stats = [
        {"id": r.id, "name": r.name, "total_requests": r.count}
        for r in department_results
    ]
    
    return {
        "role": "DIVISION_MANAGER",
        "division": {
            "id": division.id,
            "name": division.name,
            "type": division.type.value
        },
        "summary": {
            "total_requests": stats.total or 0,
            "pending": stats.pending or 0,
            "in_progress": stats.in_progress or 0,
            "completed": stats.completed or 0
        },
        "departments": dept_stats
    }


@router.get("/department-head")
async def get_department_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Department-specific dashboard for DEPARTMENT_HEAD users using optimized SQL"""
    if current_user.role != "DEPARTMENT_HEAD":
        raise HTTPException(status_code=403, detail="Department head access required")
    
    if not current_user.department_id:
        raise HTTPException(status_code=400, detail="User not assigned to a department")
    
    from sqlalchemy import case
    
    # Department statistics
    department = db.query(Department).filter(Department.id == current_user.department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # 1. Requests for this department in one query
    stats = db.query(
        func.count(Request.id).label("total"),
        func.count(case((Request.status == RequestStatus.PENDING, 1))).label("pending"),
        func.count(case((Request.status == RequestStatus.IN_PROGRESS, 1))).label("in_progress"),
        func.count(case((Request.status == RequestStatus.COMPLETED, 1))).label("completed")
    ).filter(Request.assigned_department_id == current_user.department_id).one()
    
    # 2. Sub-department breakdown in one query
    subdepartment_results = db.query(
        SubDepartment.id,
        SubDepartment.name,
        func.count(Request.id).label('count')
    ).outerjoin(Request, Request.assigned_subdepartment_id == SubDepartment.id).filter(
        SubDepartment.department_id == current_user.department_id
    ).group_by(SubDepartment.id, SubDepartment.name).all()
    
    subdept_stats = [
        {"id": r.id, "name": r.name, "total_requests": r.count}
        for r in subdepartment_results
    ]
    
    return {
        "role": "DEPARTMENT_HEAD",
        "department": {
            "id": department.id,
            "name": department.name,
            "division_id": department.division_id
        },
        "summary": {
            "total_requests": stats.total or 0,
            "pending": stats.pending or 0,
            "in_progress": stats.in_progress or 0,
            "completed": stats.completed or 0
        },
        "subdepartments": subdept_stats
    }


@router.get("/staff")
async def get_staff_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Simple dashboard for SUB_DEPARTMENT_STAFF users using optimized SQL"""
    if current_user.role != "SUB_DEPARTMENT_STAFF":
        raise HTTPException(status_code=403, detail="Staff access required")
    
    from sqlalchemy import case
    
    # 1. My sent and received requests in one query
    # This is a bit tricky since they are different filters. 
    # We'll use two simple counts or one query with union/case if possible.
    # For staff, simple counts are usually fine as they are indexed.
    
    sent_requests = db.query(func.count(Request.id)).filter(
        Request.requester_id == current_user.id
    ).scalar() or 0
    
    if current_user.subdepartment_id:
        received_stats = db.query(
            func.count(Request.id).label("total"),
            func.count(case((Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS]), 1))).label("pending")
        ).filter(Request.assigned_subdepartment_id == current_user.subdepartment_id).one()
        
        received_requests = received_stats.total or 0
        pending_to_handle = received_stats.pending or 0
    else:
        received_requests = 0
        pending_to_handle = 0
    
    return {
        "role": "SUB_DEPARTMENT_STAFF",
        "summary": {
            "sent_requests": sent_requests,
            "received_requests": received_requests,
            "pending_to_handle": pending_to_handle
        }
    }
