import sys
import os
sys.path.append(os.getcwd())

from app.models import Request
from app.database import SessionLocal

db = SessionLocal()

print("--- Debugging Recent Requests ---")
requests = db.query(Request).order_by(Request.created_at.desc()).limit(5).all()

if not requests:
    print("No requests found.")
else:
    for req in requests:
        print(f"ID: {req.id} | RequestID: {req.request_id}")
        print(f"  Status: {req.status}")
        print(f"  Created At: {req.created_at}")
        print(f"  SLA Completion Hours: {req.sla_completion_time_hours}")
        print(f"  SLA Completion Deadline: {req.sla_completion_deadline}")
        print(f"  Requester ID: {req.requester_id}")
        print("-" * 30)

print("\n--- Checking SLA Compliance Logic ---")
# Simulate the query from get_sla_compliance
from app.models import RequestStatus
from datetime import datetime, timedelta

now = datetime.utcnow()
start = now - timedelta(days=30)

query = db.query(Request).filter(Request.created_at >= start)
active_requests = query.filter(
    Request.status.in_([RequestStatus.PENDING, RequestStatus.IN_PROGRESS]),
    Request.sla_completion_time_hours.isnot(None),
    Request.created_at.isnot(None)
).all()

print(f"Active Requests (Pending/InProgress + SLA + CreatedAt): {len(active_requests)}")
for req in active_requests:
    print(f"  - {req.request_id}: {req.status}")
