"""PDF Generation Service for Tebita SLA System - Odoo Style"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
import os

class TEditaPDFGenerator:
    """Generate professional Odoo-style PDFs for requests"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 20 * mm
        
    def generate_request_pdf(self, request_data: dict) -> BytesIO:
        """Generate PDF for a request matching the new design"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin * 2  # More space for footer
        )
        
        # Build PDF content
        story = []
        styles = getSampleStyleSheet()
        
        # Brand Colors
        COLOR_RED = colors.HexColor('#E63946')
        COLOR_BLUE = colors.HexColor('#1D3557')
        COLOR_GRAY_BG = colors.HexColor('#F8F9FA')
        COLOR_TEXT_GRAY = colors.HexColor('#6C757D')
        
        # Custom styles
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=COLOR_RED,
            leading=24,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        )
        
        subheader_style = ParagraphStyle(
            'CustomSubHeader',
            parent=styles['Heading2'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=4,
            fontName='Helvetica-Bold'
        )
        
        value_style = ParagraphStyle(
            'Value',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#495057'),
            leading=14
        )
        
        # 1. Header Section (Logo + REQUEST FORM)
        # We use a table to align Logo (Left) and Title (Right)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        logo_path = os.path.join(base_dir, 'assets', 'tebita-logo.png')
        logo_img = None
        if os.path.exists(logo_path):
            logo_img = Image(logo_path, width=70*mm, height=25*mm)
            logo_img.hAlign = 'LEFT'
        
        title_para = Paragraph("REQUEST<br/>FORM", header_style)
        
        header_data = [[logo_img if logo_img else "", title_para]]
        header_table = Table(header_data, colWidths=[100*mm, 70*mm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEBELOW', (0, 0), (-1, -1), 2, COLOR_RED),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 5*mm))
        
        # 2. Request Number
        req_no_style = ParagraphStyle('ReqNo', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=14, fontName='Helvetica-Bold')
        req_label_style = ParagraphStyle('ReqLabel', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=9, textColor=COLOR_TEXT_GRAY)
        
        req_no_data = [[
            Paragraph("Request NO.", req_label_style),
        ], [
            Paragraph(request_data.get('request_id', 'N/A'), req_no_style)
        ]]
        
        req_table = Table(req_no_data, colWidths=[170*mm])
        req_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_GRAY_BG),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(req_table)
        story.append(Spacer(1, 10*mm))
        
        # 3. Sender & Recipient (Side by Side)
        sender_content = [
            Paragraph("SENDER", subheader_style),
            Paragraph(f"<b>Division:</b> {request_data.get('senderDivision', 'N/A')}", value_style),
            Paragraph(f"<b>Department:</b> {request_data.get('senderDepartment', 'N/A')}", value_style),
            Paragraph(f"<b>Sub-Department:</b> {request_data.get('senderSubDepartment') or 'N/A'}", value_style),
        ]
        
        recipient_content = [
            Paragraph("RECIPIENT", subheader_style),
            Paragraph(f"<b>Division:</b> {request_data.get('receiverDivision', 'N/A')}", value_style),
            Paragraph(f"<b>Department:</b> {request_data.get('receiverDepartment', 'N/A')}", value_style),
            Paragraph(f"<b>Sub-Department:</b> {request_data.get('receiverSubDepartment') or 'N/A'}", value_style),
        ]
        
        sr_data = [[sender_content, recipient_content]]
        sr_table = Table(sr_data, colWidths=[85*mm, 85*mm])
        sr_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(sr_table)
        story.append(Spacer(1, 10*mm))
        
        # 4. Request Description
        story.append(Paragraph("REQUEST DESCRIPTION", subheader_style))
        desc_content = Paragraph(request_data.get('requestDescription', 'N/A'), value_style)
        
        desc_table = Table([[desc_content]], colWidths=[170*mm])
        desc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_GRAY_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]), 
        ]))
        story.append(desc_table)
        story.append(Spacer(1, 8*mm))
        
        # 5. Priority
        story.append(Paragraph("PRIORITY TYPE", subheader_style))
        priority = request_data.get('priority', 'MEDIUM')
        
        # Determine priority color
        p_color = colors.HexColor('#f39c12') # Medium
        if priority == 'HIGH': p_color = colors.HexColor('#e74c3c')
        elif priority == 'LOW': p_color = colors.HexColor('#3498db')
        
        # Create a colored box for priority
        p_style = ParagraphStyle('Prio', parent=styles['Normal'], textColor=colors.white, fontName='Helvetica-Bold', fontSize=9)
        p_table = Table([[Paragraph(priority, p_style)]], colWidths=[30*mm])
        p_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), p_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]), 
        ]))
        story.append(p_table)
        story.append(Spacer(1, 10*mm))
        
        # 6. Items Table
        # Header
        items_header = ['ITEM TYPE', 'PRICE', 'QTY', 'TOTAL']
        items_data = [items_header]
        
        # Rows
        items = request_data.get('items', [])
        if not items:
            items_data.append(['No items', '-', '-', '-'])
        else:
            for item in items:
                desc = item.get('item_description', 'Item')
                # Add attachment icon if exists
                if item.get('attachment_filename'):
                    desc += f" (File: {item.get('attachment_filename')})"
                    
                price = float(item.get('unit_price', 0) or 0)
                qty = float(item.get('quantity', 0) or 0)
                total = price * qty
                
                items_data.append([
                    Paragraph(desc, value_style),
                    f"${price:.2f}",
                    f"{qty}",
                    f"${total:.2f}"
                ])
        
        items_table = Table(items_data, colWidths=[80*mm, 30*mm, 30*mm, 30*mm])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_BLUE), # Header Blue
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'), # Numbers right aligned
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DEE2E6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_GRAY_BG]),
        ]))
        story.append(items_table)
        
        # Footer Drawing (Red Angular Design)
        def draw_footer(canvas, doc):
            canvas.saveState()
            
            # Draw Red Polygon
            path = canvas.beginPath()
            path.moveTo(0, 0)
            path.lineTo(doc.pagesize[0], 0)
            path.lineTo(doc.pagesize[0], 60)
            path.lineTo(doc.pagesize[0] - 50, 80) # Angle
            path.lineTo(0, 80)
            path.close()
            
            # We want this at the bottom
            # Coordinate system: 0,0 is bottom left
            # But we are in a flowable... actually for footer we should use onPage callback
            # For simplicity in SimpleDocTemplate, we can just append a graphic or use a page template
            # Let's try to append a custom flowable or just a spacer and then the contact info
            
            canvas.restoreState()

        # Since we are using SimpleDocTemplate, we can't easily do the absolute footer without a PageTemplate.
        # Let's stick to a simple footer content for now, or use a custom PageTemplate if strictly required.
        # Given the complexity, let's add the contact info at the end of the story with a red line above it.
        
        story.append(Spacer(1, 20*mm))
        
        # Footer Content
        # Red line with angle simulation
        story.append(Spacer(1, 2*mm))
        
        # Contact Info
        contact_style = ParagraphStyle('Contact', parent=styles['Normal'], fontSize=8, textColor=COLOR_TEXT_GRAY, alignment=TA_CENTER)
        
        # Make location clickable
        location_url = request_data.get('company_location', 'https://maps.google.com/maps/place//data=!4m2!3m1!1s0x164b85001ee00be1:0xe1a1d67bd070ea7?entry=s&sa=X&ved=2ahUKEwiY2-Owj6aRAxUzUkEAHbpiHEMQ4kB6BAgVEAA&hl=en')
        
        # Get sender email from request data, fallback to default
        sender_email = request_data.get('sender_email', 'info@tebitambulance.com')
        
        contact_data = [[
            Paragraph("📞 8035<br/>+251 911 225464", contact_style),
            Paragraph(f"✉️ {sender_email}<br/>www.tebitambulance.com", contact_style),
            Paragraph(f'📍 <a href="{location_url}" color="blue">Addis Ababa, Ethiopia</a>', contact_style)
        ]]
        
        contact_table = Table(contact_data, colWidths=[56*mm, 56*mm, 56*mm])
        contact_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 3, COLOR_RED), # Thick red line to simulate the design
            ('TOPPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(contact_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
