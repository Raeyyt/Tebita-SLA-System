"""
Create Demo Data for Tebita SLA System
Creates users, requests, and sample data for testing.
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User, Division, Department, Request, RequestItem, UserRole, Priority, RequestStatus, DivisionType
from app.auth import get_password_hash
from datetime import datetime, timedelta
import random

def create_demo_data():
    db = SessionLocal()
    try:
        print("🚀 Creating Demo Data...")
        
        # 1. Get Divisions & Departments
        ems_div = db.query(Division).filter(Division.name == "EMS Division").first()
        medcom_div = db.query(Division).filter(Division.name == "MEDCOM Division").first()
        support_div = db.query(Division).filter(Division.name == "Support Division").first()
        
        if not ems_div:
            print("❌ Organizational structure not found. Please run setup_organization.py first.")
            return

        # 2. Create Users
        users_data = [
            # Admin
            {"username": "admin", "full_name": "System Administrator", "role": UserRole.ADMIN, "div": support_div, "dept": None},
            
            # Leadership
            {"username": "ceo", "full_name": "Tebita CEO", "role": UserRole.LEADERSHIP, "div": None, "dept": None},
            
            # EMS Staff
            {"username": "ems_manager", "full_name": "EMS Manager", "role": UserRole.DIVISION_STAFF, "div": ems_div, "dept": ems_div.departments[0]},
            {"username": "dispatcher", "full_name": "Dispatch Supervisor", "role": UserRole.DIVISION_STAFF, "div": ems_div, "dept": ems_div.departments[0]},
            
            # Medcom Staff
            {"username": "pharmacy_head", "full_name": "Pharmacy Head", "role": UserRole.DIVISION_STAFF, "div": medcom_div, "dept": medcom_div.departments[1]},
            
            # Support Staff
            {"username": "hr_manager", "full_name": "HR Manager", "role": UserRole.SUPPORT_STAFF, "div": support_div, "dept": support_div.departments[0]},
            {"username": "finance_officer", "full_name": "Finance Officer", "role": UserRole.SUPPORT_STAFF, "div": support_div, "dept": support_div.departments[1]},
        ]
        
        created_users = []
        print("\n👤 Creating Users...")
        for u in users_data:
            # Check if exists
            existing = db.query(User).filter(User.username == u["username"]).first()
            if not existing:
                user = User(
                    username=u["username"],
                    full_name=u["full_name"],
                    email=f"{u['username']}@tebita.com",
                    hashed_password=get_password_hash("password123"), # Default password
                    role=u["role"],
                    division_id=u["div"].id if u["div"] else None,
                    department_id=u["dept"].id if u["dept"] else None,
                    is_active=True
                )
                db.add(user)
                created_users.append(user)
                print(f"  ✅ Created {u['username']}")
            else:
                created_users.append(existing)
                print(f"  ℹ️  User {u['username']} already exists")
        
        db.commit()
        
        # 3. Create Sample Requests (30+ entries)
        print("\n📝 Creating 35 Sample Requests...")
        
        request_types = ["GENERAL", "HR", "FINANCE", "IT", "MEDICAL", "LOGISTICS", "TRAINING"]
        descriptions = [
            "Urgent requirement for ambulance maintenance",
            "Request for new medical supplies batch",
            "IT support for dispatch system upgrade",
            "Staff training session materials",
            "Monthly financial report review",
            "New uniform procurement for EMS staff",
            "Vehicle insurance renewal processing",
            "Pharmaceutical inventory restocking",
            "Office supplies for HR department",
            "Network infrastructure maintenance",
            "Quarterly budget approval request",
            "Emergency oxygen cylinder refill",
            "Patient care report forms printing",
            "Ambulance GPS tracker installation",
            "Staff overtime payment processing"
        ]
        
        statuses = [
            RequestStatus.PENDING, RequestStatus.IN_PROGRESS, 
            RequestStatus.APPROVED, RequestStatus.COMPLETED, 
            RequestStatus.REJECTED
        ]
        
        priorities = [Priority.HIGH, Priority.MEDIUM, Priority.LOW]
        
        # Get all staff users for random selection
        staff_users = [u for u in created_users if u.role in [UserRole.DIVISION_STAFF, UserRole.SUPPORT_STAFF]]
        
        for i in range(1, 36): # Generate 35 requests
            # Randomize data
            requester = random.choice(staff_users)
            assigned_div = random.choice([ems_div, medcom_div, support_div])
            
            # Pick a random department from the assigned division
            if assigned_div.departments:
                assigned_dept = random.choice(assigned_div.departments)
            else:
                assigned_dept = None
                
            # Random date in last 30 days
            days_ago = random.randint(0, 30)
            created_date = datetime.now() - timedelta(days=days_ago)
            
            req = Request(
                request_id=f"REQ-{created_date.strftime('%Y%m%d')}-{i:03d}",
                request_type=random.choice(request_types),
                requester_id=requester.id,
                requester_division_id=requester.division_id,
                requester_department_id=requester.department_id,
                assigned_division_id=assigned_div.id,
                assigned_department_id=assigned_dept.id if assigned_dept else None,
                priority=random.choice(priorities),
                status=random.choice(statuses),
                description=random.choice(descriptions) + f" (Ref: {i})",
                created_at=created_date
            )
            db.add(req)
            db.flush()
            
            # Add 1-3 items per request
            for j in range(random.randint(1, 3)):
                item = RequestItem(
                    request_id=req.id,
                    item_description=f"Item {j+1} for Request {i}",
                    quantity=random.randint(1, 10),
                    unit_price=random.uniform(10.0, 500.0),
                    notes=f"Note for item {j+1}"
                )
                db.add(item)
            
            if i % 5 == 0:
                print(f"  ... Generated {i} requests")
        
        db.commit()
        print("  ✅ Created 35 sample requests with items")
        
        # 4. Output Credentials
        print("\n" + "="*60)
        print("🔑 SYSTEM LOGIN CREDENTIALS")
        print("="*60)
        print(f"{'Role':<20} | {'Username':<15} | {'Password':<15}")
        print("-" * 60)
        
        all_users = db.query(User).all()
        for u in all_users:
            # We only know the password for users we just created with "password123"
            # For existing users, we can't show the password, but we'll assume "password123" for this demo script context
            # or just show the ones we know.
            pwd = "password123" 
            print(f"{u.role.value:<20} | {u.username:<15} | {pwd:<15}")
            
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()
