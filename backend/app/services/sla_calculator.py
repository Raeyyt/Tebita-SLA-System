from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models import Request, RequestStatus
from .sla_policy import get_sla_standards
from app.sla_utils import get_sla_policy

def calculate_deadlines(request: Request, db: Session = None):
    """
    Calculates and sets the SLA deadlines (response and completion)
    based on the request's activity type, resource type, and priority.
    
    Now supports policy-based lookup from sla_policies table.
    Falls back to legacy standards if no policy found or db not provided.
    """
    if not request.created_at:
        return
    
    response_hours = None
    resolution_hours = None
    
    # Try policy-based lookup if db session provided
    if db and hasattr(request, 'activity_type') and request.activity_type:
        policy = get_sla_policy(
            db=db,
            resource_type=request.resource_type,
            activity_type=request.activity_type,
            priority=request.priority,
            division_id=request.assigned_division_id,
            department_id=request.assigned_department_id
        )
        
        if policy:
            response_hours = policy.response_time_hours
            resolution_hours = policy.completion_time_hours
    
    # Fallback to legacy standards if no policy found
    if response_hours is None or resolution_hours is None:
        standards = get_sla_standards(request.resource_type, request.priority)
        if response_hours is None:
            response_hours = standards["response"]
        if resolution_hours is None:
            resolution_hours = standards["resolution"]
    
    # Store SLA hours
    request.sla_response_time_hours = int(response_hours) if response_hours >= 1 else 1  # Min 1 hour, store as int
    request.sla_completion_time_hours = int(resolution_hours)
    
    # Calculate deadlines from created_at
    request.sla_response_deadline = request.created_at + timedelta(hours=response_hours)
    request.sla_completion_deadline = request.created_at + timedelta(hours=resolution_hours)


def calculate_sla_status(request: Request) -> dict:
    """
    Determines the current SLA status of a request.
    Returns a dict with 'status' (BREACHED, WARNING, ON_TRACK) and 'time_remaining_str'.
    """
    now = datetime.now(timezone.utc)
    
    # 1. Check Response SLA (if not yet acknowledged)
    if not request.acknowledged_at:
        deadline = request.sla_response_deadline
        if not deadline:
            return {"status": "UNKNOWN", "message": "No deadline set"}
            
        # Ensure deadline is timezone-aware
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
            
        if now > deadline:
            return {"status": "BREACHED", "message": "Response overdue"}
        
        time_left = deadline - now
        if time_left < timedelta(hours=1):
            return {"status": "WARNING", "message": "Response due soon"}
            
        return {"status": "ON_TRACK", "message": "Waiting for response"}

    # 2. Check Resolution SLA (if not completed)
    if request.status not in [RequestStatus.COMPLETED, RequestStatus.REJECTED, RequestStatus.CANCELLED]:
        deadline = request.sla_completion_deadline
        if not deadline:
            return {"status": "UNKNOWN", "message": "No deadline set"}
            
        # Ensure deadline is timezone-aware
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
            
        if now > deadline:
            return {"status": "BREACHED", "message": "Resolution overdue"}
            
        time_left = deadline - now
        total_duration = timedelta(hours=request.sla_completion_time_hours or 24)
        
        # Warning if < 20% time remaining
        if time_left < (total_duration * 0.2):
             return {"status": "WARNING", "message": "Resolution due soon"}
             
        return {"status": "ON_TRACK", "message": "In progress"}

    # 3. Completed
    return {"status": "COMPLETED", "message": "Request completed"}
