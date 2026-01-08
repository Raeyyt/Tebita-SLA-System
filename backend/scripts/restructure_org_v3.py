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
        print("--- Starting JSON-Based Restructuring ---")
        
        # 1. Define the Hierarchy from JSON
        HIERARCHY = {
            "EMS": {
                "type": DivisionType.INCOME_GENERATING,
                "departments": {
                    "Comprehensive Ambulance Services": ["Fleet Head", "Ambulance Crew Head", "Dispatch Supervisor"],
                    "Vocational Training": ["Dean", "Vice Dean"],
                    "CPD & Short-Term Training": ["CPD Coordinator", "Short-Term Training Lead"]
                }
            },
            "Medcom": {
                "type": DivisionType.INCOME_GENERATING,
                "departments": {
                    "Medical Equipment Production Department": ["Ambulance Outfitting", "First Aid Kit Production"],
                    "Marketing and Sales Department": [],
                    "Pharmaceutical Import Department": []
                }
            },
            "Support": {
                "type": DivisionType.SUPPORT,
                "departments": {
                    "Finance Department": [
                        "Cost Accountant", "Junior Accountant", "Cashier", 
                        "Senior Collection and Revenue Accountant", "Store Officer", 
                        "Senior Payment & Disbursement Accountant"
                    ],
                    "Human Resources Department": [
                        "Office Assistant", "Legal Advisor", "Procurement", 
                        "IT Department", "Maintenance", "Communication Officer"
                    ]
                }
            }
        }
        
        # 2. Process Hierarchy
        valid_div_ids = []
        valid_dept_ids = []
        valid_sub_ids = []
        
        for div_name, div_data in HIERARCHY.items():
            # Create/Get Division
            div = db.query(Division).filter(Division.name == div_name).first()
            if not div:
                # Check for similar names to rename if needed
                similar_names = [f"{div_name} Division", div_name.upper()]
                div = db.query(Division).filter(Division.name.in_(similar_names)).first()
                if div:
                    print(f"Renaming Division: {div.name} -> {div_name}")
                    div.name = div_name
                else:
                    print(f"Creating Division: {div_name}")
                    div = Division(name=div_name, type=div_data["type"], description=div_name)
                    db.add(div)
                    db.flush()
            
            div.type = div_data["type"]
            valid_div_ids.append(div.id)
            
            for dept_name, subs in div_data["departments"].items():
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
                
                valid_dept_ids.append(dept.id)
                
                for sub_name in subs:
                    # Create/Get Sub-Department
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
                    
                    valid_sub_ids.append(sub.id)

        # 3. Cleanup and Re-assignment
        # Move users from obsolete divisions to Support Division (default)
        support_div = db.query(Division).filter(Division.name == "Support").first()
        
        obsolete_divs = db.query(Division).filter(Division.id.notin_(valid_div_ids)).all()
        for d in obsolete_divs:
            print(f"Cleaning up obsolete Division: {d.name}")
            users = db.query(User).filter(User.division_id == d.id).all()
            for u in users:
                u.division_id = support_div.id if support_div else None
            db.delete(d)
            
        # Obsolete Departments
        obsolete_depts = db.query(Department).filter(Department.id.notin_(valid_dept_ids)).all()
        for d in obsolete_depts:
            print(f"Cleaning up obsolete Department: {d.name}")
            users = db.query(User).filter(User.department_id == d.id).all()
            for u in users:
                u.department_id = None
            db.delete(d)
            
        # Obsolete Sub-Departments
        obsolete_subs = db.query(SubDepartment).filter(SubDepartment.id.notin_(valid_sub_ids)).all()
        for s in obsolete_subs:
            print(f"Cleaning up obsolete Sub-Department: {s.name}")
            users = db.query(User).filter(User.subdepartment_id == s.id).all()
            for u in users:
                u.subdepartment_id = None
            db.delete(s)

        db.commit()
        print("\n✅ Restructuring to JSON Hierarchy Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    restructure()
