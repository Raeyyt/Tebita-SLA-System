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
    Calculate request volume over time using SQL GROUP BY
    """
    start_date, end_date = get_time_range(period, custom_start, custom_end)
    
    # Map period to date_trunc interval
    trunc_map = {
        "daily": "day",
        "weekly": "week",
        "monthly": "month",
        "yearly": "year"
    }
    interval = trunc_map.get(period, "month")
    
    # Query with GROUP BY
    from sqlalchemy import case
    results = db.query(
        func.date_trunc(interval, Request.created_at).label("time_bucket"),
        func.count(Request.id).label("total"),
        func.count(case((Request.status == RequestStatus.PENDING, 1))).label("pending"),
        func.count(case((Request.status == RequestStatus.COMPLETED, 1))).label("completed"),
        func.count(case((Request.status == RequestStatus.REJECTED, 1))).label("rejected")
    ).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date
    ).group_by("time_bucket").order_by("time_bucket").all()
    
    # Format labels and data
    labels = []
    total_data = []
    pending_data = []
    completed_data = []
    rejected_data = []
    
    for r in results:
        if period == "daily":
            labels.append(r.time_bucket.strftime("%b %d"))
        elif period == "weekly":
            labels.append(r.time_bucket.strftime("Week %U"))
        elif period == "monthly":
            labels.append(r.time_bucket.strftime("%b %Y"))
        else:
            labels.append(r.time_bucket.strftime("%Y"))
            
        total_data.append(r.total)
        pending_data.append(r.pending)
        completed_data.append(r.completed)
        rejected_data.append(r.rejected)
    
    return {
        "labels": labels,
        "datasets": [
            {"label": "Total Requests", "data": total_data},
            {"label": "Pending", "data": pending_data},
            {"label": "Completed", "data": completed_data},
            {"label": "Rejected", "data": rejected_data}
        ]
    }


def calculate_sla_compliance_trend(
    db: Session,
    period: TimePeriod = "monthly",
    custom_start: Optional[datetime] = None,
    custom_end: Optional[datetime] = None
) -> Dict:
    """
    Calculate SLA compliance rate over time using SQL GROUP BY
    """
    start_date, end_date = get_time_range(period, custom_start, custom_end)
    interval = {"daily": "day", "weekly": "week", "monthly": "month", "yearly": "year"}.get(period, "month")
    
    from sqlalchemy import case, extract, and_
    
    # We need to count compliant completed and total evaluated (completed + active overdue)
    now_epoch = extract('epoch', func.now())
    created_epoch = extract('epoch', Request.created_at)
    target_seconds = func.coalesce(Request.sla_completion_time_hours, 24) * 3600
    
    results = db.query(
        func.date_trunc(interval, Request.created_at).label("time_bucket"),
        func.count(case((
            and_(
                Request.status == RequestStatus.COMPLETED,
                extract('epoch', Request.actual_completion_time) <= created_epoch + target_seconds
            ), 1
        ))).label("compliant"),
        func.count(case((
            or_(
                Request.status == RequestStatus.COMPLETED,
                and_(
                    Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS]),
                    now_epoch > created_epoch + target_seconds
                )
            ), 1
        ))).label("evaluated")
    ).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date
    ).group_by("time_bucket").order_by("time_bucket").all()
    
    labels = []
    compliance_data = []
    
    for r in results:
        if period == "daily":
            labels.append(r.time_bucket.strftime("%b %d"))
        elif period == "weekly":
            labels.append(r.time_bucket.strftime("Week %U"))
        elif period == "monthly":
            labels.append(r.time_bucket.strftime("%b %Y"))
        else:
            labels.append(r.time_bucket.strftime("%Y"))
            
        rate = (r.compliant / r.evaluated * 100) if r.evaluated > 0 else 100
        compliance_data.append(round(rate, 2))
    
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
    Calculate request distribution by division using SQL GROUP BY
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
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
    Calculate request distribution by priority over time using SQL GROUP BY
    """
    start_date, end_date = get_time_range(period, custom_start, custom_end)
    interval = {"daily": "day", "weekly": "week", "monthly": "month", "yearly": "year"}.get(period, "month")
    
    from sqlalchemy import case
    results = db.query(
        func.date_trunc(interval, Request.created_at).label("time_bucket"),
        func.count(case((Request.priority == Priority.HIGH, 1))).label("high"),
        func.count(case((Request.priority == Priority.MEDIUM, 1))).label("medium"),
        func.count(case((Request.priority == Priority.LOW, 1))).label("low")
    ).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date
    ).group_by("time_bucket").order_by("time_bucket").all()
    
    labels = []
    high_data = []
    medium_data = []
    low_data = []
    
    for r in results:
        if period == "daily":
            labels.append(r.time_bucket.strftime("%b %d"))
        elif period == "weekly":
            labels.append(r.time_bucket.strftime("Week %U"))
        elif period == "monthly":
            labels.append(r.time_bucket.strftime("%b %Y"))
        else:
            labels.append(r.time_bucket.strftime("%Y"))
            
        high_data.append(r.high)
        medium_data.append(r.medium)
        low_data.append(r.low)
    
    return {
        "labels": labels,
        "datasets": [
            {"label": "High", "data": high_data},
            {"label": "Medium", "data": medium_data},
            {"label": "Low", "data": low_data}
        ]
    }


def calculate_response_time_by_resource(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """
    Calculate average response time by resource type using SQL GROUP BY
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    from sqlalchemy import extract
    results = db.query(
        Request.resource_type,
        func.avg(
            extract('epoch', Request.actual_response_time) - extract('epoch', Request.created_at)
        ).label("avg_seconds")
    ).filter(
        Request.actual_response_time.isnot(None),
        Request.created_at >= start_date,
        Request.created_at <= end_date
    ).group_by(Request.resource_type).all()
    
    return {
        "labels": [r[0].value for r in results],
        "data": [round(r.avg_seconds / 3600, 2) if r.avg_seconds else 0 for r in results]
    }


def calculate_request_status_distribution(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """
    Calculate current request status distribution using SQL GROUP BY
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
    Calculate satisfaction ratings over time using SQL GROUP BY
    """
    start_date, end_date = get_time_range(period, custom_start, custom_end)
    interval = {"daily": "day", "weekly": "week", "monthly": "month", "yearly": "year"}.get(period, "month")
    
    results = db.query(
        func.date_trunc(interval, Request.created_at).label("time_bucket"),
        func.avg(Request.satisfaction_rating).label("avg_rating")
    ).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date,
        Request.satisfaction_rating.isnot(None)
    ).group_by("time_bucket").order_by("time_bucket").all()
    
    labels = []
    satisfaction_data = []
    
    for r in results:
        if period == "daily":
            labels.append(r.time_bucket.strftime("%b %d"))
        elif period == "weekly":
            labels.append(r.time_bucket.strftime("Week %U"))
        elif period == "monthly":
            labels.append(r.time_bucket.strftime("%b %Y"))
        else:
            labels.append(r.time_bucket.strftime("%Y"))
            
        satisfaction_data.append(round(r.avg_rating, 2) if r.avg_rating else 0)
    
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
    Calculate Service Efficiency score over time using SQL GROUP BY
    """
    start_date, end_date = get_time_range(period, custom_start, custom_end)
    interval = {"daily": "day", "weekly": "week", "monthly": "month", "yearly": "year"}.get(period, "month")
    
    from sqlalchemy import extract
    results = db.query(
        func.date_trunc(interval, Request.created_at).label("time_bucket"),
        func.avg(
            extract('epoch', Request.completed_at) - extract('epoch', Request.created_at)
        ).label("avg_seconds")
    ).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date,
        Request.status == RequestStatus.COMPLETED,
        Request.completed_at.isnot(None)
    ).group_by("time_bucket").order_by("time_bucket").all()
    
    labels = []
    efficiency_data = []
    
    for r in results:
        if period == "daily":
            labels.append(r.time_bucket.strftime("%b %d"))
        elif period == "weekly":
            labels.append(r.time_bucket.strftime("Week %U"))
        elif period == "monthly":
            labels.append(r.time_bucket.strftime("%b %Y"))
        else:
            labels.append(r.time_bucket.strftime("%Y"))
            
        if r.avg_seconds:
            avg_hours = r.avg_seconds / 3600
            # 72 hours baseline
            score = min(100, max(0, 100 - (avg_hours / 72 * 100)))
            efficiency_data.append(round(score, 2))
        else:
            efficiency_data.append(0)
            
    return {
        "labels": labels,
        "datasets": [
            {"label": "Service Efficiency", "data": efficiency_data}
        ]
    }
