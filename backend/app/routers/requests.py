import csv
import io
from datetime import datetime
from typing import List
from pydantic import Field

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..auth import get_current_active_user
from ..models import (
    Request,
    RequestItem,
    RequestWorkflow,
    RequestActivityLog,
    RequestActivityAction,
    User,
    UserRole,
    RequestStatus,
    WorkflowStep,
)
from .. import schemas
from ..services.sla_calculator import calculate_deadlines  # NEW: Import SLA service
from ..services.notification_service import send_user_notification
from ..services.access_control import apply_role_based_filtering

router = APIRouter(prefix="/requests", tags=["requests"])


def generate_request_id(db: Session, request_type: str) -> str:
    """Generate unique request ID in format REQ-DEPT-DATE-XXX"""
    from datetime import datetime
    
    date_str = datetime.now().strftime("%Y%m%d")
    dept_code = request_type[:3].upper()
    prefix = f"REQ-{dept_code}-{date_str}-"
    
    # Get count of requests today with this specific prefix
    # We filter by the ID string itself to handle multiple request types sharing the same prefix
    count = db.query(Request).filter(
        Request.request_id.like(f"{prefix}%")
    ).count()
    
    sequence = str(count + 1).zfill(3)
    return f"{prefix}{sequence}"


@router.get("/", response_model=List[schemas.RequestRead])
async def get_requests(
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get requests based on user role"""
    from sqlalchemy.orm import joinedload
    
    query = db.query(Request).options(
        joinedload(Request.requester),
        joinedload(Request.requester_division),
        joinedload(Request.requester_department),
        joinedload(Request.requester_subdepartment),
        joinedload(Request.assigned_division),
        joinedload(Request.assigned_department),
        joinedload(Request.assigned_subdepartment)
    )

    # Role-based filtering
    query = apply_role_based_filtering(query, current_user)

    if status:
        query = query.filter(Request.status == status)

    requests = query.order_by(Request.created_at.desc()).all()
    return requests


@router.get("/incoming", response_model=List[schemas.RequestRead])
async def get_incoming_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Requests assigned to the current user's department/division/user"""
    # Allow access if user has department OR division OR is Admin
    is_admin = "ADMIN" in str(current_user.role)
    has_dept = current_user.department_id is not None
    has_div = current_user.division_id is not None
    
    if not has_dept and not has_div and not is_admin:
        raise HTTPException(status_code=403, detail="Department or Division membership required")

    from sqlalchemy import or_, and_
    
    # Base filters that always apply
    filters = [
        Request.assigned_to_user_id == current_user.id  # Directly assigned to user
    ]
    
    # Role-specific "Incoming" logic
    if current_user.role == UserRole.DIVISION_MANAGER:
        # Show requests assigned directly to the Division (from any division)
        filters.append(
            and_(
                Request.assigned_division_id == current_user.division_id,
                Request.assigned_department_id.is_(None)
            )
        )
    elif current_user.role == UserRole.DEPARTMENT_HEAD:
        # Show requests assigned directly to the Department (from any department)
        filters.append(
            and_(
                Request.assigned_department_id == current_user.department_id,
                Request.assigned_subdepartment_id.is_(None)
            )
        )
    elif current_user.subdepartment_id:
        # Staff: Show requests assigned to their Sub-Department
        filters.append(Request.assigned_subdepartment_id == current_user.subdepartment_id)
    else:
        # Fallback for staff without subdept (shouldn't happen ideally)
        filters.append(Request.assigned_to_user_id == current_user.id)
    
    
    query = db.query(Request).filter(or_(*filters))
    
    # Filter for active/pending requests AND completed ones (so they show up in the completed tab)
    query = query.filter(Request.status.in_([
        RequestStatus.PENDING, 
        RequestStatus.IN_PROGRESS,
        RequestStatus.COMPLETED
    ]))
    
    return query.order_by(Request.submitted_at.desc()).all()


@router.get("/sent", response_model=List[schemas.RequestRead])
async def get_sent_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Requests created by the current user"""
    return (
        db.query(Request)
        .filter(Request.requester_id == current_user.id)
        .order_by(Request.created_at.desc())
        .all()
    )


@router.post("/", response_model=schemas.RequestRead, status_code=status.HTTP_201_CREATED)
async def create_request(
    request_in: schemas.RequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new request with auto-calculated SLA deadlines"""
    # 1. Restriction: Admins cannot create requests
    if current_user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrators cannot create requests. Please use a standard user account."
        )

    # 2. Restriction: Self-requests (sending to own unit)
    # Only block if sending to the EXACT SAME organizational level
    
    # Check if sending to same division
    if request_in.assigned_division_id == current_user.division_id:
        # Check if sending to same department (both must be non-None to compare)
        if (request_in.assigned_department_id is not None and 
            current_user.department_id is not None and
            request_in.assigned_department_id == current_user.department_id):
            
            # Check Sub-Department level (if applicable)
            # If user has subdept, and request is to same subdept -> BLOCK
            if (current_user.subdepartment_id is not None and
                request_in.assigned_subdepartment_id is not None and
                request_in.assigned_subdepartment_id == current_user.subdepartment_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You cannot send a request to your own Sub-Department."
                )
            
            # If user has NO subdept (Dept Head), and request is to same Dept (and no specific subdept) -> BLOCK
            # (Sending to a specific subdept within own Dept is allowed for Dept Heads)
            if (current_user.subdepartment_id is None and 
                request_in.assigned_subdepartment_id is None):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You cannot send a request to your own Department."
                )
        
        # If sending to same division but NO department specified (division-level request)
        # And user is a Division Manager (has no dept) -> BLOCK
        elif (request_in.assigned_department_id is None and 
              current_user.department_id is None and
              current_user.role == UserRole.DIVISION_MANAGER):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot send a request to your own Division."
            )

    # Generate request ID
    request_id = generate_request_id(db, request_in.request_type)
    
    # Create request object
    request_data = request_in.model_dump(exclude={'items'})
    request = Request(
        **request_data,
        request_id=request_id,
        requester_id=current_user.id,
        status=RequestStatus.PENDING,
        submitted_at=datetime.utcnow()
    )
    
    # Calculate SLA deadlines using policy-based system
    calculate_deadlines(request, db)
    
    db.add(request)
    db.flush()  # Get request.id without committing
    
    # Add request items
    for item_data in request_in.items:
        item = RequestItem(**item_data.model_dump(), request_id=request.id)
        db.add(item)
    
    # Add workflow entry
    workflow = RequestWorkflow(
        request_id=request.id,
        step=WorkflowStep.SUBMITTED,
        performed_by_user_id=current_user.id,
        notes="Request submitted"
    )
    db.add(workflow)
    _log_request_activity(
        db,
        request=request,
        action=RequestActivityAction.SENT,
        performed_by=current_user,
        details=f"Request sent to division {request.assigned_division_id}"
    )
    
    db.commit()
    db.refresh(request)
    
    # Notify assigned user (if any) about the new request
    try:
        if request.assigned_to_user_id:
            await send_user_notification(
                str(request.assigned_to_user_id),
                {"type": "request_created", "request_id": request.request_id, "status": str(request.status)}
            )
    except Exception:
        pass
    
    # Send email notification for HIGH priority requests
    # Send email notification (for all priorities)
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Attempting to send email for request {request.request_id}")
        
        from ..services.email_service import email_service
        
        # Get assigned users
        assigned_users = []
        if request.assigned_to_user_id:
            assigned_user = db.get(User, request.assigned_to_user_id)
            if assigned_user:
                assigned_users.append(assigned_user)
        elif request.assigned_subdepartment_id:
            # Get all users in subdepartment  
            assigned_users = db.query(User).filter(
                User.subdepartment_id == request.assigned_subdepartment_id
            ).all()
        elif request.assigned_department_id:
            # Get department head
            assigned_users = db.query(User).filter(
                User.department_id == request.assigned_department_id,
                User.role.in_([UserRole.DEPARTMENT_HEAD, UserRole.DIVISION_MANAGER])
            ).all()
        
        if assigned_users:
            logger.info(f"Found {len(assigned_users)} assigned users, sending email...")
            email_service.send_request_notification(db, request, assigned_users)
        else:
            logger.warning(f"No assigned users found for request {request.request_id}")
    except Exception as e:
        # Non-fatal: email failures shouldn't break request creation
        import traceback
        print(f"⚠️ Email notification failed (non-blocking): {e}")
        print(traceback.format_exc())
    
    return request



def _ensure_user_is_assignee(request: Request, user: User):
    """Ensure user can act on this request - must EXACTLY match incoming requests query logic"""
    # Admin can always act
    if user.role == "ADMIN":
        return

    # Division Manager can act on requests in their division
    if user.role == "DIVISION_MANAGER":
        if request.assigned_division_id == user.division_id:
            return
        raise HTTPException(status_code=403, detail="Not authorized for this division")

    # Check direct assignment to user
    if request.assigned_to_user_id == user.id:
        return

    # If user has subdepartment, only allow if request is assigned to that subdepartment
    if user.subdepartment_id:
        if request.assigned_subdepartment_id == user.subdepartment_id:
            return
    else:
        # If user has NO subdepartment, allow department-wide requests
        # (only if request is NOT assigned to a specific subdepartment)
        if (request.assigned_department_id == user.department_id and 
            request.assigned_subdepartment_id is None):
            return

    raise HTTPException(status_code=403, detail="Not authorized to act on this request")


def _ensure_user_has_request_access(request: Request, user: User):
    if not user.department_id:
        raise HTTPException(status_code=403, detail="Department membership required")

    has_access = (
        (request.requester_department_id and request.requester_department_id == user.department_id) or
        (request.assigned_department_id and request.assigned_department_id == user.department_id) or
        request.assigned_to_user_id == user.id or
        request.requester_id == user.id
    )
    if not has_access:
        raise HTTPException(status_code=403, detail="Not authorized")


def _log_request_activity(
    db: Session,
    *,
    request: Request,
    action: RequestActivityAction,
    performed_by: User,
    details: str = ""
):
    # Determine target IDs safely
    target_dept_id = None
    if action == RequestActivityAction.SENT:
        target_dept_id = request.assigned_department_id
    else:
        target_dept_id = request.requester_department_id

    target_div_id = None
    if action == RequestActivityAction.SENT:
        target_div_id = request.assigned_division_id
    else:
        target_div_id = request.requester_division_id

    log = RequestActivityLog(
        request_id=request.id,
        action=action,
        performed_by_user_id=performed_by.id,
        performed_by_department_id=performed_by.department_id,
        performed_by_division_id=performed_by.division_id,
        target_department_id=target_dept_id,
        target_division_id=target_div_id,
        details=details or None,
    )
    db.add(log)


@router.post("/{request_id}/acknowledge", response_model=schemas.RequestRead)
async def acknowledge_request(
    request_id: int,
    notes: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    print(f"🔵 Acknowledge request {request_id} by user {current_user.username} (ID: {current_user.id})")
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    print(f"   Request found: {request.request_id}")
    print(f"   Assigned to user: {request.assigned_to_user_id}")
    print(f"   Assigned to dept: {request.assigned_department_id}")
    print(f"   Assigned to subdept: {request.assigned_subdepartment_id}")
    print(f"   Current user dept: {current_user.department_id}")
    print(f"   Current user subdept: {current_user.subdepartment_id}")
    
    _ensure_user_is_assignee(request, current_user)
    print(f"   ✅ Authorization passed")

    if request.acknowledged_at:
        print(f"   ❌ Already acknowledged at {request.acknowledged_at}")
        raise HTTPException(status_code=400, detail="Request already acknowledged")

    # Update request status and timestamps
    request.acknowledged_at = datetime.utcnow()
    request.actual_response_time = datetime.utcnow()  # NEW: Log actual response time
    request.acknowledged_by_user_id = current_user.id
    request.status = RequestStatus.IN_PROGRESS  # Move to "In Progress" section

    workflow = RequestWorkflow(
        request_id=request.id,
        step=WorkflowStep.RECEIVED,
        performed_by_user_id=current_user.id,
        notes=notes or "Request acknowledged"
    )
    db.add(workflow)
    _log_request_activity(
        db,
        request=request,
        action=RequestActivityAction.RECEIVED,
        performed_by=current_user,
        details=notes
    )
    db.commit()
    db.refresh(request)
    print(f"   ✅ Request acknowledged successfully!")
    return request


@router.post("/{request_id}/complete", response_model=schemas.RequestRead)
async def complete_request(
    request_id: int,
    notes: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a request as completed"""
    print(f"🟢 Complete request {request_id} by user {current_user.username}")
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    _ensure_user_is_assignee(request, current_user)

    if not request.acknowledged_at:
        raise HTTPException(status_code=400, detail="Request must be acknowledged first")

    if request.completed_at:
        raise HTTPException(status_code=400, detail="Request already completed")

    # Mark as completed
    request.completed_at = datetime.utcnow()
    request.actual_completion_time = datetime.utcnow()  # NEW: Log actual completion time
    request.status = RequestStatus.COMPLETED

    workflow = RequestWorkflow(
        request_id=request.id,
        step=WorkflowStep.COMPLETED,
        performed_by_user_id=current_user.id,
        notes=notes or "Request completed"
    )
    db.add(workflow)
    
    db.commit()
    db.refresh(request)
    print(f"   ✅ Request completed successfully!")
    return request


@router.post("/{request_id}/validate-completion", response_model=schemas.RequestRead)
async def validate_request_completion(
    request_id: int,
    notes: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Only the requester or admin can validate completion
    if current_user.role != "ADMIN" and request.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to act on this request")

    if request.completion_validated_at:
        raise HTTPException(status_code=400, detail="Completion already validated")

    request.completion_validated_at = datetime.utcnow()
    request.completion_validated_by_user_id = current_user.id
    request.status = RequestStatus.COMPLETED
    request.completed_at = request.completed_at or datetime.utcnow()
    request.actual_completion_time = datetime.utcnow()

    workflow = RequestWorkflow(
        request_id=request.id,
        step=WorkflowStep.VALIDATED,
        performed_by_user_id=current_user.id,
        notes=notes or "Completion validated"
    )
    db.add(workflow)
    db.commit()
    db.refresh(request)
    return request


@router.get("/{request_id}", response_model=schemas.RequestRead)
async def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific request"""
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check access permissions - user can view if they are:
    # 1. The requester (created the request)
    # 2. Assigned to the request (personally)
    # 3. In the requester's organizational hierarchy (division/department/subdepartment)
    # 4. In the assigned organizational hierarchy (division/department/subdepartment)
    
    is_requester = request.requester_id == current_user.id
    is_assigned_user = request.assigned_to_user_id == current_user.id
    
    # Check if user is in requester's hierarchy
    in_requester_division = (request.requester_division_id and 
                             current_user.division_id and
                             request.requester_division_id == current_user.division_id)
    in_requester_department = (request.requester_department_id and 
                               current_user.department_id and
                               request.requester_department_id == current_user.department_id)
    in_requester_subdepartment = (request.requester_subdepartment_id and 
                                  current_user.subdepartment_id and
                                  request.requester_subdepartment_id == current_user.subdepartment_id)
    
    # Check if user is in assigned hierarchy
    in_assigned_division = (request.assigned_division_id and 
                           current_user.division_id and
                           request.assigned_division_id == current_user.division_id)
    in_assigned_department = (request.assigned_department_id and 
                             current_user.department_id and
                             request.assigned_department_id == current_user.department_id)
    in_assigned_subdepartment = (request.assigned_subdepartment_id and 
                                current_user.subdepartment_id and
                                request.assigned_subdepartment_id == current_user.subdepartment_id)
    
    has_access = (is_requester or is_assigned_user or 
                 in_requester_division or in_requester_department or in_requester_subdepartment or
                 in_assigned_division or in_assigned_department or in_assigned_subdepartment or
                 current_user.role == UserRole.ADMIN)
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Not authorized to view this request")
    
    return request


@router.get("/activity/export")
async def export_request_activity_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only administrators can export activity logs")

    logs = (
        db.query(RequestActivityLog)
        .options(
            joinedload(RequestActivityLog.request),
            joinedload(RequestActivityLog.performed_by),
            joinedload(RequestActivityLog.performed_department),
            joinedload(RequestActivityLog.performed_division),
            joinedload(RequestActivityLog.target_department),
            joinedload(RequestActivityLog.target_division),
        )
        .order_by(RequestActivityLog.created_at.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Log ID",
        "Request Number",
        "Action",
        "Performed By",
        "Performed Dept",
        "Performed Division",
        "Target Dept",
        "Target Division",
        "Details",
        "Timestamp",
    ])

    for log in logs:
        writer.writerow([
            log.id,
            log.request.request_id if log.request else "",
            log.action.value,
            log.performed_by.full_name if log.performed_by else "",
            log.performed_department.name if log.performed_department else "",
            log.performed_division.name if log.performed_division else "",
            log.target_department.name if log.target_department else "",
            log.target_division.name if log.target_division else "",
            log.details or "",
            log.created_at.isoformat() if log.created_at else "",
        ])

    output.seek(0)
    filename = f"request_activity_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    content = output.getvalue().encode("utf-8")
    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.patch("/{request_id}/status", response_model=schemas.RequestRead)
async def update_request_status(
    request_id: int,
    status_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update request status"""
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    new_status = status_update.get('status')
    notes = status_update.get('notes', '')
    
    # Update request status
    old_status = request.status
    request.status = RequestStatus(new_status)
    
    # Update timestamps based on status
    if new_status == RequestStatus.APPROVED:
        request.approved_at = datetime.utcnow()
        request.approved_by_user_id = current_user.id
    elif new_status == RequestStatus.IN_PROGRESS:
        request.started_at = datetime.utcnow()
        # NEW: Track actual response time on first status change to IN_PROGRESS
        if not request.actual_response_time:
            request.actual_response_time = datetime.utcnow()
    elif new_status == RequestStatus.COMPLETED:
        request.completed_at = datetime.utcnow()
        request.actual_completion_time = datetime.utcnow()
    
    # Add workflow entry
    workflow_step_map = {
        RequestStatus.APPROVAL_PENDING: WorkflowStep.APPROVAL_PENDING,
        RequestStatus.APPROVED: WorkflowStep.APPROVED,
        RequestStatus.REJECTED: WorkflowStep.REJECTED,
        RequestStatus.IN_PROGRESS: WorkflowStep.DEPLOYED,
        RequestStatus.COMPLETED: WorkflowStep.COMPLETED,
    }
    
    workflow = RequestWorkflow(
        request_id=request.id,
        step=workflow_step_map.get(RequestStatus(new_status), WorkflowStep.APPROVAL_PENDING),
        performed_by_user_id=current_user.id,
        notes=notes or f"Status changed from {old_status} to {new_status}"
    )
    db.add(workflow)
    
    db.commit()
    db.refresh(request)
    return request


@router.post("/{request_id}/approve", response_model=schemas.RequestRead)
async def approve_request(
    request_id: int,
    notes: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Approve a request (Admin or authorized staff)"""
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request.status != RequestStatus.PENDING and request.status != RequestStatus.APPROVAL_PENDING:
        raise HTTPException(status_code=400, detail="Request cannot be approved in current status")
    
    request.status = RequestStatus.APPROVED
    request.approved_at = datetime.utcnow()
    request.approved_by_user_id = current_user.id
    
    # Add workflow entry
    workflow = RequestWorkflow(
        request_id=request.id,
        step=WorkflowStep.APPROVED,
        performed_by_user_id=current_user.id,
        notes=notes or "Request approved"
    )
    db.add(workflow)
    
    db.commit()
    db.refresh(request)
    return request


@router.post("/{request_id}/reject", response_model=schemas.RequestRead)
async def reject_request(
    request_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reject a request"""
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request.status = RequestStatus.REJECTED
    
    # Add workflow entry
    workflow = RequestWorkflow(
        request_id=request.id,
        step=WorkflowStep.REJECTED,
        performed_by_user_id=current_user.id,
        notes=f"Request rejected: {reason}"
    )
    db.add(workflow)
    
    db.commit()
    db.refresh(request)
    return request

# NEW ENDPOINT: Satisfaction Rating Submission
@router.post("/{request_id}/satisfaction", response_model=schemas.RequestRead)
async def submit_satisfaction_rating(
    request_id: int,
    satisfaction_data: schemas.SatisfactionSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Submit satisfaction rating for a completed request (requester only)"""
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Only requester can submit satisfaction rating
    if request.requester_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Only the requester can submit satisfaction rating"
        )
    
    # Request must be completed
    if request.status != RequestStatus.COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail="Can only rate completed requests"
        )
    
    # Update satisfaction fields
    request.satisfaction_rating = satisfaction_data.rating
    request.satisfaction_comment = satisfaction_data.comment
    
    db.commit()
    db.refresh(request)
    return request


# NEW ENDPOINT: Get SLA Status for Request
@router.get("/{request_id}/sla-status")
async def get_request_sla_status(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current SLA status and compliance info for a request"""
    from ..sla_utils import get_sla_status, check_sla_compliance
    
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Get SLA status
    sla_status = get_sla_status(request)
    
    # Get compliance details if completed
    compliance_details = None
    if request.status == RequestStatus.COMPLETED:
        compliance_details = check_sla_compliance(request)
    
    return {
        "request_id": request.request_id,
        "status": request.status,
        "sla_status": sla_status,
        "sla_response_deadline": request.sla_response_deadline,
        "sla_completion_deadline": request.sla_completion_deadline,
        "actual_response_time": request.actual_response_time,
        "actual_completion_time": request.actual_completion_time,
        "compliance_details": compliance_details
    }
