"""
Organizational Restructuring Script
Implements the final 4-level hierarchy:
- Level 1: ADMIN (raeyyt - preserved)
- Level 2: DIVISION_MANAGER (3 users)
- Level 3: DEPARTMENT_HEAD (7 users)
- Level 4: SUB_DEPARTMENT_STAFF (23 users)
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from app.auth import get_password_hash

def restructure_organization():
    db = SessionLocal()
    try:
        print("=" * 80)
        print("ORGANIZATIONAL RESTRUCTURING")
        print("=" * 80)
        
        # Step 1: Delete all users except raeyyt
        print("\n[1/4] Cleaning up existing users...")
        users_to_delete = db.query(models.User).filter(models.User.username != "raeyyt").all()
        count = len(users_to_delete)
        for user in users_to_delete:
            db.delete(user)
        db.commit()
        print(f"✓ Deleted {count} users (kept: raeyyt)")
        
        # Step 2: Update raeyyt to ADMIN role
        print("\n[2/4] Updating raeyyt to ADMIN role...")
        raeyyt = db.query(models.User).filter(models.User.username == "raeyyt").first()
        if raeyyt:
            raeyyt.role = models.UserRole.ADMIN
            db.commit()
            print("✓ raeyyt is now ADMIN (Level 1)")
        
        # Step 3: Create Division Managers (Level 2)
        print("\n[3/4] Creating Division Managers (Level 2)...")
        
        # Get divisions
        ems_div = db.query(models.Division).filter(models.Division.name == "EMS Division").first()
        medcom_div = db.query(models.Division).filter(models.Division.name == "MEDCOM Division").first()
        support_div = db.query(models.Division).filter(models.Division.name == "Support Division").first()
        
        division_managers = [
            {
                "username": "ems_division_manager",
                "full_name": "EMS Division Manager",
                "email": "ems.manager@tebita.com",
                "division_id": ems_div.id if ems_div else None
            },
            {
                "username": "medcom_division_manager",
                "full_name": "MEDCOM Division Manager",
                "email": "medcom.manager@tebita.com",
                "division_id": medcom_div.id if medcom_div else None
            },
            {
                "username": "support_division_liaison",
                "full_name": "Support Division Liaison",
                "email": "support.liaison@tebita.com",
                "division_id": support_div.id if support_div else None
            }
        ]
        
        for mgr in division_managers:
            user = models.User(
                username=mgr["username"],
                full_name=mgr["full_name"],
                email=mgr["email"],
                hashed_password=get_password_hash("password123"),
                role=models.UserRole.DIVISION_MANAGER,
                division_id=mgr["division_id"],
                is_active=True
            )
            db.add(user)
            print(f"  ✓ {mgr['username']}")
        
        db.commit()
        
        # Step 4: Create Department Heads (Level 3) and Sub-Department Staff (Level 4)
        print("\n[4/4] Creating Department Heads (Level 3) and Sub-Department Staff (Level 4)...")
        
        # Get all departments and subdepartments
        departments = db.query(models.Department).all()
        subdepartments = db.query(models.SubDepartment).all()
        
        # Map department names to usernames
        dept_head_mapping = {
            "Comprehensive Ambulance Service": "ambulance_services_head",
            "CPD Short Term Training": "cpd_training_head",
            "Vocational Training": "vocational_training_head",
            "Medical Equipment Production": "medical_equipment_head",
            "Pharmaceutical Import": "pharma_import_head",
            "HR": "hr_manager",
            "Finance": "finance_manager"
        }
        
        created_heads = []
        created_staff = []
        
        # Create Department Heads
        for dept in departments:
            if dept.name in dept_head_mapping:
                username = dept_head_mapping[dept.name]
                head = models.User(
                    username=username,
                    full_name=f"{dept.name} Head",
                    email=f"{username}@tebita.com",
                    hashed_password=get_password_hash("password123"),
                    role=models.UserRole.DEPARTMENT_HEAD,
                    division_id=dept.division_id,
                    department_id=dept.id,
                    is_active=True
                )
                db.add(head)
                created_heads.append(username)
                print(f"  ✓ {username} (Department Head)")
        
        db.commit()
        
        # Create Sub-Department Staff
        for subdept in subdepartments:
            # Create username from subdepartment name
            username = subdept.name.lower().replace(" ", "_").replace("&", "and")
            username = username[:50]  # Truncate if too long
            
            staff = models.User(
                username=username,
                full_name=subdept.name,
                email=f"{username}@tebita.com",
                hashed_password=get_password_hash("password123"),
                role=models.UserRole.SUB_DEPARTMENT_STAFF,
                division_id=subdept.department.division_id,
                department_id=subdept.department_id,
                subdepartment_id=subdept.id,
                is_active=True
            )
            db.add(staff)
            created_staff.append(username)
        
        db.commit()
        print(f"  ✓ Created {len(created_staff)} Sub-Department Staff members")
        
        # Summary
        print("\n" + "=" * 80)
        print("RESTRUCTURING COMPLETE")
        print("=" * 80)
        print(f"\n✓ Level 1 (ADMIN): 1 user")
        print(f"✓ Level 2 (DIVISION_MANAGER): {len(division_managers)} users")
        print(f"✓ Level 3 (DEPARTMENT_HEAD): {len(created_heads)} users")
        print(f"✓ Level 4 (SUB_DEPARTMENT_STAFF): {len(created_staff)} users")
        print(f"\n📊 TOTAL USERS: {1 + len(division_managers) + len(created_heads) + len(created_staff)}")
        print(f"\n🔑 Default password for all users: password123")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    restructure_organization()
