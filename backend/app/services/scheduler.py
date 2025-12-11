from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from app.database import SessionLocal
from app.models import Request, RequestStatus, SLAAlert, AlertType
from app.services.sla_calculator import calculate_sla_status
from app.services.backup_service import create_database_backup

# Configure logging
logging.basicConfig()
logger = logging.getLogger("apscheduler")
logger.setLevel(logging.WARNING)

scheduler = BackgroundScheduler()

def check_sla_status_job():
    """
    Periodic job to check all active requests for SLA breaches or warnings.
    Creates SLAAlert records if needed.
    """
    db = SessionLocal()
    try:
        # Get all active requests
        active_requests = db.query(Request).filter(
            Request.status.notin_([
                RequestStatus.COMPLETED, 
                RequestStatus.REJECTED, 
                RequestStatus.CANCELLED
            ])
        ).all()
        
        for request in active_requests:
            status_info = calculate_sla_status(request)
            status = status_info["status"]
            
            if status == "BREACHED":
                _create_alert_if_not_exists(db, request, AlertType.OVERDUE)
            elif status == "WARNING":
                # Could differentiate 50% vs 80% if calculator supported it, 
                # for now mapping WARNING to 80% (close to deadline)
                _create_alert_if_not_exists(db, request, AlertType.PERCENT_80)
                
    except Exception as e:
        print(f"Error in SLA check job: {e}")
    finally:
        db.close()

def _create_alert_if_not_exists(db: Session, request: Request, alert_type: AlertType):
    """Helper to create an alert only if one of that type doesn't exist for the request"""
    exists = db.query(SLAAlert).filter(
        SLAAlert.request_id == request.id,
        SLAAlert.alert_type == alert_type
    ).first()
    
    if not exists:
        alert = SLAAlert(
            request_id=request.id,
            alert_type=alert_type,
            sent_at=datetime.now(timezone.utc)
        )
        db.add(alert)
        db.commit()
        print(f"⚠️ SLA Alert Created: {alert_type} for Request {request.request_id}")

def database_backup_job():
    """
    Periodic job to backup the database.
    Runs daily at 2:00 AM.
    """
    try:
        create_database_backup()
    except Exception as e:
        print(f"❌ Error in database backup job: {e}")

def start_scheduler():
    if not scheduler.running:
        # SLA monitoring every 5 minutes
        scheduler.add_job(check_sla_status_job, 'interval', minutes=5)
        
        # Database backup daily at 2:00 AM
        scheduler.add_job(
            database_backup_job, 
            'cron', 
            hour=2, 
            minute=0,
            id='database_backup'
        )
        
        scheduler.start()
        print("⏰ Background Scheduler started:")
        print("   - SLA Monitoring: Every 5 minutes")
        print("   - Database Backup: Daily at 2:00 AM")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
