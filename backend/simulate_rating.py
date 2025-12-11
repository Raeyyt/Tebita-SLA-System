import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Request, RequestStatus

db = SessionLocal()

print("--- Simulating Rating Submission ---")
# Get a completed request
request = db.query(Request).filter(Request.status == RequestStatus.COMPLETED).first()

if not request:
    print("No completed requests found to rate.")
else:
    print(f"Rating Request {request.request_id}...")
    
    # Simulate rating
    request.satisfaction_rating = 5
    request.satisfaction_comment = "Excellent service! Very fast."
    
    db.commit()
    print("Rating submitted successfully.")
