from app.database import SessionLocal
from app.models import User, Request
from app.routers.requests import _ensure_user_is_assignee
from fastapi import HTTPException

db = SessionLocal()

# Get User
user = db.query(User).filter(User.username == "fleet_head").first()
print(f"User: {user.username}")
print(f"Role: {user.role}")
print(f"Dept: {user.department_id}")
print(f"SubDept: {user.subdepartment_id}")

# Get Request
request = db.query(Request).filter(Request.request_id == "REQ-GEN-20251211-005").first()
print(f"\nRequest: {request.request_id}")
print(f"Assigned Dept: {request.assigned_department_id}")
print(f"Assigned SubDept: {request.assigned_subdepartment_id}")
print(f"Assigned User: {request.assigned_to_user_id}")

print("\nTesting Authorization Logic...")
try:
    _ensure_user_is_assignee(request, user)
    print("✅ Authorization PASSED")
except HTTPException as e:
    print(f"❌ Authorization FAILED: {e.detail}")
except Exception as e:
    print(f"❌ Authorization CRASHED: {e}")
