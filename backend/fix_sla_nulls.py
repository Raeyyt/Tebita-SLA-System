import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Request
from app.services.sla_calculator import calculate_deadlines

db = SessionLocal()

print("--- Fixing Requests with Missing SLA Data ---")
requests = db.query(Request).filter(Request.sla_completion_time_hours == None).all()

if not requests:
    print("No requests found with missing SLA data.")
else:
    print(f"Found {len(requests)} requests to fix.")
    for req in requests:
        print(f"Fixing Request {req.request_id}...")
        calculate_deadlines(req, db)
        print(f"  -> SLA Completion Hours: {req.sla_completion_time_hours}")
        print(f"  -> SLA Deadline: {req.sla_completion_deadline}")
    
    db.commit()
    print("Done! All requests fixed.")
