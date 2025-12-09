from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from app.models import Request, RequestStatus, Priority, FleetRequest, HRDeployment, FinanceTransaction, ICTTicket, LogisticsRequest, CustomerSatisfaction
from datetime import datetime, timedelta

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
            "pending_requests": 0
        }

    # 1. SLA Resolution Compliance
    # Count requests that are COMPLETED and actual_completion_time <= sla_completion_deadline
    compliant_count = query.filter(
        Request.status == RequestStatus.COMPLETED,
        Request.actual_completion_time <= Request.sla_completion_deadline
    ).count()
    
    completed_count = query.filter(Request.status == RequestStatus.COMPLETED).count()
    compliance_rate = (compliant_count / completed_count * 100) if completed_count > 0 else 100

    # 2. Average Resolution Time
    # Avg of (actual_completion_time - created_at) for completed requests
    # Note: This is a simplified calculation. For precise DB-side avg, we'd use func.avg with epoch extraction.
    # Here we'll do it in Python for simplicity if volume is low, or use a hybrid approach.
    # Let's use a DB query for efficiency.
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

    return {
        "total_requests": total_requests,
        "sla_compliance_rate": round(compliance_rate, 1),
        "avg_resolution_time_hours": avg_hours,
        "pending_requests": pending_count,
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
    # Count unique vehicles used in the period
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
    # Avg time between dispatch and return
    # Note: This assumes dispatch_time and return_time are stored as strings or datetimes. 
    # If strings, this SQL avg won't work directly. Assuming datetime or handling in python.
    # For now returning placeholder 0.0 as schema has them as strings/datetime?
    # Schema says string. We need to cast or fetch and compute.
    return 0.0 # Placeholder for complex string-date parsing

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

def calculate_staff_utilization(db: Session, start_date: datetime, end_date: datetime):
    # Placeholder: Ratio of deployed staff vs total pool
    return 85.0 

# ============================================================================
# FINANCE KPIs
# ============================================================================

def calculate_payment_accuracy(db: Session, start_date: datetime, end_date: datetime):
    query = db.query(FinanceTransaction).join(Request)
    query = query.filter(Request.created_at >= start_date, Request.created_at <= end_date)
    
    total = query.count()
    if total == 0: return 100.0
    
    accurate = query.filter(FinanceTransaction.payment_accuracy == True).count()
    return (accurate / total) * 100.0
