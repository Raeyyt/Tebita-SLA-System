import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent dir to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import Division, Department, SubDepartment, User, DivisionType, UserRole

def restructure():
    db = SessionLocal()
    try:
        print("--- Starting Robust 3-Tier Restructuring ---")
        
        # 1. Ensure the 3 Main Divisions exist
        main_div_configs = {
            "EMS Division": DivisionType.INCOME_GENERATING,
            "Medical Equipment Production and Imports": DivisionType.INCOME_GENERATING,
            "Support Division": DivisionType.SUPPORT
        }
        
        main_divs = {}
        for name, dtype in main_div_configs.items():
            div = db.query(Division).filter(Division.name == name).first()
            if not div:
                print(f"Creating Division: {name}")
                div = Division(name=name, type=dtype, description=name)
                db.add(div)
                db.flush()
            else:
                print(f"Found Division: {name} (ID: {div.id})")
                div.type = dtype # Ensure type is correct
            main_divs[name] = div
            
        ems_div = main_divs["EMS Division"]
        medcom_div = main_divs["Medical Equipment Production and Imports"]
        support_div = main_divs["Support Division"]
        
        # 2. Migrate ALL other divisions to Departments under the 3 main ones
        all_divs = db.query(Division).all()
        for div in all_divs:
            if div.id in [ems_div.id, medcom_div.id, support_div.id]:
                continue
                
            print(f"\nMigrating old Division '{div.name}' (ID: {div.id}) to Department...")
            
            # Determine which main division it should go under
            target_parent = support_div # Default to support
            if "EMS" in div.name or "Ambulance" in div.name:
                target_parent = ems_div
            elif "Medical" in div.name or "Equipment" in div.name or "Import" in div.name:
                target_parent = medcom_div
                
            # Create new Department
            new_dept = db.query(Department).filter(
                Department.name == div.name, 
                Department.division_id == target_parent.id
            ).first()
            
            if not new_dept:
                new_dept = Department(
                    name=div.name, 
                    division_id=target_parent.id, 
                    description=f"Migrated from Division {div.name}"
                )
                db.add(new_dept)
                db.flush()
            
            # Move Users from old Division to new Department
            users_in_div = db.query(User).filter(User.division_id == div.id, User.department_id == None).all()
            for u in users_in_div:
                print(f"  Moving User: {u.username} to {target_parent.name} / {new_dept.name}")
                u.division_id = target_parent.id
                u.department_id = new_dept.id
                
            # Move Departments from old Division to be Sub-Departments under the new Department
            old_depts = db.query(Department).filter(Department.division_id == div.id).all()
            for old_dept in old_depts:
                print(f"  Converting Dept '{old_dept.name}' to Sub-Department under {new_dept.name}...")
                
                new_sub = db.query(SubDepartment).filter(
                    SubDepartment.name == old_dept.name,
                    SubDepartment.department_id == new_dept.id
                ).first()
                
                if not new_sub:
                    new_sub = SubDepartment(
                        name=old_dept.name,
                        department_id=new_dept.id,
                        description=f"Migrated from Department {old_dept.name}"
                    )
                    db.add(new_sub)
                    db.flush()
                
                # Move Users from old Dept to new Sub-Dept
                users_in_dept = db.query(User).filter(User.department_id == old_dept.id).all()
                for u in users_in_dept:
                    u.division_id = target_parent.id
                    u.department_id = new_dept.id
                    u.subdepartment_id = new_sub.id
                
                db.delete(old_dept)
                
            # Finally delete the old division
            db.delete(div)
            db.flush()

        # 3. Fix orphaned Departments (those pointing to non-existent divisions)
        orphaned_depts = db.query(Department).filter(Department.division_id.notin_([ems_div.id, medcom_div.id, support_div.id])).all()
        for dept in orphaned_depts:
            print(f"\nFixing orphaned Department '{dept.name}' (ID: {dept.id})...")
            # Move to Support Division by default
            dept.division_id = support_div.id
            
        # 4. Fix orphaned Sub-Departments
        valid_dept_ids = [d.id for d in db.query(Department).all()]
        orphaned_subs = db.query(SubDepartment).filter(SubDepartment.department_id.notin_(valid_dept_ids)).all()
        for sub in orphaned_subs:
            print(f"Deleting orphaned Sub-Department '{sub.name}'...")
            db.delete(sub)

        db.commit()
        print("\n✅ Robust Restructuring Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    restructure()
