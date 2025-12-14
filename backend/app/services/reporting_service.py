import csv
import io
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from sqlalchemy.orm import Session, joinedload
from app.models import Request
from app.services.sla_calculator import calculate_sla_status

def generate_scorecard_pdf(scorecard_data: dict, division_name: str, period: str) -> io.BytesIO:
    """
    Generates a PDF scorecard in memory.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = styles['Title']
    elements.append(Paragraph(f"Department Balanced Scorecard", title_style))
    elements.append(Paragraph(f"Division: {division_name}", styles['Heading2']))
    elements.append(Paragraph(f"Period: {period}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Overall Score
    score_style = ParagraphStyle(
        'Score',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.blue,
        alignment=1 # Center
    )
    elements.append(Paragraph(f"Overall Score: {scorecard_data['total_score']}", score_style))
    elements.append(Paragraph(f"Rating: {scorecard_data['rating']}", styles['Heading3']))
    elements.append(Spacer(1, 20))
    
    # Metrics Table
    data = [
        ['Dimension', 'Score', 'Weight', 'Weighted Score'],
        ['Service Efficiency', f"{scorecard_data['service_efficiency']}", '40%', f"{scorecard_data['service_efficiency'] * 0.4:.1f}"],
        ['Compliance', f"{scorecard_data['compliance']}", '20%', f"{scorecard_data['compliance'] * 0.2:.1f}"],
        ['Cost Optimization', f"{scorecard_data['cost_optimization']}", '20%', f"{scorecard_data['cost_optimization'] * 0.2:.1f}"],
        ['Customer Satisfaction', f"{scorecard_data['satisfaction']}", '20%', f"{scorecard_data['satisfaction'] * 0.2:.1f}"],
    ]
    
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def format_datetime_for_export(dt: datetime) -> str:
    """
    Formats a UTC datetime to EAT (UTC+3) string in 12-hour format.
    Format: MMM DD, YYYY, h:mm A
    Example: Dec 11, 2025, 2:09 PM
    """
    if not dt:
        return ""
    
    # Convert to EAT (UTC+3)
    eat_time = dt + timedelta(hours=3)
    
    # Format: MMM DD, YYYY, h:mm A
    # %b = Month abbr, %d = Day, %Y = Year, %I = 12h Hour, %M = Minute, %p = AM/PM
    return eat_time.strftime("%b %d, %Y, %I:%M %p").lstrip("0").replace(" 0", " ")

def generate_request_export_csv(db: Session, start_date: datetime, end_date: datetime) -> io.StringIO:
    """
    Generates a CSV export of requests in the given period.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Request ID', 'Type', 'Priority', 'Status', 
        'Sender Division', 'Sender Department', 'Sender Name',
        'Recipient Division', 'Recipient Department', 'Recipient Name',
        'Created At', 'Submitted At', 'Acknowledged At', 
        'Completed At', 'Validated At',
        'SLA Deadline', 'Actual Completion (Hrs)', 'SLA Status', 'Rejection Reason'
    ])
    
    # Data
    requests = db.query(Request).options(
        joinedload(Request.requester),
        joinedload(Request.requester_division),
        joinedload(Request.requester_department),
        joinedload(Request.assigned_to),
        joinedload(Request.assigned_division),
        joinedload(Request.assigned_department)
    ).filter(
        Request.created_at >= start_date,
        Request.created_at <= end_date
    ).all()
    
    for req in requests:
        # Calculate actual hours if completed
        actual_hours = ""
        if req.completed_at and req.created_at:
            actual_hours = f"{(req.completed_at - req.created_at).total_seconds() / 3600:.1f}"
            
        writer.writerow([
            req.request_id,
            req.request_type,
            req.priority,
            req.status,
            req.requester_division.name if req.requester_division else "",
            req.requester_department.name if req.requester_department else "",
            req.requester.full_name if req.requester else "",
            req.assigned_division.name if req.assigned_division else "",
            req.assigned_department.name if req.assigned_department else "",
            req.assigned_to.full_name if req.assigned_to else "Unassigned",
            format_datetime_for_export(req.created_at),
            format_datetime_for_export(req.submitted_at),
            format_datetime_for_export(req.acknowledged_at),
            format_datetime_for_export(req.completed_at),
            format_datetime_for_export(req.completion_validated_at),
            format_datetime_for_export(req.sla_completion_deadline),
            actual_hours,
            calculate_sla_status(req),
            req.rejection_reason or ""
        ])
        
    output.seek(0)
    return output
