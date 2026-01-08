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
        print("--- Starting Final 3-Tier Restructuring ---")
        
        # 1. Define the 3 Main Divisions with preferred names
        main_div_configs = {
            "EMS Division": DivisionType.INCOME_GENERATING,
            "MEDCOM Division": DivisionType.INCOME_GENERATING,
            "Support Division": DivisionType.SUPPORT
        }
        
        # Mapping for renaming
        rename_map = {
            "Medical Equipment Production and Imports": "MEDCOM Division"
        }
        
        main_divs = {}
        for name, dtype in main_div_configs.items():
            # Check if it exists with preferred name
            div = db.query(Division).filter(Division.name == name).first()
            
            # If not, check if it exists with an old name that needs renaming
            if not div:
                for old_name, new_name in rename_map.items():
                    if new_name == name:
                        old_div = db.query(Division).filter(Division.name == old_name).first()
                        if old_div:
                            print(f"Renaming Division: {old_name} -> {new_name}")
                            old_div.name = new_name
                            div = old_div
                            break
            
            if not div:
                print(f"Creating Division: {name}")
                div = Division(name=name, type=dtype, description=name)
                db.add(div)
                db.flush()
            else:
                print(f"Found Division: {div.name} (ID: {div.id})")
                div.type = dtype
            
            main_divs[name] = div
            
        ems_div = main_divs["EMS Division"]
        medcom_div = main_divs["MEDCOM Division"]
        support_div = main_divs["Support Division"]
        
        # 2. Migrate ALL other divisions to Departments
        all_divs = db.query(Division).all()
        for div in all_divs:
            if div.id in [ems_div.id, medcom_div.id, support_div.id]:
                continue
                
            print(f"\nMigrating old Division '{div.name}' (ID: {div.id}) to Department...")
            
            # Determine target parent
            target_parent = support_div
            if "EMS" in div.name or "Ambulance" in div.name:
                target_parent = ems_div
            elif "MEDCOM" in div.name or "Medical" in div.name or "Equipment" in div.name or "Import" in div.name:
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
            
            # Move Users
            users_in_div = db.query(User).filter(User.division_id == div.id, User.department_id == None).all()
            for u in users_in_div:
                u.division_id = target_parent.id
                u.department_id = new_dept.id
                
            # Move Departments to Sub-Departments
            old_depts = db.query(Department).filter(Department.division_id == div.id).all()
            for old_dept in old_depts:
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
                
                users_in_dept = db.query(User).filter(User.department_id == old_dept.id).all()
                for u in users_in_dept:
                    u.division_id = target_parent.id
                    u.department_id = new_dept.id
                    u.subdepartment_id = new_sub.id
                
                db.delete(old_dept)
                
            db.delete(div)
            db.flush()

        # 3. Final Cleanup of Orphaned Records
        valid_div_ids = [ems_div.id, medcom_div.id, support_div.id]
        orphaned_depts = db.query(Department).filter(Department.division_id.notin_(valid_div_ids)).all()
        for dept in orphaned_depts:
            dept.division_id = support_div.id
            
        valid_dept_ids = [d.id for d in db.query(Department).all()]
        orphaned_subs = db.query(SubDepartment).filter(SubDepartment.department_id.notin_(valid_dept_ids)).all()
        for sub in orphaned_subs:
            db.delete(sub)

        db.commit()
        print("\n✅ Final Restructuring Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    restructure()
