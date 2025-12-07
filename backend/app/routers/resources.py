"""
Resource-Specific Endpoints for Phase 2
Handles Fleet, HR, Finance, ICT, and Logistics resource details
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_active_user
from ..models import (
    Request,
    FleetRequest,
    HRDeployment,
    FinanceTransaction,
    ICTTicket,
    LogisticsRequest,
    User,
    RequestStatus
)
from .. import schemas

router = APIRouter(prefix="/requests", tags=["resource-details"])


# ============================================================================
# FLEET MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/{request_id}/fleet-details", response_model=schemas.FleetRequestRead)
async def create_fleet_details(
    request_id: int,
    fleet_data: schemas.FleetRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add fleet-specific details to a request"""
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check if fleet details already exist
    existing = db.query(FleetRequest).filter(FleetRequest.request_id == request_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Fleet details already exist for this request")
    
    fleet_request = FleetRequest(
        **fleet_data.model_dump(),
        request_id=request_id
    )
    
    db.add(fleet_request)
    db.commit()
    db.refresh(fleet_request)
    return fleet_request


@router.get("/{request_id}/fleet-details", response_model=schemas.FleetRequestRead)
async def get_fleet_details(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get fleet-specific details for a request"""
    fleet_request = db.query(FleetRequest).filter(FleetRequest.request_id == request_id).first()
    if not fleet_request:
        raise HTTPException(status_code=404, detail="Fleet details not found")
    
    return fleet_request


@router.patch("/{request_id}/fleet-details", response_model=schemas.FleetRequestRead)
async def update_fleet_details(
    request_id: int,
    fleet_data: schemas.FleetRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update fleet-specific details"""
    fleet_request = db.query(FleetRequest).filter(FleetRequest.request_id == request_id).first()
    if not fleet_request:
        raise HTTPException(status_code=404, detail="Fleet details not found")
    
    # Update fields
    update_data = fleet_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(fleet_request, field, value)
    
    db.commit()
    db.refresh(fleet_request)
    return fleet_request


# ============================================================================
# HR DEPLOYMENT ENDPOINTS
# ============================================================================

@router.post("/{request_id}/hr-details", response_model=schemas.HRDeploymentRead)
async def create_hr_details(
    request_id: int,
    hr_data: schemas.HRDeploymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add HR deployment details to a request"""
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    existing = db.query(HRDeployment).filter(HRDeployment.request_id == request_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="HR details already exist for this request")
    
    hr_deployment = HRDeployment(
        **hr_data.model_dump(),
        request_id=request_id
    )
    
    db.add(hr_deployment)
    db.commit()
    db.refresh(hr_deployment)
    return hr_deployment


@router.get("/{request_id}/hr-details", response_model=schemas.HRDeploymentRead)
async def get_hr_details(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get HR deployment details for a request"""
    hr_deployment = db.query(HRDeployment).filter(HRDeployment.request_id == request_id).first()
    if not hr_deployment:
        raise HTTPException(status_code=404, detail="HR details not found")
    
    return hr_deployment


@router.patch("/{request_id}/hr-details", response_model=schemas.HRDeploymentRead)
async def update_hr_details(
    request_id: int,
    hr_data: schemas.HRDeploymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update HR deployment details"""
    hr_deployment = db.query(HRDeployment).filter(HRDeployment.request_id == request_id).first()
    if not hr_deployment:
        raise HTTPException(status_code=404, detail="HR details not found")
    
    update_data = hr_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hr_deployment, field, value)
    
    db.commit()
    db.refresh(hr_deployment)
    return hr_deployment


# ============================================================================
# FINANCE TRANSACTION ENDPOINTS
# ============================================================================

@router.post("/{request_id}/finance-details", response_model=schemas.FinanceTransactionRead)
async def create_finance_details(
    request_id: int,
    finance_data: schemas.FinanceTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add finance transaction details to a request"""
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    existing = db.query(FinanceTransaction).filter(FinanceTransaction.request_id == request_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Finance details already exist for this request")
    
    finance_transaction = FinanceTransaction(
        **finance_data.model_dump(),
        request_id=request_id
    )
    
    db.add(finance_transaction)
    db.commit()
    db.refresh(finance_transaction)
    return finance_transaction


@router.get("/{request_id}/finance-details", response_model=schemas.FinanceTransactionRead)
async def get_finance_details(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get finance transaction details for a request"""
    finance_transaction = db.query(FinanceTransaction).filter(FinanceTransaction.request_id == request_id).first()
    if not finance_transaction:
        raise HTTPException(status_code=404, detail="Finance details not found")
    
    return finance_transaction


@router.patch("/{request_id}/finance-details", response_model=schemas.FinanceTransactionRead)
async def update_finance_details(
    request_id: int,
    finance_data: schemas.FinanceTransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update finance transaction details"""
    finance_transaction = db.query(FinanceTransaction).filter(FinanceTransaction.request_id == request_id).first()
    if not finance_transaction:
        raise HTTPException(status_code=404, detail="Finance details not found")
    
    update_data = finance_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(finance_transaction, field, value)
    
    db.commit()
    db.refresh(finance_transaction)
    return finance_transaction


# ============================================================================
# ICT TICKET ENDPOINTS
# ============================================================================

@router.post("/{request_id}/ict-details", response_model=schemas.ICTTicketRead)
async def create_ict_details(
    request_id: int,
    ict_data: schemas.ICTTicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add ICT ticket details to a request"""
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    existing = db.query(ICTTicket).filter(ICTTicket.request_id == request_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="ICT details already exist for this request")
    
    ict_ticket = ICTTicket(
        **ict_data.model_dump(),
        request_id=request_id
    )
    
    db.add(ict_ticket)
    db.commit()
    db.refresh(ict_ticket)
    return ict_ticket


@router.get("/{request_id}/ict-details", response_model=schemas.ICTTicketRead)
async def get_ict_details(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get ICT ticket details for a request"""
    ict_ticket = db.query(ICTTicket).filter(ICTTicket.request_id == request_id).first()
    if not ict_ticket:
        raise HTTPException(status_code=404, detail="ICT details not found")
    
    return ict_ticket


@router.patch("/{request_id}/ict-details", response_model=schemas.ICTTicketRead)
async def update_ict_details(
    request_id: int,
    ict_data: schemas.ICTTicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update ICT ticket details"""
    ict_ticket = db.query(ICTTicket).filter(ICTTicket.request_id == request_id).first()
    if not ict_ticket:
        raise HTTPException(status_code=404, detail="ICT details not found")
    
    update_data = ict_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ict_ticket, field, value)
    
    db.commit()
    db.refresh(ict_ticket)
    return ict_ticket


# ============================================================================
# LOGISTICS REQUEST ENDPOINTS
# ============================================================================

@router.post("/{request_id}/logistics-details", response_model=schemas.LogisticsRequestRead)
async def create_logistics_details(
    request_id: int,
    logistics_data: schemas.LogisticsRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add logistics details to a request"""
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    existing = db.query(LogisticsRequest).filter(LogisticsRequest.request_id == request_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Logistics details already exist for this request")
    
    logistics_request = LogisticsRequest(
        **logistics_data.model_dump(),
        request_id=request_id
    )
    
    db.add(logistics_request)
    db.commit()
    db.refresh(logistics_request)
    return logistics_request


@router.get("/{request_id}/logistics-details", response_model=schemas.LogisticsRequestRead)
async def get_logistics_details(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get logistics details for a request"""
    logistics_request = db.query(LogisticsRequest).filter(LogisticsRequest.request_id == request_id).first()
    if not logistics_request:
        raise HTTPException(status_code=404, detail="Logistics details not found")
    
    return logistics_request


@router.patch("/{request_id}/logistics-details", response_model=schemas.LogisticsRequestRead)
async def update_logistics_details(
    request_id: int,
    logistics_data: schemas.LogisticsRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update logistics details"""
    logistics_request = db.query(LogisticsRequest).filter(LogisticsRequest.request_id == request_id).first()
    if not logistics_request:
        raise HTTPException(status_code=404, detail="Logistics details not found")
    
    update_data = logistics_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(logistics_request, field, value)
    
    db.commit()
    db.refresh(logistics_request)
    return logistics_request
