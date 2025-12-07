from app.database import SessionLocal
from app.models import Request, User

db = SessionLocal()

# Get the IT department user's incoming requests
user = db.query(User).filter(User.username == "it_department").first()

if user:
    print(f"Finding requests for {user.username} (dept={user.department_id}, subdept={user.subdepartment_id})")
    
    # Find all requests assigned to this subdepartment
    requests = db.query(Request).filter(
        Request.assigned_subdepartment_id == user.subdepartment_id
    ).all()
    
    print(f"\nFound {len(requests)} requests assigned to subdepartment {user.subdepartment_id}")
    
    for r in requests:
        print(f"\n{r.request_id} (ID: {r.id}):")
        print(f"  acknowledged_at: {r.acknowledged_at}")
        print(f"  completed_at: {r.completed_at}")
        
        if r.acknowledged_at or r.completed_at:
            print(f"  ⚠️  Resetting...")
            r.acknowledged_at = None
            r.acknowledged_by_user_id = None
            r.completed_at = None
            r.completion_validated_at = None
    
    db.commit()
    print("\n✅ All requests reset!")
else:
    print("User not found")

db.close()
