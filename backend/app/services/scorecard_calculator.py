from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.models import Request, RequestStatus, CustomerSatisfaction, KPIMetric

def calculate_overall_scorecard(db: Session, division_id: int = None, department_id: int = None, start_date: datetime = None, end_date: datetime = None):
    """
    Calculates the overall scorecard metrics for a given period and scope.
    Returns a dict with scores for the 4 dimensions and the total score.
    """
    # 1. Service Efficiency (40%)
    # Based on SLA Compliance and Avg Resolution Time
    efficiency_score = _calculate_service_efficiency(db, division_id, department_id, start_date, end_date)
    
    # 2. Compliance (20%)
    # Placeholder: In a real system, this would check SOP adherence from audit logs or specific form fields.
    # For now, we'll use a default high score or random variation for demo, 
    # or derive it from "Documentation Complete" fields in resource forms if available.
    compliance_score = 95.0 
    
    # 3. Cost Optimization (20%)
    # Placeholder: Could be based on budget variance.
    cost_score = 90.0
    
    # 4. Customer Satisfaction (20%)
    satisfaction_score = _calculate_satisfaction_score(db, division_id, department_id, start_date, end_date)
    
    # Weighted Total
    total_score = (
        (efficiency_score * 0.4) +
        (compliance_score * 0.2) +
        (cost_score * 0.2) +
        (satisfaction_score * 0.2)
    )
    
    return {
        "service_efficiency": round(efficiency_score, 1),
        "compliance": round(compliance_score, 1),
        "cost_optimization": round(cost_score, 1),
        "satisfaction": round(satisfaction_score, 1),
        "total_score": round(total_score, 1),
        "rating": _get_rating_label(total_score)
    }

def calculate_integration_index(db: Session, start_date: datetime, end_date: datetime):
    """
    Calculates a system-wide 'Integration Index' representing overall health/efficiency.
    """
    # Simple average of all department scores for now
    scorecard = calculate_overall_scorecard(db, start_date=start_date, end_date=end_date)
    return scorecard["total_score"]

def _calculate_service_efficiency(db: Session, division_id, department_id, start, end):
    query = db.query(Request).filter(Request.created_at >= start, Request.created_at <= end)
    if division_id:
        query = query.filter(Request.assigned_division_id == division_id)
    if department_id:
        query = query.filter(Request.assigned_department_id == department_id)
        
    total = query.count()
    if total == 0:
        return 100.0
        
    # SLA Compliance
    compliant = query.filter(
        Request.status == RequestStatus.COMPLETED,
        Request.actual_completion_time <= Request.sla_completion_deadline
    ).count()
    
    completed = query.filter(Request.status == RequestStatus.COMPLETED).count()
    
    if completed == 0:
        return 100.0
        
    return (compliant / completed) * 100.0

def _calculate_satisfaction_score(db: Session, division_id, department_id, start, end):
    query = db.query(func.avg(CustomerSatisfaction.overall_score)).join(Request)
    query = query.filter(Request.created_at >= start, Request.created_at <= end)
    
    if division_id:
        query = query.filter(Request.assigned_division_id == division_id)
    if department_id:
        query = query.filter(Request.assigned_department_id == department_id)
        
    avg_rating = query.scalar()
    
    if not avg_rating:
        return 100.0 # Default if no ratings
        
    # Convert 1-5 scale to 0-100
    # 1=0, 2=25, 3=50, 4=75, 5=100
    return (float(avg_rating) - 1) * 25.0

def _get_rating_label(score):
    if score >= 90: return "OUTSTANDING"
    if score >= 80: return "VERY_GOOD"
    if score >= 70: return "GOOD"
    if score >= 60: return "NEEDS_IMPROVEMENT"
    return "UNSATISFACTORY"
