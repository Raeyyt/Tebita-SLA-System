import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import make_msgid
from typing import List, Optional
import logging
from sqlalchemy.orm import Session
import os

from ..config import settings
from ..models import Request, User, SystemSettings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications"""
    
    @staticmethod
    def is_email_enabled(db: Session) -> bool:
        """Check if email notifications are enabled in system settings"""
        try:
            setting = db.query(SystemSettings).filter(
                SystemSettings.setting_key == "email_notifications_enabled"
            ).first()
            
            if not setting:
                # Default to disabled if setting doesn't exist
                return False
            
            return setting.setting_value.lower() == "true"
        except Exception as e:
            logger.error(f"Error checking email settings: {e}")
            return False
    
    @staticmethod
    def send_request_notification(
        db: Session,
        request: Request,
        assigned_users: List[User]
    ) -> bool:
        """
        Send email notification for a new request (any priority)
        
        Returns True if email sent successfully, False otherwise
        """
        # Check if email notifications are enabled globally
        if not EmailService.is_email_enabled(db):
            logger.info("Email notifications are disabled in system settings")
            return False
        
        # Fetch SMTP settings from DB
        smtp_host_setting = db.query(SystemSettings).filter(SystemSettings.setting_key == "smtp_host").first()
        smtp_port_setting = db.query(SystemSettings).filter(SystemSettings.setting_key == "smtp_port").first()
        smtp_user_setting = db.query(SystemSettings).filter(SystemSettings.setting_key == "smtp_email").first()
        smtp_pass_setting = db.query(SystemSettings).filter(SystemSettings.setting_key == "smtp_password").first()
        
        # Use DB settings or fallback to env vars
        smtp_host = smtp_host_setting.setting_value if smtp_host_setting else settings.SMTP_HOST
        smtp_port = int(smtp_port_setting.setting_value) if smtp_port_setting else settings.SMTP_PORT
        smtp_user = smtp_user_setting.setting_value if smtp_user_setting else settings.SMTP_USERNAME
        smtp_pass = smtp_pass_setting.setting_value if smtp_pass_setting else settings.SMTP_PASSWORD
        
        if not smtp_host or not smtp_user:
            logger.warning("SMTP not configured, skipping email")
            return False
        
        try:
            # Get recipients
            recipients = [user.email for user in assigned_users if user.email]
            
            if not recipients:
                logger.warning(f"No email recipients for request {request.request_id}")
                return False
            
            # Generate CIDs for images
            header_cid = make_msgid()
            icon_cid = make_msgid()
            
            # Create email content
            # Handle Priority Enum
            priority_value = request.priority.value if hasattr(request.priority, 'value') else str(request.priority)
            if "Priority." in priority_value:
                priority_value = priority_value.split('.')[-1]
            
            # Update: Use 🚨 for ALL priorities
            priority_emoji = "🚨"
            subject = f"{priority_emoji} {priority_value} PRIORITY Request - {request.request_id}"
            
            # Pass CIDs (stripping angle brackets for HTML src)
            html_body = EmailService._create_email_html(
                request, 
                header_cid[1:-1], 
                icon_cid[1:-1]
            )
            
            # Send email with attachments
            try:
                # Define image paths
                # Current file: backend/app/services/email_service.py
                # We need to go up 4 levels to reach project root: services -> app -> backend -> Tebita-SLA-System
                current_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.dirname(os.path.dirname(current_dir))
                project_root = os.path.dirname(backend_dir)
                
                header_logo_path = os.path.join(project_root, "frontend", "public", "tebita-email-header.png")
                icon_image_path = os.path.join(project_root, "frontend", "public", "tebita-email-icon.png")
                
                images = []
                
                # Helper to load image
                def load_image(path, cid):
                    if os.path.exists(path):
                        with open(path, 'rb') as f:
                            img_data = f.read()
                            # Pass the full CID (with brackets) for the header
                            return {"data": img_data, "cid": cid, "name": os.path.basename(path)}
                    return None

                img1 = load_image(header_logo_path, header_cid)
                if img1: images.append(img1)
                
                img2 = load_image(icon_image_path, icon_cid)
                if img2: images.append(img2)

                return EmailService._send_email(
                    recipients=recipients,
                    subject=subject,
                    html_body=html_body,
                    smtp_host=smtp_host,
                    smtp_port=smtp_port,
                    smtp_user=smtp_user,
                    smtp_pass=smtp_pass,
                    images=images
                )
            except Exception as e:
                logger.error(f"Error preparing email images: {e}")
                # Fallback to sending without images if file access fails
                return EmailService._send_email(
                    recipients=recipients,
                    subject=subject,
                    html_body=html_body,
                    smtp_host=smtp_host,
                    smtp_port=smtp_port,
                    smtp_user=smtp_user,
                    smtp_pass=smtp_pass
                )
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    @staticmethod
    def _create_email_html(request: Request, header_cid: str, icon_cid: str) -> str:
        """Create HTML email body"""
        
        # Get department/division name
        assigned_to = (
            request.assigned_subdepartment.name if request.assigned_subdepartment
            else request.assigned_department.name if request.assigned_department
            else request.assigned_division.name if request.assigned_division
            else "Your Department"
        )
        
        # Format deadline
        deadline = request.sla_completion_deadline.strftime("%b %d, %Y - %I:%M %p") if request.sla_completion_deadline else "Not set"
        
        # Create request link
        request_link = f"{settings.FRONTEND_URL}/requests/{request.id}"
        
        # Fix priority display (handle Enum)
        priority_display = request.priority.value if hasattr(request.priority, 'value') else str(request.priority)
        if "Priority." in priority_display:
            priority_display = priority_display.split('.')[-1]
            
        priority_color = "#dc2626" if priority_display == "HIGH" else "#d97706" if priority_display == "MEDIUM" else "#059669"
        
        # HTML Content with CID references - Table Based for Maximum Compatibility
        html = f"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>New Request Assigned</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%">
        <tr>
            <td style="padding: 20px 0 30px 0;">
                <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td align="center" bgcolor="#8B0000" style="padding: 30px 20px;">
                            <img src="cid:{header_cid}" alt="Tebita Ambulance" width="220" style="display: block; max-width: 100%; height: auto;" />
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td bgcolor="#ffffff" style="padding: 40px 30px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <!-- Icon & Title -->
                                <tr>
                                    <td align="center" style="padding-bottom: 20px;">
                                        <img src="cid:{icon_cid}" alt="Alert" width="80" style="display: block; max-width: 80px; height: auto;" />
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="color: #111111; font-size: 24px; font-weight: bold; padding-bottom: 10px;">
                                        New Request Assigned
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="color: #666666; font-size: 16px; line-height: 1.5; padding-bottom: 30px;">
                                        A new request has been submitted to <strong>{assigned_to}</strong>.
                                    </td>
                                </tr>
                                
                                <!-- Details Box -->
                                <tr>
                                    <td>
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border: 1px solid #eeeeee; border-radius: 6px;">
                                            <tr>
                                                <td width="35%" style="padding: 15px; border-bottom: 1px solid #eeeeee; color: #666666; font-weight: bold; font-size: 14px;">Request ID</td>
                                                <td width="65%" style="padding: 15px; border-bottom: 1px solid #eeeeee; color: #111111; font-size: 14px;"><strong>{request.request_id}</strong></td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 15px; border-bottom: 1px solid #eeeeee; color: #666666; font-weight: bold; font-size: 14px;">Priority</td>
                                                <td style="padding: 15px; border-bottom: 1px solid #eeeeee; font-size: 14px;">
                                                    <span style="background-color: {priority_color}; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold;">{priority_display}</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 15px; border-bottom: 1px solid #eeeeee; color: #666666; font-weight: bold; font-size: 14px;">Type</td>
                                                <td style="padding: 15px; border-bottom: 1px solid #eeeeee; color: #111111; font-size: 14px;">{request.request_type.replace('_', ' ').title()}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 15px; border-bottom: 1px solid #eeeeee; color: #666666; font-weight: bold; font-size: 14px;">Submitted By</td>
                                                <td style="padding: 15px; border-bottom: 1px solid #eeeeee; color: #111111; font-size: 14px;">{request.requester.full_name if request.requester else 'N/A'}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 15px; color: #666666; font-weight: bold; font-size: 14px;">Deadline</td>
                                                <td style="padding: 15px; color: #111111; font-size: 14px;">{deadline}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                                
                                <!-- Description -->
                                <tr>
                                    <td style="padding-top: 30px;">
                                        <div style="background-color: #f9f9f9; border-left: 4px solid #8B0000; padding: 15px; border-radius: 4px;">
                                            <div style="color: #8B0000; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px;">Description</div>
                                            <div style="color: #333333; font-size: 14px; line-height: 1.6;">{request.description}</div>
                                        </div>
                                    </td>
                                </tr>
                                
                                <!-- Button -->
                                <tr>
                                    <td align="center" style="padding-top: 30px;">
                                        <table border="0" cellspacing="0" cellpadding="0">
                                            <tr>
                                                <td align="center" style="border-radius: 4px;" bgcolor="#8B0000">
                                                    <a href="{request_link}" target="_blank" style="font-size: 16px; font-family: Arial, sans-serif; color: #ffffff; text-decoration: none; padding: 12px 30px; border-radius: 4px; border: 1px solid #8B0000; display: inline-block; font-weight: bold;">View Request</a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td bgcolor="#8B0000" style="padding: 30px 30px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="color: #ffffff; font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; padding-bottom: 10px;">
                                        Tebita Ambulance Pre-Hospital Emergency Medical Service
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="color: #ffffff; font-family: Arial, sans-serif; font-size: 12px; opacity: 0.8;">
                                        Addis Ababa, Ethiopia
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="color: #ffffff; font-family: Arial, sans-serif; font-size: 12px; opacity: 0.6; padding-top: 20px;">
                                        This is an automated notification. Please do not reply.
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        return html
    
    @staticmethod
    def _send_email(
        recipients: List[str], 
        subject: str, 
        html_body: str,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_pass: str,
        images: Optional[List[dict]] = None
    ) -> bool:
        """Send email using SMTP with provided credentials"""
        try:
            # Create message
            msg = MIMEMultipart('related')
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{smtp_user}>"
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Attach images if provided
            if images:
                for img in images:
                    try:
                        image_part = MIMEImage(img['data'], name=img['name'])
                        # Use the CID exactly as provided (should include angle brackets)
                        image_part.add_header('Content-ID', f"{img['cid']}")
                        image_part.add_header('Content-Disposition', 'inline', filename=img['name'])
                        msg.attach(image_part)
                    except Exception as e:
                        logger.error(f"Failed to attach image {img.get('name')}: {e}")
            
            # Connect to SMTP server
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {len(recipients)} recipient(s)")
            return True
            
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False


# Global instance
email_service = EmailService()


