import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
from sqlalchemy.orm import Session

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
            
            # Create email content
            priority_emoji = "🔴" if request.priority == "HIGH" else "🟡" if request.priority == "MEDIUM" else "🟢"
            subject = f"{priority_emoji} {request.priority} PRIORITY Request - {request.request_id}"
            html_body = EmailService._create_email_html(request)
            
            # Send email
            return EmailService._send_email(recipients, subject, html_body, smtp_host, smtp_port, smtp_user, smtp_pass)
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    @staticmethod
    def _create_email_html(request: Request) -> str:
        """Create HTML email body"""
        
        # Get department/division name
        assigned_to = (
            request.assigned_subdepartment.name if request.assigned_subdepartment
            else request.assigned_department.name if request.assigned_department
            else request.assigned_division.name if request.assigned_division
            else "Your Department"
        )
        
        # Format deadline
        deadline = request.due_date.strftime("%b %d, %Y - %I:%M %p") if request.due_date else "Not set"
        
        # Create request link
        request_link = f"{settings.FRONTEND_URL}/requests/{request.id}"
        
        priority_color = "#ef4444" if request.priority == "HIGH" else "#f59e0b" if request.priority == "MEDIUM" else "#10b981"
        priority_emoji = "🔴" if request.priority == "HIGH" else "🟡" if request.priority == "MEDIUM" else "🟢"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .details {{ background: white; padding: 20px; border-left: 4px solid {priority_color}; margin: 20px 0; }}
        .detail-row {{ display: flex; margin: 10px 0; }}
        .detail-label {{ font-weight: bold; min-width: 140px; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; margin-top: 30px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{priority_emoji} {request.priority} PRIORITY REQUEST</h1>
            <p>A new request has been assigned to {assigned_to}</p>
        </div>
        
        <div class="content">
            <div class="details">
                <h2>Request Details</h2>
                <div class="detail-row">
                    <span class="detail-label">Request ID:</span>
                    <span>{request.request_id}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Priority:</span>
                    <span style="color: {priority_color}; font-weight: bold;">{priority_emoji} {request.priority}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Type:</span>
                    <span>{request.request_type.replace('_', ' ').title()}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Submitted By:</span>
                    <span>{request.requester.full_name if request.requester else 'N/A'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Deadline:</span>
                    <span>{deadline}</span>
                </div>
            </div>
            
            <div style="background: white; padding: 20px; margin: 20px 0;">
                <h3>Description:</h3>
                <p>{request.description}</p>
            </div>
            
            <div style="text-align: center;">
                <a href="{request_link}" class="button">View Request in System</a>
            </div>
            
            <p style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-top: 20px;">
                ⚠️ <strong>Action Required:</strong> Please review and acknowledge this request.
            </p>
        </div>
        
        <div class="footer">
            <p><strong>Tebita Ambulance SLA System</strong></p>
            <p>ጠብታ አምቡላንስ</p>
            <p style="font-size: 10px; color: #999;">
                This is an automated notification. Please do not reply to this email.
            </p>
        </div>
    </div>
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
        smtp_pass: str
    ) -> bool:
        """Send email using SMTP with provided credentials"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{smtp_user}>"
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
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

# Global instance
email_service = EmailService()
