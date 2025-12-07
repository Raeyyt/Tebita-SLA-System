"""
Enhanced KPI Endpoints using kpi_calculator and scorecard_calculator modules
Comprehensive M&E analytics endpoints
"""
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import get_current_active_user
from ..models import User
from ..kpi_calculator import *
from ..scorecard_calculator import (
    calculate_overall_scorecard,
    calculate_overall_scorecard,
    calculate_integration_index
)
from ..services.reporting_service import generate_scorecard_pdf, generate_request_export_csv

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ============================================================================
# GENERAL INTEGRATION KPIs
# ============================================================================

@router.get("/general")
async def get_general_kpis(
    division_id: Optional[int] = None,
    department_id: Optional[int] = None,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get general integration KPIs"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return {
        "period": f"Last {days} days",
        "start_date": start_date,
        "end_date": end_date,
        "kpis": {
            "sla_compliance_rate": calculate_sla_compliance_rate(
                db, division_id, department_id, start_date, end_date
            ),
            "service_fulfillment_rate": calculate_service_request_fulfillment_rate(
                db, division_id, start_date, end_date
            ),
            "customer_satisfaction_score": calculate_customer_satisfaction_score(
                db, division_id, start_date, end_date
            )
        }
    }


# ============================================================================
# FLEET KPIs
# ============================================================================

@router.get("/fleet")
async def get_fleet_kpis(
    days: int = Query(30, description="Number of days to analyze"),
    fleet_size: int = Query(10, description="Total fleet size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all Fleet KPIs"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return {
        "period": f"Last {days} days",
        "fleet_kpis": {
            "vehicle_utilization_rate": calculate_vehicle_utilization_rate(
                db, start_date, end_date, fleet_size
            ),
            "trip_completion_rate": calculate_trip_completion_rate(
                db, start_date, end_date
            ),
            "average_turnaround_time_hours": calculate_average_turnaround_time(
                db, start_date, end_date
            ),
            "fuel_efficiency_km_per_liter": calculate_fuel_efficiency(
                db, start_date, end_date
            ),
            "breakdown_frequency": calculate_breakdown_frequency(
                db, start_date, end_date
            )
        }
    }


# ============================================================================
# HR KPIs
# ============================================================================

@router.get("/hr")
async def get_hr_kpis(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all HR Deployment KPIs"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return {
        "period": f"Last {days} days",
        "hr_kpis": {
            "deployment_filling_rate": calculate_staff_deployment_filling_rate(
                db, start_date, end_date
            ),
            "deployment_response_time_hours": calculate_deployment_average_response_time(
                db, start_date, end_date
            ),
            "overtime_usage_rate": calculate_overtime_usage_rate(
                db, start_date, end_date
            )
        }
    }


# ============================================================================
# FINANCE KPIs
# ============================================================================

@router.get("/finance")
async def get_finance_kpis(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all Finance Transaction KPIs"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return {
        "period": f"Last {days} days",
        "finance_kpis": {
            "payment_processing_turnaround_days": calculate_payment_processing_turnaround_time(
                db, start_date, end_date
            ),
            "payment_accuracy_rate": calculate_payment_accuracy_rate(
                db, start_date, end_date
            ),
            "document_completeness_rate": calculate_document_completeness_rate(
                db, start_date, end_date
            )
        }
    }


# ============================================================================
# ICT KPIs
# ============================================================================

@router.get("/ict")
async def get_ict_kpis(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all ICT Ticketing KPIs"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return {
        "period": f"Last {days} days",
        "ict_kpis": {
            "ticket_resolution_rate": calculate_ticket_resolution_rate(
                db, start_date, end_date
            ),
            "average_response_time_hours": calculate_average_ict_response_time(
                db, start_date, end_date
            ),
            "reopened_tickets_rate": calculate_reopened_tickets_rate(
                db, start_date, end_date
            )
        }
    }


# ============================================================================
# LOGISTICS KPIs
# ============================================================================

@router.get("/logistics")
async def get_logistics_kpis(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all Logistics KPIs"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return {
        "period": f"Last {days} days",
        "logistics_kpis": {
            "on_time_delivery_rate": calculate_on_time_delivery_rate(
                db, start_date, end_date
            ),
            "stock_fulfillment_rate": calculate_stock_fulfillment_rate(
                db, start_date, end_date
            ),
            "requisition_accuracy": calculate_requisition_accuracy(
                db, start_date, end_date
            )
        }
    }


# ============================================================================
# SCORECARD & INTEGRATION INDEX
# ============================================================================

@router.get("/scorecard")
async def get_scorecard_analysis(
    division_id: Optional[int] = None,
    department_id: Optional[int] = None,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get 4-dimension scorecard analysis"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    scorecard = calculate_overall_scorecard(
        db, division_id, department_id, start_date, end_date
    )
    
    return {
        "period": f"Last {days} days",
        "division_id": division_id,
        "department_id": department_id,
        **scorecard
    }


@router.get("/integration-index")
async def get_integration_index_analysis(
    division_id: Optional[int] = None,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get Integration Index (Composite Index)"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    integration_index = calculate_integration_index(
        db, division_id, start_date, end_date
    )
    
    return {
        "period": f"Last {days} days",
        "division_id": division_id,
        **integration_index
    }


# ============================================================================
# COMPREHENSIVE ANALYTICS DASHBOARD
# ============================================================================

@router.get("/dashboard")
async def get_comprehensive_analytics_dashboard(
    division_id: Optional[int] = None,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive M&E analytics dashboard with all KPIs"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Collect all KPIs
    general_kpis = {
        "sla_compliance_rate": calculate_sla_compliance_rate(
            db, division_id, None, start_date, end_date
        ),
        "service_fulfillment_rate": calculate_service_request_fulfillment_rate(
            db, division_id, start_date, end_date
        ),
        "customer_satisfaction_score": calculate_customer_satisfaction_score(
            db, division_id, start_date, end_date
        )
    }
    
    fleet_kpis = {
        "trip_completion_rate": calculate_trip_completion_rate(db, start_date, end_date),
        "fuel_efficiency": calculate_fuel_efficiency(db, start_date, end_date),
    }
    
    hr_kpis = {
        "deployment_filling_rate": calculate_staff_deployment_filling_rate(db, start_date, end_date),
        "overtime_usage_rate": calculate_overtime_usage_rate(db, start_date, end_date),
    }
    
    finance_kpis = {
        "payment_accuracy_rate": calculate_payment_accuracy_rate(db, start_date, end_date),
        "document_completeness_rate": calculate_document_completeness_rate(db, start_date, end_date),
    }
    
    ict_kpis = {
        "ticket_resolution_rate": calculate_ticket_resolution_rate(db, start_date, end_date),
        "reopened_tickets_rate": calculate_reopened_tickets_rate(db, start_date, end_date),
    }
    
    logistics_kpis = {
        "on_time_delivery_rate": calculate_on_time_delivery_rate(db, start_date, end_date),
        "stock_fulfillment_rate": calculate_stock_fulfillment_rate(db, start_date, end_date),
    }
    
    scorecard = calculate_overall_scorecard(db, division_id, None, start_date, end_date)
    integration_index = calculate_integration_index(db, division_id, start_date, end_date)
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
            "days": days
        },
        "general_kpis": general_kpis,
        "resource_kpis": {
            "fleet": fleet_kpis,
            "hr": hr_kpis,
            "finance": finance_kpis,
            "ict": ict_kpis,
            "logistics": logistics_kpis
        },
        "scorecard": scorecard,
        "integration_index": integration_index
    }

@router.get("/scorecard/export")
async def export_scorecard_pdf(
    division_id: Optional[int] = None,
    department_id: Optional[int] = None,
    days: int = Query(30, description="Number of days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export Scorecard as PDF"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Calculate scorecard
    scorecard = calculate_overall_scorecard(db, division_id, department_id, start_date, end_date)
    
    # Generate PDF
    division_name = "All Divisions"
    if division_id:
        # Fetch division name (simplified)
        division_name = f"Division {division_id}" 
        
    pdf_buffer = generate_scorecard_pdf(scorecard, division_name, f"Last {days} Days")
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=scorecard_{datetime.now().strftime('%Y%m%d')}.pdf"}
    )

@router.get("/requests/export")
async def export_requests_csv(
    days: int = Query(30, description="Number of days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export Request Logs as CSV"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    csv_buffer = generate_request_export_csv(db, start_date, end_date)
    
    return StreamingResponse(
        csv_buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=requests_log_{datetime.now().strftime('%Y%m%d')}.csv"}
    )
