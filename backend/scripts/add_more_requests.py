"""Add 32 more requests for comprehensive testing"""
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
import sys
sys.path.insert(0, '.')

from app.models import *

engine = create_engine("sqlite:///./tebita.db", connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
db = Session()

print("Adding 32 more requests...")

try:
    divs = db.query(Division).all()
    admin = db.query(User).filter_by(username="admin").first()
    
    ems = [d for d in divs if "EMS" in d.name][0]
    fin = [d for d in divs if "Finance" in d.name][0]
    hr = [d for d in divs if "HR" in d.name][0]
    ict = divs[-1]
    
    types = ["Equipment", "Training", "IT Support", "Supplies", "Maintenance", "Recruitment", "License"]
    created = 0
    
    for div in [ems, fin, hr, ict]:
        for i in range(8):
            days_ago = random.randint(5, 80)
            status = random.choice([RequestStatus.PENDING, RequestStatus.APPROVED, RequestStatus.IN_PROGRESS, 
                                   RequestStatus.COMPLETED, RequestStatus.COMPLETED])
            priority = random.choice([Priority.HIGH, Priority.MEDIUM, Priority.LOW])
            sla_hrs = 24 if priority == Priority.HIGH else 72
            created_date = datetime.now() - timedelta(days=days_ago)
            
            r = Request(
                request_id=f'REQ-{div.name[:3]}-{created_date.strftime("%Y%m%d")}-{200+created:03d}',
                request_type=random.choice(types),
                requester_id=admin.id,
                requester_division_id=div.id,
                assigned_division_id=random.choice([d for d in divs if d != div]).id,
                priority=priority,
                description=f'Request for {random.choice(types)}',
                status=status,
                sla_response_time_hours=sla_hrs,
                sla_completion_time_hours=sla_hrs*3,
                created_at=created_date,
                submitted_at=created_date+timedelta(hours=2) if status != RequestStatus.PENDING else None,
                approved_at=created_date+timedelta(days=1) if status in [RequestStatus.APPROVED, RequestStatus.IN_PROGRESS, RequestStatus.COMPLETED] else None,
                completed_at=created_date+timedelta(days=random.randint(3,7)) if status == RequestStatus.COMPLETED and days_ago > 7 else None
            )
            db.add(r)
            db.flush()
            
            db.add(RequestItem(
                request_id=r.id,
                item_description=f'Item for {r.request_type}',
                quantity=Decimal(str(random.randint(1,10))),
                unit_price=Decimal(str(random.randint(1000,20000)))
            ))
            created += 1
    
    db.commit()
    total = db.query(Request).count()
    print(f"✓ Created {created} additional requests")
    print(f"✓ Total requests in database: {total}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
