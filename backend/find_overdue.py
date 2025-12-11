from app.database import SessionLocal
from app.models import Request, RequestStatus
from datetime import datetime, timedelta

db = SessionLocal()
now = datetime.utcnow()

print(f"Current Time (UTC): {now}")

# Find active requests (PENDING, IN_PROGRESS, APPROVED)
active_requests = db.query(Request).filter(
    Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS, RequestStatus.APPROVED])
).all()

print(f"Total Active Requests: {len(active_requests)}")

overdue_count = 0
print("\n--- Overdue Requests ---")
for req in active_requests:
    if req.created_at and req.sla_completion_time_hours:
        deadline = req.created_at + timedelta(hours=req.sla_completion_time_hours)
        if now > deadline:
            overdue_count += 1
            print(f"ID: {req.request_id}")
            print(f"  Status: {req.status}")
            print(f"  Created: {req.created_at}")
            print(f"  SLA Hours: {req.sla_completion_time_hours}")
            print(f"  Deadline: {deadline}")
            print(f"  Overdue by: {now - deadline}")
            print("-" * 20)

print(f"\nTotal Overdue Found: {overdue_count}")
