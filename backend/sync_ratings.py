import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Request, CustomerSatisfaction

db = SessionLocal()

print("--- Syncing Ratings from CustomerSatisfaction to Request ---")
ratings = db.query(CustomerSatisfaction).all()

if not ratings:
    print("No ratings found in CustomerSatisfaction table.")
else:
    print(f"Found {len(ratings)} ratings to sync.")
    count = 0
    for rating in ratings:
        request = db.query(Request).filter(Request.id == rating.request_id).first()
        if request:
            if request.satisfaction_rating is None:
                print(f"Syncing Request {request.request_id}: Rating={rating.overall_score}")
                request.satisfaction_rating = rating.overall_score
                request.satisfaction_comment = rating.comments
                count += 1
            else:
                print(f"Request {request.request_id} already has rating: {request.satisfaction_rating}")
        else:
            print(f"Warning: Request ID {rating.request_id} not found.")
    
    if count > 0:
        db.commit()
        print(f"Successfully synced {count} ratings.")
    else:
        print("No updates needed.")
