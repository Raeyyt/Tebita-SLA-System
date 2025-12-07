"""
Create Targeted Demo Data for Tebita SLA System
Ensures requests are visible to specific users.
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User, Division, Department, Request, RequestItem, UserRole, Priority, RequestStatus
from app.auth import get_password_hash
from datetime import datetime, timedelta

def create_targeted_demo_data():
    db = SessionLocal()
    try:
        print("🚀 Creating Targeted Demo Data...")
        
        # 1. Get Users
        admin = db.query(User).filter(User.username == "admin").first()
        ems_manager = db.query(User).filter(User.username == "ems_manager").first()
        hr_manager = db.query(User).filter(User.username == "hr_manager").first()
        
        if not admin or not ems_manager or not hr_manager:
            print("❌ Users not found. Please run create_demo_data.py first.")
            return

        print(f"👤 Found Users: Admin({admin.id}), EMS Manager({ems_manager.id}), HR Manager({hr_manager.id})")

        # 2. Create Requests specifically for these users
        
        # Request A: Created by EMS Manager (Visible to EMS Manager & Admin)
        req_id_a = f"REQ-EMS-{datetime.now().strftime('%Y%m%d')}-A01"
        if not db.query(Request).filter(Request.request_id == req_id_a).first():
            req_a = Request(
                request_id=req_id_a,
                request_type="GENERAL",
                requester_id=ems_manager.id,
                requester_division_id=ems_manager.division_id,
                requester_department_id=ems_manager.department_id,
                assigned_division_id=hr_manager.division_id, # Assign to HR
                assigned_department_id=hr_manager.department_id,
                priority=Priority.HIGH,
                status=RequestStatus.PENDING,
                description="[DEMO] Urgent EMS Request (Visible to EMS Manager)",
                created_at=datetime.now()
            )
            db.add(req_a)
            print(f"  ✅ Created Request A: {req_id_a}")
        else:
            print(f"  ℹ️  Request A already exists: {req_id_a}")
        
        # Request B: Assigned to HR Manager (Visible to HR Manager & Admin)
        req_id_b = f"REQ-HR-{datetime.now().strftime('%Y%m%d')}-B01"
        try:
            # Debug Admin Division
            print(f"  DEBUG: Admin ID={admin.id}, Division ID={admin.division_id}, Department ID={admin.department_id}")
            
            if admin.division_id is None:
                print("  ⚠️ Admin has no division! Using HR Manager's division for demo purposes.")
                requester_div_id = hr_manager.division_id
            else:
                requester_div_id = admin.division_id

            if not db.query(Request).filter(Request.request_id == req_id_b).first():
                print(f"  Attempting to create Request B with: requester_id={admin.id}, div={requester_div_id}")
                
                req_b = Request(
                    request_id=req_id_b,
                    request_type="HR",
                    requester_id=admin.id, # Admin requesting
                    requester_division_id=requester_div_id,
                    requester_department_id=admin.department_id,
                    assigned_division_id=hr_manager.division_id,
                    assigned_department_id=hr_manager.department_id,
                    priority=Priority.MEDIUM,
                    status=RequestStatus.IN_PROGRESS,
                    description="[DEMO] Request Assigned to HR (Visible to HR Manager)",
                    created_at=datetime.now()
                )
                db.add(req_b)
                db.flush() # Flush to check for errors immediately
                
                # Add Item
                item_b = RequestItem(
                    request_id=req_b.id,
                    item_description="HR Policy Review Document",
                    quantity=1,
                    unit_price=0,
                    notes="Please review attached draft"
                )
                db.add(item_b)
                
                print(f"  ✅ Created Request B: {req_id_b}")
            else:
                print(f"  ℹ️  Request B already exists: {req_id_b}")
        except Exception as e:
            print(f"  ❌ Failed to create Request B: {e}")
            db.rollback()
        
        # Request C: Completed Request (Visible to EMS Manager)
        req_id_c = f"REQ-EMS-{datetime.now().strftime('%Y%m%d')}-C01"
        try:
            if not db.query(Request).filter(Request.request_id == req_id_c).first():
                req_c = Request(
                    request_id=req_id_c,
                    request_type="LOGISTICS",
                    requester_id=ems_manager.id,
                    requester_division_id=ems_manager.division_id,
                    requester_department_id=ems_manager.department_id,
                    assigned_division_id=hr_manager.division_id,
                    assigned_department_id=hr_manager.department_id,
                    priority=Priority.LOW,
                    status=RequestStatus.COMPLETED,
                    description="[DEMO] Completed EMS Request",
                    created_at=datetime.now() - timedelta(days=5),
                    completed_at=datetime.now()
                )
                db.add(req_c)
                db.flush()
                
                # Add Item
                item_c = RequestItem(
                    request_id=req_c.id,
                    item_description="Logistics Support Service",
                    quantity=1,
                    unit_price=500.00
                )
                db.add(item_c)
                
                print(f"  ✅ Created Request C: {req_id_c}")
            else:
                print(f"  ℹ️  Request C already exists: {req_id_c}")
        except Exception as e:
            print(f"  ❌ Failed to create Request C: {e}")
            db.rollback()

        db.commit()
        
        # 3. Verify Visibility Logic
        print("\n🔍 Verifying Visibility Logic:")
        
        # Check what EMS Manager sees (requester_division_id == ems_manager.division_id)
        ems_visible = db.query(Request).filter(Request.requester_division_id == ems_manager.division_id).count()
        print(f"  👉 EMS Manager (Division Staff) should see: {ems_visible} requests (from their division)")
        
        # Check what HR Manager sees (assigned_division_id == hr_manager.division_id)
        hr_visible = db.query(Request).filter(
            (Request.assigned_division_id == hr_manager.division_id) |
            (Request.assigned_department_id == hr_manager.department_id)
        ).count()
        print(f"  👉 HR Manager (Support Staff) should see: {hr_visible} requests (assigned to them)")
        
        # Check what Admin sees (All)
        admin_visible = db.query(Request).count()
        print(f"  👉 Admin should see: {admin_visible} requests (Total)")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_targeted_demo_data()
