"""
Trend Calculator Service
Calculates time-series data for visual analytics dashboard
Supports daily, weekly, monthly, and yearly aggregations
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Literal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from collections import defaultdict

from app.models import Request, RequestStatus, Priority, ResourceType, Division, Department


TimePeriod = Literal["daily", "weekly", "monthly", "yearly"]


def get_time_range(period: TimePeriod, custom_start:Optional[datetime] = None, custom_end: Optional[datetime] = None):
    """Get start and end dates for a time period"""
    if custom_start and custom_end:
        return custom_start, custom_end
    
    end_date = datetime.utcnow()
    
    if period == "daily":
        start_date = end_date - timedelta(days=30)  # Last 30 days
    elif period == "weekly":
        start_date = end_date - timedelta(weeks=12)  # Last 12 weeks
    elif period == "monthly":
        start_date = end_date - timedelta(days=365)  # Last 12 months
    else:  # yearly
        start_date = end_date - timedelta(days=365 * 3)  # Last 3 years
    
    return start_date, end_date


def generate_time_labels(start_date: datetime, end_date: datetime, period: TimePeriod) -> List[str]:
    """Generate time labels for chart x-axis"""
    labels = []
    current = start_date
    
    if period == "daily":
        while current <= end_date:
            labels.append(current.strftime("%b %d"))
            current += timedelta(days=1)
    elif period == "weekly":
        while current <= end_date:
            labels.append(current.strftime("Week %U"))
            current += timedelta(weeks=1)
    elif period == "monthly":
        while current <= end_date:
            labels.append(current.strftime("%b %Y"))
            current = (current.replace(day=1) + timedelta(days=32)).replace(day=1)
    else:  # yearly
        while current <= end_date:
            labels.append(current.strftime("%Y"))
            current = current.replace(year=current.year + 1)
    
    return labels


def calculate_request_volume_trend(
    db: Session,
    period: TimePeriod = "monthly",
    custom_start: Optional[datetime] = None,
    custom_end: Optional[datetime] = None
) -> Dict:
    """
    Calculate request volume over time
    Returns data for line chart showing total, pending, completed
    """
    start_date, end_date = get_time_range(period, custom_start, custom_end)
    labels = generate_time_labels(start_date, end_date, period)
    
    # Query all requests in period
    requests = db.query(Request).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date
    ).all()
    
    # Initialize data buckets
    total_data = {label: 0 for label in labels}
    pending_data = {label: 0 for label in labels}
    completed_data = {label: 0 for label in labels}
    rejected_data = {label: 0 for label in labels}
    
    # Aggregate by time period
    for request in requests:
        if period == "daily":
            label = request.created_at.strftime("%b %d")
        elif period == "weekly":
            label = request.created_at.strftime("Week %U")
        elif period == "monthly":
            label = request.created_at.strftime("%b %Y")
        else:  # yearly
            label = request.created_at.strftime("%Y")
        
        if label in total_data:
            total_data[label] += 1
            if request.status == RequestStatus.PENDING:
                pending_data[label] += 1
            elif request.status == RequestStatus.COMPLETED:
                completed_data[label] += 1
            elif request.status == RequestStatus.REJECTED:
                rejected_data[label] += 1
    
    return {
        "labels": labels,
        "datasets": [
            {"label": "Total Requests", "data": [total_data[l] for l in labels]},
            {"label": "Pending", "data": [pending_data[l] for l in labels]},
            {"label": "Completed", "data": [completed_data[l] for l in labels]},
            {"label": "Rejected", "data": [rejected_data[l] for l in labels]}
        ]
    }


def calculate_sla_compliance_trend(
    db: Session,
    period: TimePeriod = "monthly",
    custom_start: Optional[datetime] = None,
    custom_end: Optional[datetime] = None
) -> Dict:
    """
    Calculate SLA compliance rate over time
    Returns data for area chart
    """
    start_date, end_date = get_time_range(period, custom_start, custom_end)
    labels = generate_time_labels(start_date, end_date, period)
    
    # Query completed requests in period
    requests = db.query(Request).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date,
        Request.status == RequestStatus.COMPLETED,
        Request.actual_completion_time.isnot(None),
        Request.sla_completion_deadline.isnot(None)
    ).all()
    
    # Calculate compliance for each period
    total_per_period = {label: 0 for label in labels}
    on_time_per_period = {label: 0 for label in labels}
    
    for request in requests:
        if period == "daily":
            label = request.created_at.strftime("%b %d")
        elif period == "weekly":
            label = request.created_at.strftime("Week %U")
        elif period == "monthly":
            label = request.created_at.strftime("%b %Y")
        else:
            label = request.created_at.strftime("%Y")
        
        if label in total_per_period:
            total_per_period[label] += 1
            if request.actual_completion_time <= request.sla_completion_deadline:
                on_time_per_period[label] += 1
    
    # Calculate percentages
    compliance_data = []
    for label in labels:
        if total_per_period[label] > 0:
            compliance = (on_time_per_period[label] / total_per_period[label]) * 100
            compliance_data.append(round(compliance, 2))
        else:
            compliance_data.append(0)
    
    return {
        "labels": labels,
        "datasets": [
            {"label": "SLA Compliance %", "data": compliance_data}
        ]
    }


def calculate_requests_by_division(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """
    Calculate request distribution by division
    Returns data for pie chart
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Query with division join
    results = db.query(
        Division.name,
        func.count(Request.id).label('count')
    ).join(Request, Request.requester_division_id == Division.id).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date
    ).group_by(Division.name).all()
    
    return {
        "labels": [r[0] for r in results],
        "data": [r[1] for r in results]
    }


def calculate_requests_by_priority(
    db: Session,
    period: TimePeriod = "monthly",
    custom_start: Optional[datetime] = None,
    custom_end: Optional[datetime] = None
) -> Dict:
    """
    Calculate request distribution by priority over time
    Returns data for stacked bar chart
    """
    start_date, end_date = get_time_range(period, custom_start, custom_end)
    labels = generate_time_labels(start_date, end_date, period)
    
    requests = db.query(Request).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date
    ).all()
    
    high_data = {label: 0 for label in labels}
    medium_data = {label: 0 for label in labels}
    low_data = {label: 0 for label in labels}
    
    for request in requests:
        if period == "daily":
            label = request.created_at.strftime("%b %d")
        elif period == "weekly":
            label = request.created_at.strftime("Week %U")
        elif period == "monthly":
            label = request.created_at.strftime("%b %Y")
        else:
            label = request.created_at.strftime("%Y")
        
        if label in high_data:
            if request.priority == Priority.HIGH:
                high_data[label] += 1
            elif request.priority == Priority.MEDIUM:
                medium_data[label] += 1
            else:
                low_data[label] += 1
    
    return {
        "labels": labels,
        "datasets": [
            {"label": "High", "data": [high_data[l] for l in labels]},
            {"label": "Medium", "data": [medium_data[l] for l in labels]},
            {"label": "Low", "data": [low_data[l] for l in labels]}
        ]
    }


def calculate_response_time_by_resource(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """
    Calculate average response time by resource type
    Returns data for bar chart
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    resource_types = [ResourceType.FLEET, ResourceType.HR, ResourceType.FINANCE, 
                      ResourceType.ICT, ResourceType.LOGISTICS, ResourceType.FACILITIES]
    
    labels = []
    data = []
    
    for resource_type in resource_types:
        requests = db.query(Request).filter(
            Request.resource_type == resource_type,
            Request.actual_response_time.isnot(None),
            Request.created_at >= start_date,
            Request.created_at <= end_date
        ).all()
        
        if requests:
            avg_response = sum(
                (r.actual_response_time - r.created_at).total_seconds() / 3600
                for r in requests
            ) / len(requests)
            labels.append(resource_type.value)
            data.append(round(avg_response, 2))
    
    return {
        "labels": labels,
        "data": data
    }


def calculate_request_status_distribution(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """
    Calculate current request status distribution
    Returns data for donut chart
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    results = db.query(
        Request.status,
        func.count(Request.id).label('count')
    ).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date
    ).group_by(Request.status).all()
    
    return {
        "labels": [r[0].value for r in results],
        "data": [r[1] for r in results]
    }


def calculate_satisfaction_trend(
    db: Session,
    period: TimePeriod = "weekly",
    custom_start: Optional[datetime] = None,
    custom_end: Optional[datetime] = None
) -> Dict:
    """
    Calculate satisfaction ratings over time
    Returns data for line chart
    """
    start_date, end_date = get_time_range(period, custom_start, custom_end)
    labels = generate_time_labels(start_date, end_date, period)
    
    requests = db.query(Request).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date,
        Request.satisfaction_rating.isnot(None)
    ).all()
    
    # Calculate average satisfaction for each period
    total_per_period = {label: [] for label in labels}
    
    for request in requests:
        if period == "daily":
            label = request.created_at.strftime("%b %d")
        elif period == "weekly":
            label = request.created_at.strftime("Week %U")
        elif period == "monthly":
            label = request.created_at.strftime("%b %Y")
        else:
            label = request.created_at.strftime("%Y")
        
        if label in total_per_period:
            total_per_period[label].append(request.satisfaction_rating)
    
    # Calculate averages
    satisfaction_data = []
    for label in labels:
        if total_per_period[label]:
            avg = sum(total_per_period[label]) / len(total_per_period[label])
            satisfaction_data.append(round(avg, 2))
        else:
            satisfaction_data.append(0)
    
    return {
        "labels": labels,
        "datasets": [
            {"label": "Satisfaction Rating", "data": satisfaction_data}
        ]
    }


def calculate_service_efficiency_trend(
    db: Session,
    period: TimePeriod = "monthly",
    custom_start: Optional[datetime] = None,
    custom_end: Optional[datetime] = None
) -> Dict:
    """
    Calculate Service Efficiency score over time
    Based on completion time vs baseline (72h)
    Returns data for line chart
    """
    start_date, end_date = get_time_range(period, custom_start, custom_end)
    labels = generate_time_labels(start_date, end_date, period)
    
    # Query completed requests in period
    requests = db.query(Request).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date,
        Request.status == RequestStatus.COMPLETED,
        Request.completed_at.isnot(None)
    ).all()
    
    # Group by period
    period_requests = {label: [] for label in labels}
    
    for request in requests:
        if period == "daily":
            label = request.created_at.strftime("%b %d")
        elif period == "weekly":
            label = request.created_at.strftime("Week %U")
        elif period == "monthly":
            label = request.created_at.strftime("%b %Y")
        else:
            label = request.created_at.strftime("%Y")
        
        if label in period_requests:
            period_requests[label].append(request)
            
    # Calculate efficiency for each period
    efficiency_data = []
    for label in labels:
        reqs = period_requests[label]
        if reqs:
            avg_time = sum([(r.completed_at - r.created_at).total_seconds() / 3600 for r in reqs]) / len(reqs)
            # 72 hours baseline
            score = min(100, max(0, 100 - (avg_time / 72 * 100)))
            efficiency_data.append(round(score, 2))
        else:
            efficiency_data.append(0)
            
    return {
        "labels": labels,
        "datasets": [
            {"label": "Service Efficiency", "data": efficiency_data}
        ]
    }
