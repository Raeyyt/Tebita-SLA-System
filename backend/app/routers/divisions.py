from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth import get_current_active_user
from ..models import Division, User, UserRole
from .. import schemas

router = APIRouter(prefix="/divisions", tags=["divisions"])


@router.get("/", response_model=List[schemas.DivisionRead])
async def get_divisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all divisions"""
    divisions = db.query(Division).all()
    return divisions


@router.post("/", response_model=schemas.DivisionRead, status_code=status.HTTP_201_CREATED)
async def create_division(
    division_in: schemas.DivisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new division (Admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if division already exists
    existing = db.query(Division).filter(Division.name == division_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Division already exists")
    
    division = Division(**division_in.model_dump())
    db.add(division)
    db.commit()
    db.refresh(division)
    return division


@router.get("/{division_id}", response_model=schemas.DivisionRead)
async def get_division(
    division_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific division"""
    division = db.get(Division, division_id)
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")
    return division
