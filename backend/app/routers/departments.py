from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth import get_current_active_user
from ..models import Department, User, UserRole
from .. import schemas

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("/", response_model=List[schemas.DepartmentRead])
async def get_departments(
    division_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all departments, optionally filtered by division"""
    query = db.query(Department)
    if division_id:
        query = query.filter(Department.division_id == division_id)
    departments = query.all()
    return departments


@router.post("/", response_model=schemas.DepartmentRead, status_code=status.HTTP_201_CREATED)
async def create_department(
    department_in: schemas.DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new department (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    department = Department(**department_in.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.get("/{department_id}", response_model=schemas.DepartmentRead)
async def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific department"""
    department = db.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.get("/{department_id}/subdepartments", response_model=List[schemas.SubDepartmentRead])
async def get_department_subdepartments(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get subdepartments for a specific department"""
    # Verify department exists
    department = db.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
        
    return department.subdepartments


@router.post("/{department_id}/subdepartments", response_model=schemas.SubDepartmentRead, status_code=status.HTTP_201_CREATED)
async def create_subdepartment(
    department_id: int,
    subdepartment_in: schemas.SubDepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new subdepartment (Admin only)"""
    from ..models import SubDepartment
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Verify department exists
    department = db.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    subdepartment = SubDepartment(
        name=subdepartment_in.name,
        department_id=department_id
    )
    db.add(subdepartment)
    db.commit()
    db.refresh(subdepartment)
    return subdepartment
