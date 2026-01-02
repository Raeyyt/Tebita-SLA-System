from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from app.models import (
    Request, RequestStatus, Priority, ResourceType, ActivityType,
    FleetRequest, HRDeployment, FinanceTransaction, ICTTicket, LogisticsRequest, 
    CustomerSatisfaction, Division, Department
)
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple

def calculate_kpi_metrics(db: Session, department_id: int = None, division_id: int = None):
    """
    Calculates real-time KPI metrics for a given department/division (or all if None).
    """
    query = db.query(Request)
    if department_id:
        query = query.filter(Request.assigned_department_id == department_id)
    if division_id:
        query = query.filter(Request.assigned_division_id == division_id)
        
    # Base stats
    total_requests = query.count()
    if total_requests == 0:
        return {
            "total_requests": 0,
            "sla_compliance_rate": 100,
            "avg_resolution_time_hours": 0,
            "pending_requests": 0,
            "rejection_rate": 0,
            "priority_breakdown": {
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }

    # 1. SLA Resolution Compliance (includes active overdue requests)
    now = datetime.utcnow()
    
    # Get all completed requests with SLA time defined
    completed_requests = query.filter(
        Request.status == RequestStatus.COMPLETED,
        Request.sla_completion_time_hours.isnot(None),
        Request.created_at.isnot(None),
        Request.actual_completion_time.isnot(None)
    ).all()
    
    compliant_completed = 0
    non_compliant_completed = 0
    
    for req in completed_requests:
        deadline = req.created_at + timedelta(hours=req.sla_completion_time_hours)
        if req.actual_completion_time <= deadline:
            compliant_completed += 1
        else:
            non_compliant_completed += 1
    
    # Get active overdue requests
    active_requests = query.filter(
        Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS]),
        Request.sla_completion_time_hours.isnot(None),
        Request.created_at.isnot(None)
    ).all()
    
    overdue_active = 0
    for req in active_requests:
        deadline = req.created_at + timedelta(hours=req.sla_completion_time_hours)
        if now > deadline:
            overdue_active += 1
    
    # Total requests to evaluate
    total_evaluated = compliant_completed + non_compliant_completed + overdue_active
    compliance_rate = (compliant_completed / total_evaluated * 100) if total_evaluated > 0 else 100

    # 2. Average Resolution Time
    avg_time_query = db.query(
        func.avg(extract('epoch', Request.actual_completion_time) - extract('epoch', Request.created_at))
    ).filter(Request.status == RequestStatus.COMPLETED)
    
    if department_id:
        avg_time_query = avg_time_query.filter(Request.assigned_department_id == department_id)
    if division_id:
        avg_time_query = avg_time_query.filter(Request.assigned_division_id == division_id)
        
    avg_seconds = avg_time_query.scalar() or 0
    avg_hours = round(avg_seconds / 3600, 1)

    # 3. Pending Requests
    pending_count = query.filter(
        Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS, RequestStatus.APPROVAL_PENDING])
    ).count()

    # 4. Priority Distribution
    high_priority = query.filter(Request.priority == Priority.HIGH).count()
    medium_priority = query.filter(Request.priority == Priority.MEDIUM).count()
    low_priority = query.filter(Request.priority == Priority.LOW).count()

    # 5. Rejection Rate
    rejected_count = query.filter(Request.status == RequestStatus.REJECTED).count()
    rejection_rate = (rejected_count / total_requests * 100) if total_requests > 0 else 0

    return {
        "total_requests": total_requests,
        "sla_compliance_rate": round(compliance_rate, 1),
        "avg_resolution_time_hours": avg_hours,
        "pending_requests": pending_count,
        "rejection_rate": round(rejection_rate, 1),
        "priority_breakdown": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority
        }
    }

# ============================================================================
# GENERAL KPIs (Date Range)
# ============================================================================

def calculate_sla_compliance_rate(db: Session, division_id: int = None, department_id: int = None, start_date: datetime = None, end_date: datetime = None):
    query = db.query(Request).filter(Request.status == RequestStatus.COMPLETED)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    if division_id: query = query.filter(Request.assigned_division_id == division_id)
    if department_id: query = query.filter(Request.assigned_department_id == department_id)
    
    total = query.count()
    if total == 0: return 100.0
    
    compliant = query.filter(Request.actual_completion_time <= Request.sla_completion_deadline).count()
    return (compliant / total) * 100.0

def calculate_service_request_fulfillment_rate(db: Session, division_id: int = None, start_date: datetime = None, end_date: datetime = None):
    query = db.query(Request)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    if division_id: query = query.filter(Request.assigned_division_id == division_id)
    
    total = query.count()
    if total == 0: return 100.0
    
    fulfilled = query.filter(Request.status == RequestStatus.COMPLETED).count()
    return (fulfilled / total) * 100.0

def calculate_customer_satisfaction_score(db: Session, division_id: int = None, start_date: datetime = None, end_date: datetime = None):
    query = db.query(func.avg(CustomerSatisfaction.overall_score)).join(Request)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    if division_id: query = query.filter(Request.assigned_division_id == division_id)
    
    avg_score = query.scalar()
    return float(avg_score) if avg_score else 0.0

# ============================================================================
# FLEET KPIs
# ============================================================================

def calculate_vehicle_utilization_rate(db: Session, start_date: datetime, end_date: datetime, fleet_size: int):
    query = db.query(func.count(func.distinct(FleetRequest.vehicle_assigned))).join(Request)
    query = query.filter(Request.created_at >= start_date, Request.created_at <= end_date)
    
    vehicles_used = query.scalar() or 0
    if fleet_size == 0: return 0.0
    return (vehicles_used / fleet_size) * 100.0

def calculate_trip_completion_rate(db: Session, start_date: datetime, end_date: datetime):
    query = db.query(FleetRequest).join(Request)
    query = query.filter(Request.created_at >= start_date, Request.created_at <= end_date)
    
    total = query.count()
    if total == 0: return 100.0
    
    completed = query.filter(FleetRequest.trip_completed == True).count()
    return (completed / total) * 100.0

def calculate_average_turnaround_time(db: Session, start_date: datetime, end_date: datetime):
    return 0.0 # Placeholder

def calculate_fuel_efficiency(db: Session, start_date: datetime, end_date: datetime):
    query = db.query(
        func.sum(FleetRequest.km_traveled),
        func.sum(FleetRequest.fuel_used)
    ).join(Request).filter(Request.created_at >= start_date, Request.created_at <= end_date)
    
    km, fuel = query.first()
    if not fuel or fuel == 0: return 0.0
    return float(km) / float(fuel)

def calculate_breakdown_frequency(db: Session, start_date: datetime, end_date: datetime):
    query = db.query(FleetRequest).join(Request)
    query = query.filter(Request.created_at >= start_date, Request.created_at <= end_date)
    
    total_trips = query.count()
    if total_trips == 0: return 0.0
    
    breakdowns = query.filter(FleetRequest.breakdown_occurred == True).count()
    return (breakdowns / total_trips) * 100.0

# ============================================================================
# HR KPIs
# ============================================================================

def calculate_staff_deployment_filling_rate(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(HRDeployment).join(Request)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    total = query.count()
    if total == 0: return 0.0
    filled = query.filter(HRDeployment.deployment_filled == True).count()
    return round((filled / total) * 100, 2)

def calculate_deployment_average_response_time(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(Request).join(HRDeployment).filter(Request.actual_response_time.isnot(None))
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    requests = query.all()
    if not requests: return 0.0
    total_hours = sum((r.actual_response_time - r.created_at).total_seconds() / 3600 for r in requests)
    return round(total_hours / len(requests), 2)

def calculate_overtime_usage_rate(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(HRDeployment).join(Request)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    total_hours = query.with_entities(func.sum(HRDeployment.deployment_duration_days * 8)).scalar() or 0
    overtime_hours = query.with_entities(func.sum(HRDeployment.overtime_hours)).scalar() or 0
    if total_hours == 0: return 0.0
    return round((overtime_hours / total_hours) * 100, 2)

# ============================================================================
# FINANCE KPIs
# ============================================================================

def calculate_payment_processing_turnaround_time(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(FinanceTransaction).join(Request).filter(FinanceTransaction.date_received.isnot(None), FinanceTransaction.date_processed.isnot(None))
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    transactions = query.all()
    if not transactions: return 0.0
    total_days = sum((t.date_processed - t.date_received).days for t in transactions)
    return round(total_days / len(transactions), 2)

def calculate_payment_accuracy_rate(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(FinanceTransaction).join(Request)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    total = query.count()
    if total == 0: return 0.0
    accurate = query.filter(FinanceTransaction.payment_accuracy == True).count()
    return round((accurate / total) * 100, 2)

def calculate_document_completeness_rate(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(FinanceTransaction).join(Request).filter(FinanceTransaction.document_completeness_score.isnot(None))
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    avg_score = query.with_entities(func.avg(FinanceTransaction.document_completeness_score)).scalar()
    return round(float(avg_score or 0), 2)

# ============================================================================
# ICT KPIs
# ============================================================================

def calculate_ticket_resolution_rate(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(ICTTicket).join(Request)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    total = query.count()
    if total == 0: return 0.0
    resolved = query.filter(Request.status == RequestStatus.COMPLETED).count()
    return round((resolved / total) * 100, 2)

def calculate_average_ict_response_time(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(Request).join(ICTTicket).filter(Request.actual_response_time.isnot(None))
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    requests = query.all()
    if not requests: return 0.0
    total_hours = sum((r.actual_response_time - r.created_at).total_seconds() / 3600 for r in requests)
    return round(total_hours / len(requests), 2)

def calculate_reopened_tickets_rate(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(ICTTicket).join(Request)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    total = query.count()
    if total == 0: return 0.0
    reopened = query.filter(ICTTicket.reopened == True).count()
    return round((reopened / total) * 100, 2)

# ============================================================================
# LOGISTICS KPIs
# ============================================================================

def calculate_on_time_delivery_rate(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(LogisticsRequest).join(Request).filter(Request.status == RequestStatus.COMPLETED, Request.actual_completion_time.isnot(None), Request.sla_completion_deadline.isnot(None))
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    requests = query.all()
    if not requests: return 0.0
    on_time = sum(1 for lr in requests if lr.request.actual_completion_time <= lr.request.sla_completion_deadline)
    return round((on_time / len(requests)) * 100, 2)

def calculate_stock_fulfillment_rate(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(LogisticsRequest).join(Request).filter(LogisticsRequest.quantity_requested.isnot(None), LogisticsRequest.quantity_delivered.isnot(None), LogisticsRequest.quantity_requested > 0)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    total_requested = query.with_entities(func.sum(LogisticsRequest.quantity_requested)).scalar() or 0
    total_delivered = query.with_entities(func.sum(LogisticsRequest.quantity_delivered)).scalar() or 0
    if total_requested == 0: return 0.0
    return round((total_delivered / total_requested) * 100, 2)

def calculate_requisition_accuracy(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(LogisticsRequest).join(Request)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    total = query.count()
    if total == 0: return 0.0
    accurate = query.filter(LogisticsRequest.requisition_accurate == True).count()
    return round((accurate / total) * 100, 2)

# ============================================================================
# ADVANCED INTEGRATION & OPTIMIZATION KPIs
# ============================================================================

def calculate_integration_index(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(Request).filter(Request.requester_division_id != Request.assigned_division_id, Request.status == RequestStatus.COMPLETED)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    total = query.count()
    if total == 0: return 0.0
    on_time = query.filter(Request.actual_completion_time <= Request.sla_completion_deadline).count()
    return round((on_time / total) * 100, 2)

def calculate_resource_optimization_score(db: Session, division_id: int = None, start_date: datetime = None, end_date: datetime = None):
    sla_compliance = calculate_sla_compliance_rate(db, division_id, None, start_date, end_date)
    query = db.query(Request).filter(Request.status == RequestStatus.COMPLETED)
    if division_id: query = query.filter(Request.requester_division_id == division_id)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    total_estimated = query.with_entities(func.sum(Request.cost_estimate)).scalar() or 1
    total_actual = query.with_entities(func.sum(Request.actual_cost)).scalar() or 0
    cost_efficiency = max(0, (total_estimated - total_actual) / total_estimated * 100) if total_estimated > 0 else 0
    cost_efficiency = min(100, 100 - abs(cost_efficiency))
    fulfillment = calculate_service_request_fulfillment_rate(db, division_id, start_date, end_date)
    return round((sla_compliance + cost_efficiency + fulfillment) / 3, 2)

def calculate_cost_per_request(db: Session, division_id: int = None, resource_type: ResourceType = None, start_date: datetime = None, end_date: datetime = None):
    query = db.query(Request)
    if division_id: query = query.filter(Request.requester_division_id == division_id)
    if resource_type: query = query.filter(Request.resource_type == resource_type)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    total = query.count()
    if total == 0: return 0.0
    total_cost = query.with_entities(func.sum(Request.actual_cost)).scalar() or 0
    return round(float(total_cost) / total, 2)

def calculate_department_efficiency_score(db: Session, department_id: int, start_date: datetime = None, end_date: datetime = None):
    query = db.query(Request).filter(Request.assigned_department_id == department_id)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    total = query.count()
    if total == 0: return 0.0
    completed = query.filter(Request.status == RequestStatus.COMPLETED).count()
    completion_rate = (completed / total) * 100
    sla_compliance = calculate_sla_compliance_rate(db, None, department_id, start_date, end_date)
    satisfaction_query = query.filter(Request.satisfaction_rating.isnot(None))
    avg_satisfaction = satisfaction_query.with_entities(func.avg(Request.satisfaction_rating)).scalar() or 0
    satisfaction_score = ((float(avg_satisfaction) - 1) / 4) * 100
    efficiency = (completion_rate * sla_compliance * satisfaction_score) ** (1/3)
    return round(efficiency, 2)

def calculate_average_response_time_by_priority(db: Session, priority: Priority, division_id: int = None, start_date: datetime = None, end_date: datetime = None):
    query = db.query(Request).filter(Request.priority == priority, Request.actual_response_time.isnot(None))
    if division_id: query = query.filter(Request.assigned_division_id == division_id)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    requests = query.all()
    if not requests: return 0.0
    total_hours = sum((r.actual_response_time - r.created_at).total_seconds() / 3600 for r in requests)
    return round(total_hours / len(requests), 2)

def calculate_completed_in_period(db: Session, start_date: datetime = None, end_date: datetime = None):
    query = db.query(Request).filter(Request.status == RequestStatus.COMPLETED, Request.actual_completion_time.isnot(None))
    if start_date: query = query.filter(Request.actual_completion_time >= start_date)
    if end_date: query = query.filter(Request.actual_completion_time <= end_date)
    return query.count()

def calculate_overdue_requests(db: Session, department_id: int = None, division_id: int = None):
    """
    Calculates count of requests that are currently overdue.
    Includes active overdue requests (PENDING or IN_PROGRESS past their deadline).
    """
    query = db.query(Request)
    if department_id:
        query = query.filter(Request.assigned_department_id == department_id)
    if division_id:
        query = query.filter(Request.assigned_division_id == division_id)
    
    now = datetime.utcnow()
    
    # Get active requests with SLA time defined
    active_requests = query.filter(
        Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS]),
        Request.sla_completion_time_hours.isnot(None),
        Request.created_at.isnot(None)
    ).all()
    
    overdue_count = 0
    for req in active_requests:
        deadline = req.created_at + timedelta(hours=req.sla_completion_time_hours)
        if now > deadline:
            overdue_count += 1
    
    return overdue_count
