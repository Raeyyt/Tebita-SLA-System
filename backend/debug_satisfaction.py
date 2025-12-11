import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Request, RequestStatus

db = SessionLocal()

print("--- Debugging Satisfaction Ratings ---")
# Get all completed requests
completed_requests = db.query(Request).filter(Request.status == RequestStatus.COMPLETED).all()

print(f"Total Completed Requests: {len(completed_requests)}")

rated_requests = [r for r in completed_requests if r.satisfaction_rating is not None]
print(f"Rated Requests: {len(rated_requests)}")

if rated_requests:
    total_score = sum(r.satisfaction_rating for r in rated_requests)
    avg_score = total_score / len(rated_requests)
    print(f"Average Score (Manual Calc): {avg_score}")
    
    for req in rated_requests:
        print(f"  - Request {req.request_id}: Rating={req.satisfaction_rating}, Comment='{req.satisfaction_comment}'")
else:
    print("No requests have been rated yet.")

print("\n--- Checking Unrated Completed Requests ---")
unrated = [r for r in completed_requests if r.satisfaction_rating is None]
for req in unrated[:5]:
    print(f"  - Request {req.request_id}: Unrated")
