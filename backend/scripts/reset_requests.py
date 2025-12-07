from app.database import SessionLocal
from app.models import Request

db = SessionLocal()

# Reset all acknowledged requests
requests = db.query(Request).filter(Request.acknowledged_at.isnot(None)).all()

print(f"Found {len(requests)} acknowledged requests")

for r in requests:
    print(f"Resetting {r.request_id} (ID: {r.id})")
    r.acknowledged_at = None
    r.acknowledged_by_user_id = None
    r.completed_at = None
    r.completion_validated_at = None
    
db.commit()
print("✅ All requests reset! You can now test acknowledge fresh.")
db.close()
