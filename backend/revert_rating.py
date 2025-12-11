import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Request, RequestStatus

db = SessionLocal()

print("--- Reverting Simulated Rating ---")
# Get the request we rated (REQ-GEN-20251211-001)
request = db.query(Request).filter(Request.request_id == "REQ-GEN-20251211-001").first()

if request:
    print(f"Reverting rating for {request.request_id}...")
    request.satisfaction_rating = None
    request.satisfaction_comment = None
    db.commit()
    print("Rating reverted successfully.")
else:
    print("Request not found.")
