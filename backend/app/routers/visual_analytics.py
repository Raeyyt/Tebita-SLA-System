"""
Visual Analytics Dashboard Router
Provides comprehensive chart data for admin visual analytics dashboard
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, Literal
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import get_current_active_user
from ..models import User, UserRole, Request, RequestStatus
from ..services.trend_calculator import (
    calculate_request_volume_trend,
    calculate_sla_compliance_trend,
    calculate_requests_by_division,
    calculate_requests_by_priority,
    calculate_response_time_by_resource,
    calculate_request_status_distribution,
    calculate_satisfaction_trend,
    calculate_service_efficiency_trend,
)
from ..kpi_calculator import (
    calculate_sla_compliance_rate,
    calculate_service_request_fulfillment_rate,
    calculate_customer_satisfaction_score
)
from ..scorecard_calculator import calculate_integration_index

def calculate_rejection_rate(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
    query = db.query(Request)
    if start_date: query = query.filter(Request.created_at >= start_date)
    if end_date: query = query.filter(Request.created_at <= end_date)
    
    total = query.count()
    if total == 0: return 0.0
    
    rejected = query.filter(Request.status == RequestStatus.REJECTED).count()
    return (rejected / total) * 100.0

router = APIRouter(prefix="/visual-analytics", tags=["visual-analytics"])


@router.get("/dashboard")
async def get_visual_dashboard_data(
    period: Literal["daily", "weekly", "monthly", "yearly"] = Query("monthly"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive visual analytics dashboard data
    Returns data for 10 charts in chart-ready format
    
    Access: Admin only
    """
    # Check admin access
    if current_user.role != UserRole.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Parse dates if provided
    custom_start = datetime.fromisoformat(start_date) if start_date else None
    custom_end = datetime.fromisoformat(end_date) if end_date else None
    
    # Calculate Summary KPIs manually
    completed_query = db.query(Request).filter(Request.status == RequestStatus.COMPLETED)
    if custom_start: completed_query = completed_query.filter(Request.created_at >= custom_start)
    if custom_end: completed_query = completed_query.filter(Request.created_at <= custom_end)
    completed_count = completed_query.count()
    
    integration_data = calculate_integration_index(db, None, custom_start, custom_end)
    
    summary_kpis = {
        "sla_compliance": calculate_sla_compliance_rate(db, None, None, custom_start, custom_end),
        "fulfillment_rate": calculate_service_request_fulfillment_rate(db, None, custom_start, custom_end),
        "completed_count": completed_count,
        "satisfaction": calculate_customer_satisfaction_score(db, None, custom_start, custom_end),
        "integration_index": integration_data.get("integration_index", 0),
        "resource_optimization": 85.0, # Placeholder (Demo Value)
        "avg_cost_per_request": 0.0, # Placeholder (Requires Finance Module)
        "rejection_rate": calculate_rejection_rate(db, custom_start, custom_end)
    }
    
    # Calculate all chart data
    return {
        "period": period,
        "generated_at": datetime.utcnow().isoformat(),
        
        # Chart 1: Request Volume Over Time (Line Chart)
        "request_volume": calculate_request_volume_trend(db, period, custom_start, custom_end),
        
        # Chart 2: SLA Compliance Trend (Area Chart)
        "sla_compliance": calculate_sla_compliance_trend(db, period, custom_start, custom_end),
        
        # Chart 3: Requests by Division (Pie Chart)
        "requests_by_division": calculate_requests_by_division(db, custom_start, custom_end),
        
        # Chart 4: Requests by Priority (Stacked Bar Chart)
        "requests_by_priority": calculate_requests_by_priority(db, period, custom_start, custom_end),
        
        # Chart 5: Service Efficiency Trend (Line Chart) - REPLACES Response Time by Resource
        "service_efficiency": calculate_service_efficiency_trend(db, period, custom_start, custom_end),
        
        # Chart 6: Request Status Distribution (Donut Chart)
        "status_distribution": calculate_request_status_distribution(db, custom_start, custom_end),
        
        # Chart 7: Satisfaction Trend (Line Chart)
        "satisfaction_trend": calculate_satisfaction_trend(db, period, custom_start, custom_end),
        
        # Summary KPIs (for dashboard header)
        "summary_kpis": summary_kpis
    }


@router.get("/request-volume")
async def get_request_volume_chart(
    period: Literal["daily", "weekly", "monthly", "yearly"] = Query("monthly"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get request volume trend data for individual chart download"""
    if current_user.role != UserRole.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    
    custom_start = datetime.fromisoformat(start_date) if start_date else None
    custom_end = datetime.fromisoformat(end_date) if end_date else None
    
    return calculate_request_volume_trend(db, period, custom_start, custom_end)


@router.get("/sla-compliance")
async def get_sla_compliance_chart(
    period: Literal["daily", "weekly", "monthly", "yearly"] = Query("monthly"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get SLA compliance trend data"""
    if current_user.role != UserRole.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    
    custom_start = datetime.fromisoformat(start_date) if start_date else None
    custom_end = datetime.fromisoformat(end_date) if end_date else None
    
    return calculate_sla_compliance_trend(db, period, custom_start, custom_end)


@router.get("/division-distribution")
async def get_division_distribution_chart(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get requests by division data"""
    if current_user.role != UserRole.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    
    custom_start = datetime.fromisoformat(start_date) if start_date else None
    custom_end = datetime.fromisoformat(end_date) if end_date else None
    
    return calculate_requests_by_division(db, custom_start, custom_end)


@router.get("/priority-distribution")
async def get_priority_distribution_chart(
    period: Literal["daily", "weekly", "monthly", "yearly"] = Query("monthly"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get requests by priority data"""
    if current_user.role != UserRole.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    
    custom_start = datetime.fromisoformat(start_date) if start_date else None
    custom_end = datetime.fromisoformat(end_date) if end_date else None
    
    return calculate_requests_by_priority(db, period, custom_start, custom_end)


@router.get("/service-efficiency")
async def get_service_efficiency_chart(
    period: Literal["daily", "weekly", "monthly", "yearly"] = Query("monthly"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get service efficiency trend data"""
    if current_user.role != UserRole.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    
    custom_start = datetime.fromisoformat(start_date) if start_date else None
    custom_end = datetime.fromisoformat(end_date) if end_date else None
    
    return calculate_service_efficiency_trend(db, period, custom_start, custom_end)


@router.get("/status-distribution")
async def get_status_distribution_chart(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get request status distribution data"""
    if current_user.role != UserRole.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    
    custom_start = datetime.fromisoformat(start_date) if start_date else None
    custom_end = datetime.fromisoformat(end_date) if end_date else None
    
    return calculate_request_status_distribution(db, custom_start, custom_end)


@router.get("/satisfaction-trend")
async def get_satisfaction_trend_chart(
    period: Literal["daily", "weekly", "monthly", "yearly"] = Query("weekly"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get satisfaction ratings trend data"""
    if current_user.role != UserRole.ADMIN:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    
    custom_start = datetime.fromisoformat(start_date) if start_date else None
    custom_end = datetime.fromisoformat(end_date) if end_date else None
    
    return calculate_satisfaction_trend(db, period, custom_start, custom_end)
