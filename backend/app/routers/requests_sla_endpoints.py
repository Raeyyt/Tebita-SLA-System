
# NEW ENDPOINT: Satisfaction Rating Submission
@router.post("/{request_id}/satisfaction", response_model=schemas.RequestRead)
async def submit_satisfaction_rating(
    request_id: int,
    rating: int = Field(ge=1, le=5),
    comment: str = None,
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
    request.satisfaction_rating = rating
    request.satisfaction_comment = comment
    
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
