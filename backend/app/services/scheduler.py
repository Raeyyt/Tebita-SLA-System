from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from app.database import SessionLocal
from app.models import Request, RequestStatus, SLAAlert, AlertType
from app.services.sla_calculator import calculate_sla_status

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

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(check_sla_status_job, 'interval', minutes=5)
        scheduler.start()
        print("⏰ SLA Background Scheduler started (Interval: 5 mins)")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
