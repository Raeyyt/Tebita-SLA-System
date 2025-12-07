from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from decimal import Decimal

from ..database import get_db
from ..auth import get_current_active_user
from ..models import Request, User, Division, Department, RequestStatus, KPIMetric, Scorecard, ScoreRating
from .. import schemas
from ..services.kpi_calculator import calculate_kpi_metrics  # NEW: Import KPI service

router = APIRouter(prefix="/kpis", tags=["kpis"])


@router.get("/realtime")
async def get_realtime_kpis(
    department_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get real-time KPI metrics for the dashboard.
    Optionally filter by department_id (if user has access).
    """
    # If user is not admin, restrict to their department
    if current_user.role != "ADMIN":
        department_id = current_user.department_id
        
    return calculate_kpi_metrics(db, department_id)


@router.get("/metrics")
async def get_kpi_metrics(
    period: str = "month",  # day, week, month, quarter
    division_id: int = None,
    department_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get KPI metrics for specified period and filters"""
    
    # Calculate period start
    now = datetime.utcnow()
    if period == "day":
        start = now - timedelta(days=1)
    elif period == "week":
        start = now - timedelta(weeks=1)
    elif period == "quarter":
        start = now - timedelta(days=90)
    else:  # month
        start = now - timedelta(days=30)
    
    # Query metrics
    query = db.query(KPIMetric).filter(KPIMetric.recorded_at >= start)
    
    if division_id:
        query = query.filter(KPIMetric.division_id == division_id)
    if department_id:
        query = query.filter(KPIMetric.department_id == department_id)
    
    metrics = query.all()
    
    # If no stored metrics, calculate real-time
    if not metrics:
        calculated_metrics = calculate_realtime_kpis(db, start, now, division_id, department_id)
        return calculated_metrics
    
    return metrics


@router.get("/scorecard")
async def get_scorecard(
    period: str = "month",
    division_id: int = None,
    department_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate scorecard for specified period"""
    
    # Calculate period
    now = datetime.utcnow()
    if period == "day":
        start = now - timedelta(days=1)
    elif period == "week":
        start = now - timedelta(weeks=1)
    elif period == "quarter":
        start = now - timedelta(days=90)
    else:  # month
        start = now - timedelta(days=30)
    
    # Check for existing scorecard
    query = db.query(Scorecard).filter(
        Scorecard.period_start >= start,
        Scorecard.period_end <= now
    )
    
    if division_id:
        query = query.filter(Scorecard.division_id == division_id)
    if department_id:
        query = query.filter(Scorecard.department_id == department_id)
    
    existing = query.first()
    if existing:
        return existing
    
    # Calculate new scorecard
    scorecard = calculate_scorecard(db, start, now, division_id, department_id)
    
    # Save scorecard
    new_scorecard = Scorecard(
        period_start=start,
        period_end=now,
        division_id=division_id,
        department_id=department_id,
        service_efficiency_score=scorecard['service_efficiency'],
        compliance_score=scorecard['compliance'],
        cost_optimization_score=scorecard['cost_optimization'],
        satisfaction_score=scorecard['satisfaction'],
        total_score=scorecard['total'],
        rating=scorecard['rating'],
        created_by_user_id=current_user.id
    )
    
    db.add(new_scorecard)
    db.commit()
    db.refresh(new_scorecard)
    
    return new_scorecard


@router.get("/dashboard")
async def get_kpi_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get KPI dashboard overview"""
    
    now = datetime.utcnow()
    month_start = now - timedelta(days=30)
    
    # Get all requests for the month
    requests = db.query(Request).filter(Request.created_at >= month_start).all()
    
    if not requests:
        return {
            "total_requests": 0,
            "avg_response_time": 0,
            "avg_completion_time": 0,
            "sla_compliance_rate": 0,
            "satisfaction_avg": 0,
        }
    
    # Calculate metrics
    total = len(requests)
    response_times = []
    completion_times = []
    within_sla = 0
    
    for req in requests:
        if req.status == RequestStatus.COMPLETED:
            if req.created_at and req.completed_at:
                completion_time = (req.completed_at - req.created_at).total_seconds() / 3600
                completion_times.append(completion_time)
                
                if req.sla_completion_time_hours and completion_time <= req.sla_completion_time_hours:
                    within_sla += 1
    
    avg_completion = sum(completion_times) / len(completion_times) if completion_times else 0
    sla_rate = (within_sla / len(completion_times) * 100) if completion_times else 0
    
    return {
        "total_requests": total,
        "avg_response_time": 0,  # Placeholder
        "avg_completion_time": round(avg_completion, 2),
        "sla_compliance_rate": round(sla_rate, 2),
        "satisfaction_avg": 0,  # Placeholder - would calculate from satisfaction table
    }


def calculate_realtime_kpis(db: Session, start: datetime, end: datetime, division_id: int = None, department_id: int = None):
    """Calculate KPIs in real-time"""
    
    query = db.query(Request).filter(Request.created_at >= start, Request.created_at <= end)
    
    if division_id:
        query = query.filter(Request.requester_division_id == division_id)
    if department_id:
        query = query.filter(Request.requester_department_id == department_id)
    
    requests = query.all()
    
    # Calculate various KPIs
    total_requests = len(requests)
    completed = len([r for r in requests if r.status == RequestStatus.COMPLETED])
    pending = len([r for r in requests if r.status == RequestStatus.PENDING])
    
    completion_rate = (completed / total_requests * 100) if total_requests > 0 else 0
    
    return {
        "total_requests": total_requests,
        "completed_requests": completed,
        "pending_requests": pending,
        "completion_rate": round(completion_rate, 2),
    }


def calculate_scorecard(db: Session, start: datetime, end: datetime, division_id: int = None, department_id: int = None):
    """Calculate 4-dimension scorecard"""
    
    query = db.query(Request).filter(Request.created_at >= start, Request.created_at <= end)
    
    if division_id:
        query = query.filter(Request.requester_division_id == division_id)
    if department_id:
        query = query.filter(Request.requester_department_id == department_id)
    
    requests = query.all()
    
    if not requests:
        return {
            'service_efficiency': Decimal('0'),
            'compliance': Decimal('0'),
            'cost_optimization': Decimal('0'),
            'satisfaction': Decimal('0'),
            'total': Decimal('0'),
            'rating': ScoreRating.UNSATISFACTORY,
        }
    
    # 1. Service Efficiency (25%) - based on completion time
    completed = [r for r in requests if r.status == RequestStatus.COMPLETED]
    if completed:
        avg_time = sum([(r.completed_at - r.created_at).total_seconds() / 3600 for r in completed if r.completed_at]) / len(completed)
        # Lower time = higher score (normalize to 0-100)
        service_efficiency = min(100, max(0, 100 - (avg_time / 72 * 100)))  # 72 hours = baseline
    else:
        service_efficiency = 0
    
    # 2. SLA Compliance (30%)
    within_sla = 0
    for req in completed:
        if req.completed_at and req.created_at and req.sla_completion_time_hours:
            time_taken = (req.completed_at - req.created_at).total_seconds() / 3600
            if time_taken <= req.sla_completion_time_hours:
                within_sla += 1
    
    compliance = (within_sla / len(completed) * 100) if completed else 0
    
    # 3. Cost Optimization (20%) - placeholder
    cost_optimization = 75  # Default score
    
    # 4. Customer Satisfaction (25%) - placeholder
    satisfaction = 80  # Default score
    
    # Weight and calculate total
    total = (
        Decimal(str(service_efficiency)) * Decimal('0.25') +
        Decimal(str(compliance)) * Decimal('0.30') +
        Decimal(str(cost_optimization)) * Decimal('0.20') +
        Decimal(str(satisfaction)) * Decimal('0.25')
    )
    
    # Determine rating
    if total >= 90:
        rating = ScoreRating.OUTSTANDING
    elif total >= 80:
        rating = ScoreRating.VERY_GOOD
    elif total >= 70:
        rating = ScoreRating.GOOD
    elif total >= 60:
        rating = ScoreRating.NEEDS_IMPROVEMENT
    else:
        rating = ScoreRating.UNSATISFACTORY
    
    return {
        'service_efficiency': Decimal(str(round(service_efficiency, 2))),
        'compliance': Decimal(str(round(compliance, 2))),
        'cost_optimization': Decimal(str(cost_optimization)),
        'satisfaction': Decimal(str(satisfaction)),
        'total': total,
        'rating': rating,
    }
