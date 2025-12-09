"""
SLA Utilities for Tebita M&E System
Auto-calculates SLA deadlines and tracks compliance based on policy lookup.
Now supports activity-specific SLA policies from database.
"""
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models import Priority, ResourceType, ActivityType, Request, RequestStatus, SLAPolicy


# Legacy SLA Configuration (Fallback if no policy found)
SLA_RESPONSE_HOURS = {
    Priority.HIGH: 4,      # 4 hours for high priority
    Priority.MEDIUM: 24,   # 24 hours for medium priority
    Priority.LOW: 48,      # 48 hours for low priority
}

SLA_COMPLETION_HOURS = {
    # Completion time by resource type (from organizational document)
    ResourceType.FLEET: 24,          # 24 hours for fleet requests
    ResourceType.ICT: 48,            # 48 hours for ICT support
    ResourceType.HR: 120,            # 5 days for HR deployment
    ResourceType.FINANCE: 168,       # 7 days for finance processing
    ResourceType.LOGISTICS: 72,      # 3 days for logistics
    ResourceType.FACILITIES: 72,     # 3 days for facilities
    ResourceType.GENERAL: 96,        # 4 days for general requests
}


def get_sla_policy(
    db: Session,
    resource_type: ResourceType,
    activity_type: Optional[ActivityType],
    priority: Priority,
    division_id: Optional[int] = None,
    department_id: Optional[int] = None
) -> Optional[SLAPolicy]:
    """
    Lookup SLA policy from database with cascading specificity.
    
    Lookup order (most specific to least specific):
    1. Division + Department + Resource + Activity + Priority
    2. Division + Resource + Activity + Priority
    3. Resource + Activity + Priority
    4. Resource + Priority (activity=NULL)
    5. NULL (returns None, use fallback)
    
    Args:
        db: Database session
        resource_type: Type of resource
        activity_type: Specific activity (can be None)
        priority: Priority level
        division_id: Optional division ID
        department_id: Optional department ID
        
    Returns:
        SLAPolicy object or None if no policy found
    """
    # Build query filters in order of specificity
    query_attempts = []
    
    # Attempt 1: Most specific - Division + Department + Resource + Activity + Priority
    if division_id and department_id and activity_type:
        query_attempts.append([
            SLAPolicy.division_id == division_id,
            SLAPolicy.department_id == department_id,
            SLAPolicy.resource_type == resource_type,
            SLAPolicy.activity_type == activity_type,
            SLAPolicy.priority == priority,
            SLAPolicy.is_active == True
        ])
    
    # Attempt 2: Division + Resource + Activity + Priority
    if division_id and activity_type:
        query_attempts.append([
            SLAPolicy.division_id == division_id,
            SLAPolicy.department_id.is_(None),
            SLAPolicy.resource_type == resource_type,
            SLAPolicy.activity_type == activity_type,
            SLAPolicy.priority == priority,
            SLAPolicy.is_active == True
        ])
    
    # Attempt 3: Resource + Activity + Priority (global policy)
    if activity_type:
        query_attempts.append([
            SLAPolicy.division_id.is_(None),
            SLAPolicy.department_id.is_(None),
            SLAPolicy.resource_type == resource_type,
            SLAPolicy.activity_type == activity_type,
            SLAPolicy.priority == priority,
            SLAPolicy.is_active == True
        ])
    
    # Attempt 4: Resource + Priority only (activity=NULL, global policy)
    query_attempts.append([
        SLAPolicy.division_id.is_(None),
        SLAPolicy.department_id.is_(None),
        SLAPolicy.resource_type == resource_type,
        SLAPolicy.activity_type.is_(None),
        SLAPolicy.priority == priority,
        SLAPolicy.is_active == True
    ])
    
    # Try each query in order, return first match
    for filters in query_attempts:
        policy = db.query(SLAPolicy).filter(*filters).first()
        if policy:
            return policy
    
    return None



def calculate_sla_deadlines(
    request_created_at: datetime,
    priority: Priority,
    resource_type: ResourceType
) -> Tuple[datetime, datetime]:
    """
    Calculate SLA response and completion deadlines.
    
    Args:
        request_created_at: When the request was created
        priority: Request priority level
        resource_type: Type of shared resource
        
    Returns:
        Tuple of (response_deadline, completion_deadline)
    """
    response_hours = SLA_RESPONSE_HOURS.get(priority, 24)
    completion_hours = SLA_COMPLETION_HOURS.get(resource_type, 96)
    
    response_deadline = request_created_at + timedelta(hours=response_hours)
    completion_deadline = request_created_at + timedelta(hours=completion_hours)
    
    return response_deadline, completion_deadline


def check_sla_compliance(request: Request) -> Dict:
    """
    Check if a request met its SLA targets.
    
    Args:
        request: Request object
        
    Returns:
        Dictionary with compliance status and delay calculations
    """
    now = datetime.utcnow()
    
    # Response compliance
    response_met = None
    response_delay_hours = None
    if request.actual_response_time and request.sla_response_deadline:
        response_met = request.actual_response_time <= request.sla_response_deadline
        response_delay_hours = (
            request.actual_response_time - request.sla_response_deadline
        ).total_seconds() / 3600
    
    # Completion compliance
    completion_met = None
    completion_delay_hours = None
    if request.actual_completion_time and request.sla_completion_deadline:
        completion_met = request.actual_completion_time <= request.sla_completion_deadline
        completion_delay_hours = (
            request.actual_completion_time - request.sla_completion_deadline
        ).total_seconds() / 3600
    
    # Overall SLA met (both response AND completion)
    sla_met = (response_met and completion_met) if (response_met is not None and completion_met is not None) else None
    
    return {
        'response_met': response_met,
        'completion_met': completion_met,
        'sla_met': sla_met,
        'response_delay_hours': response_delay_hours,
        'completion_delay_hours': completion_delay_hours,
        'response_deadline': request.sla_response_deadline,
        'completion_deadline': request.sla_completion_deadline,
    }


def get_sla_status(request: Request) -> str:
    """
    Get current SLA status for an in-progress request.
    
    Args:
        request: Request object
        
    Returns:
        Status string: 'ON_TRACK', 'AT_RISK_50', 'AT_RISK_80', 'OVERDUE', 'COMPLETED_ON_TIME', 'COMPLETED_LATE'
    """
    now = datetime.utcnow()
    
    # If completed, check if it was on time
    if request.status == RequestStatus.COMPLETED:
        compliance = check_sla_compliance(request)
        return 'COMPLETED_ON_TIME' if compliance['sla_met'] else 'COMPLETED_LATE'
    
    # For in-progress requests, check against completion deadline
    if not request.sla_completion_deadline:
        return 'NO_SLA'
    
    if now > request.sla_completion_deadline:
        return 'OVERDUE'
    
    # Calculate time elapsed percentage
    total_time = (request.sla_completion_deadline - request.created_at).total_seconds()
    elapsed_time = (now - request.created_at).total_seconds()
    percent_elapsed = (elapsed_time / total_time * 100) if total_time > 0 else 0
    
    if percent_elapsed >= 80:
        return 'AT_RISK_80'
    elif percent_elapsed >= 50:
        return 'AT_RISK_50'
    else:
        return 'ON_TRACK'


def calculate_sla_compliance_rate(
    requests: list,
    division_id: int = None,
    date_range: Tuple[datetime, datetime] = None
) -> float:
    """
    Calculate SLA compliance rate for a set of requests.
    
    Args:
        requests: List of Request objects
        division_id: Optional division filter
        date_range: Optional (start_date, end_date) tuple
        
    Returns:
        Compliance rate as percentage (0-100)
    """
    completed_requests = [
        r for r in requests 
        if r.status == RequestStatus.COMPLETED
    ]
    
    if not completed_requests:
        return 0.0
    
    on_time_count = sum(
        1 for r in completed_requests 
        if check_sla_compliance(r)['sla_met']
    )
    
    return (on_time_count / len(completed_requests)) * 100


def get_delay_reason_template(resource_type: ResourceType) -> str:
    """
    Get suggested delay reason template based on resource type.
    
    Args:
        resource_type: Type of shared resource
        
    Returns:
        Template string for delay explanation
    """
    templates = {
        ResourceType.FLEET: "Vehicle unavailable / Driver shortage / Breakdown / Fuel delay",
        ResourceType.HR: "Candidate not found / Interview delays / Documentation incomplete",
        ResourceType.FINANCE: "Missing documents / Approval delays / Budget constraints",
        ResourceType.ICT: "Parts unavailable / System complexity / Escalation required",
        ResourceType.LOGISTICS: "Stock unavailable / Supplier delay / Transport issues",
        ResourceType.FACILITIES: "Contractor unavailable / Material delay / Weather conditions",
        ResourceType.GENERAL: "Unforeseen circumstances / Resource constraints / Approval delays",
    }
    
    return templates.get(resource_type, "Please specify reason for delay")
