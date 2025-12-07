"""
Scorecard Calculator Module
Implements 4-dimension scorecard system as per organizational requirements:
1. Service Efficiency (25%)
2. SLA Compliance & Data Quality (30%)
3. Cost & Resource Optimization (20%)
4. Customer Satisfaction & Integration (25%)
"""
from datetime import datetime
from typing import Dict, Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models import Request, RequestStatus, ScoreRating
from app.kpi_calculator import (
    calculate_sla_compliance_rate,
    calculate_service_request_fulfillment_rate,
    calculate_customer_satisfaction_score,
    calculate_vehicle_utilization_rate,
    calculate_staff_deployment_filling_rate
)


# ============================================================================
# SCORECARD DIMENSION CALCULATIONS
# ============================================================================

def calculate_service_efficiency_score(
    db: Session,
    division_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """
    Service Efficiency Score (25% of total)
    Components:
    - SLA Response Time (10%)
    - SLA Completion Time (10%)
    - Resource Utilization Efficiency (5%)
    """
    # Calculate average response time compliance
    query = db.query(Request).filter(
        Request.actual_response_time.isnot(None),
        Request.sla_response_deadline.isnot(None)
    )
    
    if division_id:
        query = query.filter(Request.requester_division_id == division_id)
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    requests = query.all()
    if not requests:
        return 0.0
    
    # Response time score (10%)
    response_on_time = sum(
        1 for r in requests 
        if r.actual_response_time <= r.sla_response_deadline
    )
    response_score = (response_on_time / len(requests)) * 10
    
    # Completion time score (10%) - from SLA compliance
    completion_rate = calculate_sla_compliance_rate(
        db, division_id, None, start_date, end_date
    )
    completion_score = (completion_rate / 100) * 10
    
    # Resource utilization (5%) - simplified
    utilization_score = 4.0  # Baseline score
    
    total_score = response_score + completion_score + utilization_score
    return round(total_score, 2)


def calculate_compliance_score(
    db: Session,
    division_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """
    SLA Compliance & Data Quality Score (30% of total)
    Components:
    - SLA Compliance Rate (10%)
    - Data Completeness Rate (5%)
    - Reporting Timeliness (5%)
    - KPI Reporting Accuracy (5%)
    - M&E Verification Compliance (5%)
    """
    # SLA Compliance (10%)
    sla_rate = calculate_sla_compliance_rate(
        db, division_id, None, start_date, end_date
    )
    sla_score = (sla_rate / 100) * 10
    
    # Data Completeness (5%) - check satisfaction rating completion
    query = db.query(Request).filter(Request.status == RequestStatus.COMPLETED)
    
    if division_id:
        query = query.filter(Request.requester_division_id == division_id)
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    total_completed = query.count()
    with_satisfaction = query.filter(
        Request.satisfaction_rating.isnot(None)
    ).count()
    
    completeness_rate = (with_satisfaction / total_completed * 100) if total_completed > 0 else 0
    completeness_score = (completeness_rate / 100) * 5
    
    # Other scores (simplified for now)
    reporting_score = 4.5  # 5% baseline
    accuracy_score = 4.5   # 5% baseline
    verification_score = 4.5  # 5% baseline
    
    total_score = sla_score + completeness_score + reporting_score + accuracy_score + verification_score
    return round(total_score, 2)


def calculate_cost_optimization_score(
    db: Session,
    division_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """
    Cost & Resource Optimization Score (20% of total)
    Components:
    - Cost per Transaction (5%)
    - Fleet Cost Efficiency (5%)
    - HR Deployment Efficiency (5%)
    - ICT Resolution Cost (5%)
    """
    # Calculate cost variance (actual vs estimate)
    query = db.query(Request).filter(
        Request.cost_estimate.isnot(None),
        Request.actual_cost.isnot(None),
        Request.cost_estimate > 0
    )
    
    if division_id:
        query = query.filter(Request.requester_division_id == division_id)
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    requests = query.all()
    
    if requests:
        # Cost efficiency: actual <= estimate is good
        within_budget = sum(
            1 for r in requests 
            if r.actual_cost <= r.cost_estimate
        )
        cost_score = (within_budget / len(requests)) * 5
    else:
        cost_score = 4.0  # Baseline
    
    # Other components (simplified)
    fleet_score = 4.5   # 5% baseline
    hr_score = 4.5      # 5% baseline
    ict_score = 4.5     # 5% baseline
    
    total_score = cost_score + fleet_score + hr_score + ict_score
    return round(total_score, 2)


def calculate_satisfaction_integration_score(
    db: Session,
    division_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> float:
    """
    Customer Satisfaction & Integration Score (25% of total)
    Components:
    - Division Satisfaction Score (10%)
    - Integration Index Score (10%)
    - Learning & Accountability Implementation (5%)
    """
    # Customer Satisfaction (10%)
    avg_satisfaction = calculate_customer_satisfaction_score(
        db, division_id, start_date, end_date
    )
    satisfaction_score = (avg_satisfaction / 5) * 10  # Convert 1-5 scale to 10%
    
    # Integration Index (10%) - based on fulfillment rate
    fulfillment_rate = calculate_service_request_fulfillment_rate(
        db, division_id, start_date, end_date
    )
    integration_score = (fulfillment_rate / 100) * 10
    
    # Learning & Accountability (5%) - baseline
    learning_score = 4.0
    
    total_score = satisfaction_score + integration_score + learning_score
    return round(total_score, 2)


# ============================================================================
# OVERALL SCORECARD
# ============================================================================

def calculate_overall_scorecard(
    db: Session,
    division_id: Optional[int] = None,
    department_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """
    Calculate overall scorecard with all 4 dimensions
    Returns dictionary with scores and rating
    """
    # Calculate each dimension
    service_efficiency = calculate_service_efficiency_score(
        db, division_id, start_date, end_date
    )
    
    compliance = calculate_compliance_score(
        db, division_id, start_date, end_date
    )
    
    cost_optimization = calculate_cost_optimization_score(
        db, division_id, start_date, end_date
    )
    
    satisfaction_integration = calculate_satisfaction_integration_score(
        db, division_id, start_date, end_date
    )
    
    # Total score (out of 100)
    total_score = (
        service_efficiency +      # 25%
        compliance +              # 30%
        cost_optimization +       # 20%
        satisfaction_integration  # 25%
    )
    
    # Determine rating
    rating = get_scorecard_rating(total_score)
    
    return {
        "service_efficiency_score": service_efficiency,
        "compliance_score": compliance,
        "cost_optimization_score": cost_optimization,
        "satisfaction_score": satisfaction_integration,
        "total_score": round(total_score, 2),
        "rating": rating,
        "breakdown": {
            "service_efficiency": {
                "score": service_efficiency,
                "weight": "25%",
                "components": ["SLA Response", "SLA Completion", "Resource Utilization"]
            },
            "compliance": {
                "score": compliance,
                "weight": "30%",
                "components": ["SLA Compliance", "Data Completeness", "Reporting Timeliness"]
            },
            "cost_optimization": {
                "score": cost_optimization,
                "weight": "20%",
                "components": ["Cost per Transaction", "Fleet Efficiency", "HR Efficiency"]
            },
            "satisfaction": {
                "score": satisfaction_integration,
                "weight": "25%",
                "components": ["Customer Satisfaction", "Integration Index", "Learning"]
            }
        }
    }


def get_scorecard_rating(total_score: float) -> str:
    """
    Determine rating based on total score
    Rating Scale:
    - 90-100% = Outstanding
    - 80-89% = Very Good
    - 70-79% = Good
    - 60-69% = Needs Improvement
    - Below 60% = Unsatisfactory
    """
    if total_score >= 90:
        return ScoreRating.OUTSTANDING.value
    elif total_score >= 80:
        return ScoreRating.VERY_GOOD.value
    elif total_score >= 70:
        return ScoreRating.GOOD.value
    elif total_score >= 60:
        return ScoreRating.NEEDS_IMPROVEMENT.value
    else:
        return ScoreRating.UNSATISFACTORY.value


# ============================================================================
# INTEGRATION INDEX
# ============================================================================

def calculate_integration_index(
    db: Session,
    division_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """
    Calculate Integration Index (Composite Index)
    Components:
    - Coordination Effectiveness
    - Process Alignment
    - Timeliness of Reporting
    - Cross-division Collaboration
    """
    # Coordination Effectiveness (based on SLA compliance)
    sla_rate = calculate_sla_compliance_rate(
        db, division_id, None, start_date, end_date
    )
    coordination = round(sla_rate, 2)
    
    # Process Alignment (based on fulfillment rate)
    fulfillment_rate = calculate_service_request_fulfillment_rate(
        db, division_id, start_date, end_date
    )
    alignment = round(fulfillment_rate, 2)
    
    # Reporting Timeliness (simplified - based on data completeness)
    query = db.query(Request).filter(Request.status == RequestStatus.COMPLETED)
    if division_id:
        query = query.filter(Request.requester_division_id == division_id)
    if start_date:
        query = query.filter(Request.created_at >= start_date)
    if end_date:
        query = query.filter(Request.created_at <= end_date)
    
    total = query.count()
    with_data = query.filter(Request.satisfaction_rating.isnot(None)).count()
    timeliness = round((with_data / total * 100) if total > 0 else 0, 2)
    
    # Collaboration (based on cross-division requests)
    collaboration = 85.0  # Baseline
    
    # Overall index (average of components)
    overall_index = round(
        (coordination + alignment + timeliness + collaboration) / 4,
        2
    )
    
    return {
        "integration_index": overall_index,
        "components": {
            "coordination_effectiveness": coordination,
            "process_alignment": alignment,
            "reporting_timeliness": timeliness,
            "collaboration_score": collaboration
        }
    }
