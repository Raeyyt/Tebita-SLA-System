from app.database import SessionLocal
from app.models import Request

db = SessionLocal()

# Reset request 45
r = db.query(Request).filter(Request.id == 45).first()

if r:
    print(f"Resetting {r.request_id} (ID: {r.id})")
    print(f"  Was acknowledged at: {r.acknowledged_at}")
    r.acknowledged_at = None
    r.acknowledged_by_user_id = None
    r.completed_at = None
    r.completion_validated_at = None
    db.commit()
    print("  ✅ Reset complete!")
else:
    print("Request 45 not found")

db.close()
