"""
KPI Calculator Module for M&E System
Calculates all KPIs as defined in organizational requirements document.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import (
    Request, RequestStatus, Priority, ResourceType,
    FleetRequest, HRDeployment, FinanceTransaction, ICTTicket, LogisticsRequest,
    Division, Department
)


# ============================================================================
# GENERAL INTEGRATION KPIs
# ============================================================================

def calculate_sla_compliance_rate(
    db: Session,
    division_id: Optional[int] = None,
    department_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """
    Calculate SLA Compliance Rate (%)
    Formula: # of requests completed within SLA ÷ total requests × 100
    """
    query = db.query(Request).filter(Request.status == RequestStatus.COMPLETED)
    
    if division_id:
        query = query.filter(Request.requester_division_id == division_id)
    if department_id:
        query = query.filter(Request.requester_department_id == department_id)
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    total_requests = query.count()
    if total_requests == 0:
        return 0.0
    
    # Count requests where actual_completion_time <= sla_completion_deadline
    on_time_requests = query.filter(
        Request.actual_completion_time <= Request.sla_completion_deadline
    ).count()
    
    return round((on_time_requests / total_requests) * 100, 2)


def calculate_service_request_fulfillment_rate(
    db: Session,
    division_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Request fulfillment rate (completed vs total)"""
    query = db.query(Request)
    
    if division_id:
        query = query.filter(Request.requester_division_id == division_id)
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    total = query.count()
    if total == 0:
        return 0.0
    
    completed = query.filter(Request.status == RequestStatus.COMPLETED).count()
    return round((completed / total) * 100, 2)


def calculate_customer_satisfaction_score(
    db: Session,
    division_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Average customer satisfaction score (1-5 scale)"""
    query = db.query(Request).filter(
        Request.satisfaction_rating.isnot(None)
    )
    
    if division_id:
        query = query.filter(Request.requester_division_id == division_id)
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    avg_score = query.with_entities(
        func.avg(Request.satisfaction_rating)
    ).scalar()
    
    return round(float(avg_score or 0), 2)


# ============================================================================
# FLEET KPIs
# ============================================================================

def calculate_vehicle_utilization_rate(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    fleet_size: int = 10  # Total vehicles available
) -> float:
    """
    Vehicle Utilization Rate (%)
    Formula: Vehicle-days used / Total vehicle-days available × 100
    """
    days = (end_date - start_date).days or 1
    total_vehicle_days = fleet_size * days
    
    # Count completed trips
    used_vehicle_days = db.query(FleetRequest).join(Request).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date,
        FleetRequest.trip_completed == True
    ).count()
    
    return round((used_vehicle_days / total_vehicle_days) * 100, 2)


def calculate_trip_completion_rate(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Trip Completion Rate (%)"""
    query = db.query(FleetRequest).join(Request)
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    total = query.count()
    if total == 0:
        return 0.0
    
    completed = query.filter(FleetRequest.trip_completed == True).count()
    return round((completed / total) * 100, 2)


def calculate_average_turnaround_time(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Average Turnaround Time in hours"""
    query = db.query(FleetRequest).join(Request).filter(
        FleetRequest.dispatch_time.isnot(None),
        FleetRequest.return_time.isnot(None)
    )
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    fleet_requests = query.all()
    if not fleet_requests:
        return 0.0
    
    total_hours = sum(
        (fr.return_time - fr.dispatch_time).total_seconds() / 3600
        for fr in fleet_requests
    )
    
    return round(total_hours / len(fleet_requests), 2)


def calculate_fuel_efficiency(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Fuel Efficiency (km/liter)"""
    query = db.query(FleetRequest).join(Request).filter(
        FleetRequest.fuel_used.isnot(None),
        FleetRequest.km_traveled.isnot(None),
        FleetRequest.fuel_used > 0
    )
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    total_km = query.with_entities(func.sum(FleetRequest.km_traveled)).scalar() or 0
    total_fuel = query.with_entities(func.sum(FleetRequest.fuel_used)).scalar() or 0
    
    if total_fuel == 0:
        return 0.0
    
    return round(total_km / total_fuel, 2)


def calculate_breakdown_frequency(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> int:
    """Breakdown frequency (count per month)"""
    query = db.query(FleetRequest).join(Request).filter(
        FleetRequest.breakdown_occurred == True
    )
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    return query.count()


# ============================================================================
# HR KPIs
# ============================================================================

def calculate_staff_deployment_filling_rate(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Staff Deployment Filling Rate (%)"""
    query = db.query(HRDeployment).join(Request)
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    total = query.count()
    if total == 0:
        return 0.0
    
    filled = query.filter(HRDeployment.deployment_filled == True).count()
    return round((filled / total) * 100, 2)


def calculate_deployment_average_response_time(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Average response time to deployment requests (hours)"""
    query = db.query(Request).join(HRDeployment).filter(
        Request.actual_response_time.isnot(None)
    )
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    requests = query.all()
    if not requests:
        return 0.0
    
    total_hours = sum(
        (r.actual_response_time - r.created_at).total_seconds() / 3600
        for r in requests
    )
    
    return round(total_hours / len(requests), 2)


def calculate_overtime_usage_rate(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Overtime Usage Rate (% of total deployment hours)"""
    query = db.query(HRDeployment).join(Request).filter(
        HRDeployment.deployment_duration_days.isnot(None)
    )
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    total_hours = query.with_entities(
        func.sum(HRDeployment.deployment_duration_days * 8)  # 8 hours per day
    ).scalar() or 0
    
    overtime_hours = query.with_entities(
        func.sum(HRDeployment.overtime_hours)
    ).scalar() or 0
    
    if total_hours == 0:
        return 0.0
    
    return round((overtime_hours / total_hours) * 100, 2)


# ============================================================================
# FINANCE KPIs
# ============================================================================

def calculate_payment_processing_turnaround_time(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Average Payment Processing Turnaround Time (days)"""
    query = db.query(FinanceTransaction).join(Request).filter(
        FinanceTransaction.date_received.isnot(None),
        FinanceTransaction.date_processed.isnot(None)
    )
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    transactions = query.all()
    if not transactions:
        return 0.0
    
    total_days = sum(
        (t.date_processed - t.date_received).days
        for t in transactions
    )
    
    return round(total_days / len(transactions), 2)


def calculate_payment_accuracy_rate(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Payment Accuracy Rate (%)"""
    query = db.query(FinanceTransaction).join(Request)
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    total = query.count()
    if total == 0:
        return 0.0
    
    accurate = query.filter(FinanceTransaction.payment_accuracy == True).count()
    return round((accurate / total) * 100, 2)


def calculate_document_completeness_rate(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Average Document Completeness Score (%)"""
    query = db.query(FinanceTransaction).join(Request).filter(
        FinanceTransaction.document_completeness_score.isnot(None)
    )
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    avg_score = query.with_entities(
        func.avg(FinanceTransaction.document_completeness_score)
    ).scalar()
    
    return round(float(avg_score or 0), 2)


# ============================================================================
# ICT KPIs
# ============================================================================

def calculate_ticket_resolution_rate(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """ICT Ticket Resolution Rate (%)"""
    query = db.query(ICTTicket).join(Request)
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    total = query.count()
    if total == 0:
        return 0.0
    
    resolved = query.join(Request).filter(
        Request.status == RequestStatus.COMPLETED
    ).count()
    
    return round((resolved / total) * 100, 2)


def calculate_average_ict_response_time(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Average ICT Response Time (hours)"""
    query = db.query(Request).join(ICTTicket).filter(
        Request.actual_response_time.isnot(None)
    )
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    requests = query.all()
    if not requests:
        return 0.0
    
    total_hours = sum(
        (r.actual_response_time - r.created_at).total_seconds() / 3600
        for r in requests
    )
    
    return round(total_hours / len(requests), 2)


def calculate_reopened_tickets_rate(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Re-opened Tickets Rate (%)"""
    query = db.query(ICTTicket).join(Request)
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    total = query.count()
    if total == 0:
        return 0.0
    
    reopened = query.filter(ICTTicket.reopened == True).count()
    return round((reopened / total) * 100, 2)


# ============================================================================
# LOGISTICS KPIs
# ============================================================================

def calculate_on_time_delivery_rate(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """On-Time Delivery Rate (%)"""
    query = db.query(LogisticsRequest).join(Request).filter(
        Request.status == RequestStatus.COMPLETED,
        Request.actual_completion_time.isnot(None),
        Request.sla_completion_deadline.isnot(None)
    )
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    requests = query.all()
    if not requests:
        return 0.0
    
    on_time = sum(
        1 for lr in requests
        if lr.request.actual_completion_time <= lr.request.sla_completion_deadline
    )
    
    return round((on_time / len(requests)) * 100, 2)


def calculate_stock_fulfillment_rate(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Stock Fulfillment Rate (%)"""
    query = db.query(LogisticsRequest).join(Request).filter(
        LogisticsRequest.quantity_requested.isnot(None),
        LogisticsRequest.quantity_delivered.isnot(None),
        LogisticsRequest.quantity_requested > 0
    )
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    total_requested = query.with_entities(
        func.sum(LogisticsRequest.quantity_requested)
    ).scalar() or 0
    
    total_delivered = query.with_entities(
        func.sum(LogisticsRequest.quantity_delivered)
    ).scalar() or 0
    
    if total_requested == 0:
        return 0.0
    
    return round((total_delivered / total_requested) * 100, 2)


def calculate_requisition_accuracy(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """Requisition Accuracy (%)"""
    query = db.query(LogisticsRequest).join(Request)
    
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    total = query.count()
    if total == 0:
        return 0.0
    
    accurate = query.filter(LogisticsRequest.requisition_accurate == True).count()
    return round((accurate / total) * 100, 2)
