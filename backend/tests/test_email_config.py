import sys
import os
import asyncio
from sqlalchemy.orm import Session

# Add current directory to path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import SystemSettings, User
from app.services.email_service import email_service
from app.config import settings

def test_email_setup():
    db = SessionLocal()
    try:
        print("--- EMAIL CONFIG DIAGNOSIS ---")
        
        # 1. Check System Settings
        setting = db.query(SystemSettings).filter(
            SystemSettings.setting_key == "email_notifications_enabled"
        ).first()
        
        print(f"1. System Setting 'email_notifications_enabled': {setting.setting_value if setting else 'NOT SET (Defaults to False)'}")
        
        # 2. Check Config Variables (Masked)
        print("\n2. Environment Configuration:")
        print(f"   SMTP_HOST: {settings.SMTP_HOST}")
        print(f"   SMTP_PORT: {settings.SMTP_PORT}")
        print(f"   SMTP_USERNAME: {'*' * len(settings.SMTP_USERNAME) if settings.SMTP_USERNAME else 'NOT SET'}")
        print(f"   SMTP_PASSWORD: {'*' * len(settings.SMTP_PASSWORD) if settings.SMTP_PASSWORD else 'NOT SET'}")
        print(f"   SMTP_FROM_EMAIL: {settings.SMTP_FROM_EMAIL}")
        
        # 3. Test Email Sending
        print("\n3. Attempting to send test email...")
        
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            print("❌ SKIPPING SEND: SMTP Credentials are missing in .env file!")
            return

        # Create a dummy request object for testing
        class DummyRequest:
            request_id = "TEST-REQ-001"
            priority = "HIGH"
            request_type = "TEST"
            submitted_at = "2025-12-06 12:00:00"
            description = "This is a test email from the debugger."
            
            class Requester:
                full_name = "Debug Script"
            requester = Requester()

        request = DummyRequest()
        
        # Get a recipient (using the SMTP username as recipient for safety)
        recipient_email = settings.SMTP_USERNAME
        
        # Mock user object
        class DummyUser:
            email = recipient_email
            full_name = "Test Recipient"
            
        recipient = DummyUser()
        
        print(f"   Sending to: {recipient.email}")
        
        # Call the service
        try:
            # We need to bypass the check in send_high_priority_notification if setting is off
            # So we'll call the internal send logic or just force the setting on temporarily in memory
            
            # Actually, let's just call the public method and see what happens
            email_service.send_high_priority_notification(db, request, [recipient])
            print("✅ Email send function called successfully (check inbox).")
        except Exception as e:
            print(f"❌ Email send FAILED: {e}")
            import traceback
            traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    test_email_setup()
