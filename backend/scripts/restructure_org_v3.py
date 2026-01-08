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
        print("--- Starting Exact Local Sync Restructuring ---")
        
        # 1. Define the 3 Main Divisions as they appear locally
        main_div_configs = {
            "EMS Division": DivisionType.INCOME_GENERATING,
            "Support Division": DivisionType.SUPPORT,
            "Medical Equipment Production and Imports": DivisionType.INCOME_GENERATING
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
                print(f"Found Division: {div.name}")
                div.type = dtype
            main_divs[name] = div
            
        ems_div = main_divs["EMS Division"]
        support_div = main_divs["Support Division"]
        medcom_div_empty = main_divs["Medical Equipment Production and Imports"]
        
        # 2. Define the exact Departments and their Sub-Departments
        # Structure: { DivisionName: { DeptName: [SubDeptNames] } }
        HIERARCHY = {
            "EMS Division": {
                "Comprehensive Ambulance Services": ["Fleet Head", "Ambulance Crew Head", "Dispatch Supervisor"],
                "Vocational Training": ["Dean", "Vice Dean"],
                "CPD & Short-Term Training": ["CPD Coordinator", "Short-Term Training Lead"]
            },
            "Support Division": {
                "Finance Department": [
                    "Costing Accountant", "Junior Accountant", "Cashier", 
                    "Senior Collection & Revenue Accountant", "Store Officer", 
                    "Senior Payment & Disbursement Accountant"
                ],
                "Human Resources (HR) Department": [
                    "Office Assistance", "Legal Advisor", "Procurement", 
                    "IT Department", "Maintenance", "Communication Officer"
                ],
                "MEDCOM Division": [
                    "Medical Equipment Production Department", 
                    "Pharmaceutical Imports Department", 
                    "Marketing and Sales Department"
                ]
            }
        }
        
        # 3. Apply the Hierarchy
        for div_name, depts in HIERARCHY.items():
            div = main_divs[div_name]
            for dept_name, subs in depts.items():
                # Create/Get Department
                dept = db.query(Department).filter(Department.name == dept_name, Department.division_id == div.id).first()
                if not dept:
                    # Check if it exists elsewhere and move it
                    dept = db.query(Department).filter(Department.name == dept_name).first()
                    if dept:
                        print(f"Moving Dept: {dept_name} to {div_name}")
                        dept.division_id = div.id
                    else:
                        print(f"Creating Dept: {dept_name} under {div_name}")
                        dept = Department(name=dept_name, division_id=div.id, description=dept_name)
                        db.add(dept)
                        db.flush()
                
                # Create/Get Sub-Departments
                for sub_name in subs:
                    sub = db.query(SubDepartment).filter(SubDepartment.name == sub_name, SubDepartment.department_id == dept.id).first()
                    if not sub:
                        # Check if it exists elsewhere and move it
                        sub = db.query(SubDepartment).filter(SubDepartment.name == sub_name).first()
                        if sub:
                            print(f"Moving Sub: {sub_name} to {dept_name}")
                            sub.department_id = dept.id
                        else:
                            print(f"Creating Sub: {sub_name} under {dept_name}")
                            sub = SubDepartment(name=sub_name, department_id=dept.id, description=sub_name)
                            db.add(sub)
                            db.flush()
                            
        # 4. Final Cleanup: Remove any Divisions/Depts/Subs NOT in the hierarchy
        # (Except the empty MEDCOM division we want to keep)
        valid_div_ids = [d.id for d in main_divs.values()]
        
        # Get all valid dept names from HIERARCHY
        valid_dept_names = []
        for depts in HIERARCHY.values():
            valid_dept_names.extend(depts.keys())
            
        # Get all valid sub names from HIERARCHY
        valid_sub_names = []
        for depts in HIERARCHY.values():
            for subs in depts.values():
                valid_sub_names.extend(subs)
                
        # Delete invalid Divisions
        obsolete_divs = db.query(Division).filter(Division.id.notin_(valid_div_ids)).all()
        for d in obsolete_divs:
            print(f"Deleting obsolete Division: {d.name}")
            # Move users to Support Division first
            users = db.query(User).filter(User.division_id == d.id).all()
            for u in users:
                u.division_id = support_div.id
            db.delete(d)
            
        # Delete invalid Departments
        obsolete_depts = db.query(Department).filter(Department.name.notin_(valid_dept_names)).all()
        for d in obsolete_depts:
            print(f"Deleting obsolete Department: {d.name}")
            users = db.query(User).filter(User.department_id == d.id).all()
            for u in users:
                u.department_id = None
            db.delete(d)
            
        # Delete invalid Sub-Departments
        obsolete_subs = db.query(SubDepartment).filter(SubDepartment.name.notin_(valid_sub_names)).all()
        for s in obsolete_subs:
            print(f"Deleting obsolete Sub-Department: {s.name}")
            users = db.query(User).filter(User.subdepartment_id == s.id).all()
            for u in users:
                u.subdepartment_id = None
            db.delete(s)

        db.commit()
        print("\n✅ Exact Local Sync Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    restructure()
