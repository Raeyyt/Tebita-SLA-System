from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case, and_, or_
from typing import List
from datetime import datetime, timedelta
from decimal import Decimal

from ..database import get_db
from ..auth import get_current_active_user
from ..models import Request, User, Division, Department, RequestStatus, KPIMetric, Scorecard, ScoreRating, UserRole, Priority
from .. import schemas
from ..services.kpi_calculator import calculate_kpi_metrics, calculate_overdue_requests, calculate_customer_satisfaction_score  # NEW: Import KPI service
from ..services.access_control import apply_role_based_filtering

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
    # Determine scope based on role
    division_id_filter = None
    department_id_filter = None
    
    if current_user.role == UserRole.DIVISION_MANAGER:
        division_id_filter = current_user.division_id
    elif current_user.role == UserRole.DEPARTMENT_HEAD:
        department_id_filter = current_user.department_id
    elif current_user.role != UserRole.ADMIN:
        # Regular staff shouldn't really see this, but default to their dept
        department_id_filter = current_user.department_id
        
    # If specific department requested (and allowed), use it
    if department_id:
        # TODO: Validate user has access to this department
        department_id_filter = department_id

    metrics = calculate_kpi_metrics(db, department_id_filter, division_id_filter)
    overdue_count = calculate_overdue_requests(db, department_id_filter, division_id_filter)
    
    return {
        **metrics,
        "overdue_requests": overdue_count
    }


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
    
    # Enforce role-based filtering for real-time calculations
    if current_user.role == UserRole.DIVISION_MANAGER:
        division_id = current_user.division_id
        department_id = None  # Division managers see all depts in their division
    elif current_user.role == UserRole.DEPARTMENT_HEAD:
        department_id = current_user.department_id
        # division_id might be passed, but department_id is the stricter constraint
    elif current_user.role != UserRole.ADMIN:
        # Regular staff -> default to their department
        department_id = current_user.department_id
    
    # Query metrics
    query = db.query(KPIMetric).filter(KPIMetric.recorded_at >= start)
    query = apply_role_based_filtering(query, current_user, model=KPIMetric)
    
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
        
    # Enforce role-based filtering
    if current_user.role == UserRole.DIVISION_MANAGER:
        division_id = current_user.division_id
        department_id = None
    elif current_user.role == UserRole.DEPARTMENT_HEAD:
        department_id = current_user.department_id
    elif current_user.role != UserRole.ADMIN:
        department_id = current_user.department_id
    
    # Check for existing scorecard
    query = db.query(Scorecard).filter(
        Scorecard.period_start >= start,
        Scorecard.period_end <= now
    )
    query = apply_role_based_filtering(query, current_user, model=Scorecard)
    
    if division_id:
        query = query.filter(Scorecard.division_id == division_id)
    if department_id:
        query = query.filter(Scorecard.department_id == department_id)
    
    existing = query.first()
    if existing:
        # FORCE REFRESH: Delete existing scorecard to ensure new SLA logic is applied
        # In production, we might want a smarter cache invalidation, but for now this ensures correctness.
        db.delete(existing)
        db.commit()
        # return existing  <-- Commented out to force recalculation
    
    # Calculate new scorecard
    try:
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
    except Exception as e:
        db.rollback()
        # Return the calculated scorecard even if saving fails (fallback)
        # We construct a mock object that matches the schema
        print(f"Error saving scorecard: {e}")
        return Scorecard(
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


@router.get("/dashboard")
async def get_kpi_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get KPI dashboard overview using SQL aggregations"""
    from sqlalchemy import case, extract, and_
    
    now = datetime.utcnow()
    month_start = now - timedelta(days=30)
    
    # Base query with role-based filtering
    base_query = db.query(Request).filter(Request.created_at >= month_start)
    base_query = apply_role_based_filtering(base_query, current_user)
    
    # 1. Base Stats and Priority Breakdown in one query
    stats = db.query(
        func.count(Request.id).label("total"),
        func.count(case((Request.priority == Priority.HIGH, 1))).label("high"),
        func.count(case((Request.priority == Priority.MEDIUM, 1))).label("medium"),
        func.count(case((Request.priority == Priority.LOW, 1))).label("low"),
        func.count(case((Request.status == RequestStatus.REJECTED, 1))).label("rejected")
    ).filter(base_query.whereclause).one()
    
    if stats.total == 0:
        return {
            "total_requests": 0,
            "avg_response_time": 0,
            "avg_completion_time": 0,
            "sla_compliance_rate": 0,
            "satisfaction_avg": 0,
            "rejection_rate": 0,
            "priority_breakdown": {"high": 0, "medium": 0, "low": 0}
        }
    
    # 2. SLA Compliance (SQL-based)
    # A request is compliant ONLY if both response and resolution SLAs are met
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
                Request.status == RequestStatus.COMPLETED,
                # Response overdue (if not yet acknowledged)
                and_(
                    Request.acknowledged_at.is_(None),
                    now_epoch > created_epoch + resp_target
                ),
                # Resolution overdue
                now_epoch > created_epoch + res_target
            ), 1
        ))).label("evaluated"),
        func.avg(
            case((
                Request.status == RequestStatus.COMPLETED,
                extract('epoch', Request.actual_completion_time) - created_epoch
            ))
        ).label("avg_completion_seconds")
    ).filter(base_query.whereclause).one()
    
    sla_rate = (sla_stats.compliant / sla_stats.evaluated * 100) if sla_stats.evaluated > 0 else 100
    avg_completion = (sla_stats.avg_completion_seconds / 3600) if sla_stats.avg_completion_seconds else 0
    
    # 3. Satisfaction Score
    satisfaction_score = calculate_customer_satisfaction_score(db, start_date=month_start, end_date=now)
    
    return {
        "total_requests": stats.total,
        "avg_response_time": 0,  # Placeholder
        "avg_completion_time": round(avg_completion, 2),
        "sla_compliance_rate": round(sla_rate, 2),
        "satisfaction_avg": round(satisfaction_score, 1),
        "rejection_rate": round((stats.rejected / stats.total * 100), 1),
        "priority_breakdown": {
            "high": stats.high,
            "medium": stats.medium,
            "low": stats.low
        }
    }



def calculate_realtime_kpis(db: Session, start: datetime, end: datetime, division_id: int = None, department_id: int = None):
    """Calculate KPIs in real-time"""
    
    query = db.query(Request).filter(Request.created_at >= start, Request.created_at <= end)
    
    if division_id:
        query = query.filter(Request.assigned_division_id == division_id)
    if department_id:
        query = query.filter(Request.assigned_department_id == department_id)
    
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
        query = query.filter(Request.assigned_division_id == division_id)
    if department_id:
        query = query.filter(Request.assigned_department_id == department_id)
    
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
            # Check both Response and Resolution
            resp_compliant = True
            if req.actual_response_time:
                resp_time = (req.actual_response_time - req.created_at).total_seconds() / 3600
                resp_compliant = resp_time <= (req.sla_response_time_hours or 2)
            
            res_time = (req.completed_at - req.created_at).total_seconds() / 3600
            res_compliant = res_time <= req.sla_completion_time_hours
            
            if resp_compliant and res_compliant:
                within_sla += 1
    
    # Add active overdue requests to calculation
    active_overdue = 0
    now = datetime.utcnow()
    for req in requests:
        if req.status in [RequestStatus.PENDING, RequestStatus.IN_PROGRESS]:
            # Response overdue?
            if not req.acknowledged_at:
                resp_deadline = req.created_at + timedelta(hours=req.sla_response_time_hours or 2)
                if now > resp_deadline:
                    active_overdue += 1
                    continue # Already overdue
            
            # Resolution overdue?
            if req.created_at and req.sla_completion_time_hours:
                res_deadline = req.created_at + timedelta(hours=req.sla_completion_time_hours)
                if now > res_deadline:
                    active_overdue += 1
    
    total_evaluated = len(completed) + active_overdue
    compliance = (within_sla / total_evaluated * 100) if total_evaluated > 0 else 100
    
    # 3. Cost Optimization (20%) - placeholder
    # Future: Calculate based on budget variance or resource utilization
    cost_optimization = 75  # Default demo score
    
    # 4. Customer Satisfaction (25%)
    # Use the shared calculator service
    raw_satisfaction = calculate_customer_satisfaction_score(db, division_id, start_date=start, end_date=now)
    
    # Convert 1-5 scale to 0-100 for scorecard
    # 1=0, 2=25, 3=50, 4=75, 5=100
    if raw_satisfaction > 0:
        satisfaction = (raw_satisfaction - 1) * 25
    else:
        satisfaction = 100 # Default if no ratings (assume good)
    
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
