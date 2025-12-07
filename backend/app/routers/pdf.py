"""PDF Generation Router for Tebita SLA System"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_active_user
from ..models import Request, User, Division, Department, UserRole
from ..services.pdf_generator import TEditaPDFGenerator

router = APIRouter(prefix="/api/requests", tags=["pdf"])


@router.get("/{request_id}/pdf")
async def generate_request_pdf(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate PDF for a specific request"""
    # Get request
    request = db.get(Request, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Enforce role-based access control - must EXACTLY match incoming requests query
    if current_user.role == "ADMIN":
        # Admin can see all PDFs
        pass
    elif current_user.role == "DIVISION_MANAGER":
        # Division managers see requests in their division
        if (request.requester_division_id != current_user.division_id and 
            request.assigned_division_id != current_user.division_id):
            raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role == "DEPARTMENT_HEAD":
        # Department heads see requests in their department
        if (request.requester_department_id != current_user.department_id and 
            request.assigned_department_id != current_user.department_id):
            raise HTTPException(status_code=403, detail="Not authorized")
    else:
        # SUB_DEPARTMENT_STAFF and others - use same logic as _ensure_user_is_assignee
        has_access = (
            request.requester_id == current_user.id or
            request.assigned_to_user_id == current_user.id
        )
        
        # If user has subdepartment, check subdepartment assignment
        if current_user.subdepartment_id:
            has_access = has_access or (request.assigned_subdepartment_id == current_user.subdepartment_id)
        else:
            # If no subdepartment, check department assignment (only for non-subdepartment requests)
            has_access = has_access or (
                request.assigned_department_id == current_user.department_id and
                request.assigned_subdepartment_id is None
            )
        
        if not has_access:
            raise HTTPException(status_code=403, detail="Not authorized")

    # Get related data
    requester_division = db.get(Division, request.requester_division_id) if request.requester_division_id else None
    assigned_division = db.get(Division, request.assigned_division_id) if request.assigned_division_id else None
    requester_dept = db.get(Department, request.requester_department_id) if request.requester_department_id else None
    assigned_dept = db.get(Department, request.assigned_department_id) if request.assigned_department_id else None
    
    # Get subdepartments
    from ..models import SubDepartment
    requester_subdept = db.get(SubDepartment, request.requester_subdepartment_id) if request.requester_subdepartment_id else None
    assigned_subdept = db.get(SubDepartment, request.assigned_subdepartment_id) if request.assigned_subdepartment_id else None

    # Prepare data for PDF
    pdf_data = {
        'request_id': request.request_id,
        'date': request.created_at.strftime('%Y-%m-%d') if request.created_at else '',
        'senderDepartment': requester_dept.name if requester_dept else 'N/A',
        'senderDivision': requester_division.name if requester_division else 'N/A',
        'senderSubDepartment': requester_subdept.name if requester_subdept else None,
        'receiverDepartment': assigned_dept.name if assigned_dept else 'N/A',
        'receiverDivision': assigned_division.name if assigned_division else 'N/A',
        'receiverSubDepartment': assigned_subdept.name if assigned_subdept else None,
        'requestType': request.request_type,
        'requestDescription': request.description,
        'priority': request.priority.value if request.priority else 'MEDIUM',
        'signedBy': current_user.full_name,
        'sender_email': request.requester.email if request.requester and request.requester.email else 'info@tebitambulance.com',
        'items': [
            {
                'item_description': item.item_description,
                'unit_price': item.unit_price,
                'quantity': item.quantity,
                'attachment_filename': item.attachment_filename,
            }
            for item in request.items
        ],
        'main_item_description': request.items[0].item_description if request.items else '',
        'item_files': [
            item.attachment_filename
            for item in request.items
            if item.attachment_filename
        ],
        'attachments': request.attachments or [],
        'company_location': 'https://maps.google.com/maps/place//data=!4m2!3m1!1s0x164b85001ee00be1:0xe1a1d67bd070ea7?entry=s&sa=X&ved=2ahUKEwiY2-Owj6aRAxUzUkEAHbpiHEMQ4kB6BAgVEAA&hl=en',
    }
    
    # Generate PDF
    generator = TEditaPDFGenerator()
    pdf_buffer = generator.generate_request_pdf(pdf_data)
    
    # Return PDF as streaming response
    return StreamingResponse(
        pdf_buffer,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'inline; filename="Request_{request.request_id}.pdf"'
        }
    )
