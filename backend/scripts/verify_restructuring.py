"""
Verify organizational restructuring results
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

def verify_restructuring():
    db = SessionLocal()
    try:
        print("=" * 80)
        print("VERIFICATION REPORT")
        print("=" * 80)
        
        # Count users by role
        admin_count = db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).count()
        div_mgr_count = db.query(models.User).filter(models.User.role == models.UserRole.DIVISION_MANAGER).count()
        dept_head_count = db.query(models.User).filter(models.User.role == models.UserRole.DEPARTMENT_HEAD).count()
        staff_count = db.query(models.User).filter(models.User.role == models.UserRole.SUB_DEPARTMENT_STAFF).count()
        
        total = admin_count + div_mgr_count + dept_head_count + staff_count
        
        print(f"\nUser Count by Role:")
        print(f"  Level 1 (ADMIN):                 {admin_count}")
        print(f"  Level 2 (DIVISION_MANAGER):      {div_mgr_count}")
        print(f"  Level 3 (DEPARTMENT_HEAD):       {dept_head_count}")
        print(f"  Level 4 (SUB_DEPARTMENT_STAFF):  {staff_count}")
        print(f"  {'─' * 40}")
        print(f"  TOTAL:                           {total}")
        
        # List Division Managers
        print(f"\n\nDivision Managers ({div_mgr_count}):")
        div_mgrs = db.query(models.User).filter(models.User.role == models.UserRole.DIVISION_MANAGER).all()
        for user in div_mgrs:
            div_name = user.division.name if user.division else "N/A"
            print(f"  • {user.username:<30} | {div_name}")
        
        # List Department Heads
        print(f"\n\nDepartment Heads ({dept_head_count}):")
        dept_heads = db.query(models.User).filter(models.User.role == models.UserRole.DEPARTMENT_HEAD).all()
        for user in dept_heads:
            dept_name = user.department.name if user.department else "N/A"
            print(f"  • {user.username:<30} | {dept_name}")
        
        # Sample Sub-Department Staff
        print(f"\n\nSub-Department Staff (showing first 5 of {staff_count}):")
        staff = db.query(models.User).filter(models.User.role == models.UserRole.SUB_DEPARTMENT_STAFF).limit(5).all()
        for user in staff:
            subdept_name = user.subdepartment.name if user.subdepartment else "N/A"
            print(f"  • {user.username:<30} | {subdept_name}")
        
        if staff_count > 5:
            print(f"  ... and {staff_count - 5} more")
        
        print("\n" + "=" * 80)
        
        # Check for expected totals
        expected = {
            "ADMIN": 1,
            "DIVISION_MANAGER": 3,
            "DEPARTMENT_HEAD": 7,
            "SUB_DEPARTMENT_STAFF": 23
        }
        
        success = True
        if admin_count != expected["ADMIN"]:
            print(f"⚠️  Expected {expected['ADMIN']} ADMIN, found {admin_count}")
            success = False
        if div_mgr_count != expected["DIVISION_MANAGER"]:
            print(f"⚠️  Expected {expected['DIVISION_MANAGER']} DIVISION_MANAGER, found {div_mgr_count}")
            success = False
        if dept_head_count != expected["DEPARTMENT_HEAD"]:
            print(f"⚠️  Expected {expected['DEPARTMENT_HEAD']} DEPARTMENT_HEAD, found {dept_head_count}")
            success = False
        if staff_count != expected["SUB_DEPARTMENT_STAFF"]:
            print(f"⚠️  Expected {expected['SUB_DEPARTMENT_STAFF']} SUB_DEPARTMENT_STAFF, found {staff_count}")
            success = False
        
        if success:
            print("✅ Restructuring SUCCESSFUL!")
        else:
            print("❌ Restructuring needs attention")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_restructuring()
