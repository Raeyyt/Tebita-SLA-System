"""
Restructure Organization Hierarchy based on new chart.
Syncs Divisions, Departments, and Users.
Removes obsolete units and users.
"""
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Add parent dir to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import (
    Base, User, Division, Department, SubDepartment,
    UserRole, DivisionType
)

# Setup DB
engine = create_engine("sqlite:///./tebita.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Define the Chart
# Structure: { "Division Name": { "Department Name": [ "User Role 1", "User Role 2" ] } }
# Note: "IT Department" under HR is treated as a User Role "IT Department" based on leaf node logic, 
# or we can treat it as a SubDept if we had users under it. 
# Given the prompt, "IT Department" is a leaf, so we treat it as a User (e.g. "IT Department Head" or generic user).
# Wait, "Comprehensive Ambulance Services" has "Fleet Head" etc.
# Let's use a recursive structure to be safe, but map to Div->Dept->User.

ORG_CHART = {
    "Support Division": {
        "type": DivisionType.SUPPORT,
        "departments": {
            "Finance Department": [
                "Senior Collection & Revenue Accountant",
                "Costing Accountant",
                "Store Officer",
                "Senior Payment & Disbursement Accountant",
                "Junior Accountant",
                "Cashier"
            ],
            "Human Resources (HR) Department": [
                "Office Assistance",
                "Legal Advisor",
                "Procurement",
                "IT Department", # Treated as User/Role
                "Maintenance",   # Treated as User/Role
                "Communication Officer"
            ]
        }
    },
    "EMS Division": {
        "type": DivisionType.INCOME_GENERATING,
        "departments": {
            "Comprehensive Ambulance Services": [
                "Fleet Head",
                "Ambulance Crew Head",
                "Dispatch Supervisor"
            ],
            "CPD & Short-Term Training": [
                "CPD Coordinator",
                "Short-Term Training Lead"
            ],
            "Vocational Training": [
                "Dean",
                "Vice Dean"
            ]
        }
    },
    "MEDCOM Division": {
        "type": DivisionType.INCOME_GENERATING,
        "departments": {
            "Medical Equipment Production Department": [
                "Ambulance Outfitting",
                "First Aid Kit Production"
            ],
            "Pharmaceutical Imports Department": [
                "Supplies Coordinator"
            ],
            "Marketing and Sales Department": [] # No users listed?
        }
    }
}

def normalize_username(role_name):
    # Create a username from role name: "Fleet Head" -> "fleet_head"
    return role_name.lower().replace(" ", "_").replace("&", "and").replace("-", "_").replace("(", "").replace(")", "")

def run_restructure():
    print("Starting Organization Restructure...")
    
    matched_user_ids = set()
    matched_dept_ids = set()
    matched_div_ids = set()

    # 1. Preserve Admin
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if admin:
        print(f"Preserving Admin: {admin.username}")
        matched_user_ids.add(admin.id)
    else:
        print("Creating Admin user...")
        admin = User(
            username="admin",
            full_name="System Administrator",
            email="admin@tebita.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.flush()
        matched_user_ids.add(admin.id)

    # 2. Process Chart
    for div_name, div_data in ORG_CHART.items():
        # Sync Division
        division = db.query(Division).filter(Division.name == div_name).first()
        if not division:
            print(f"Creating Division: {div_name}")
            division = Division(name=div_name, type=div_data["type"], description=div_name)
            db.add(division)
            db.flush()
        else:
            print(f"Found Division: {div_name}")
        
        matched_div_ids.add(division.id)

        for dept_name, users in div_data["departments"].items():
            # Sync Department
            department = db.query(Department).filter(Department.name == dept_name, Department.division_id == division.id).first()
            if not department:
                # Try finding by name only first (maybe moved division?)
                department = db.query(Department).filter(Department.name == dept_name).first()
                if department:
                    print(f"Moving Department {dept_name} to {div_name}")
                    department.division_id = division.id
                else:
                    print(f"Creating Department: {dept_name}")
                    department = Department(name=dept_name, division_id=division.id, description=dept_name)
                    db.add(department)
                    db.flush()
            
            matched_dept_ids.add(department.id)

            # Sync Users
            for role_name in users:
                # Check if user exists by Full Name (Role Name)
                user = db.query(User).filter(User.full_name == role_name).first()
                
                # Special mapping for known existing users to preserve them if names differ slightly
                # (Optional: add manual mapping here if needed. For now, strict match or create new)
                
                if not user:
                    # Try username match
                    username = normalize_username(role_name)
                    user = db.query(User).filter(User.username == username).first()

                if not user:
                    print(f"Creating User: {role_name} ({username})")
                    user = User(
                        username=username,
                        full_name=role_name,
                        email=f"{username}@tebita.com",
                        hashed_password=get_password_hash("password123"),
                        role=UserRole.SUB_DEPARTMENT_STAFF,
                        division_id=division.id,
                        department_id=department.id,
                        is_active=True
                    )
                    db.add(user)
                    db.flush()
                else:
                    print(f"Updating User: {user.username} -> {div_name} / {dept_name}")
                    user.division_id = division.id
                    user.department_id = department.id
                    user.full_name = role_name # Ensure exact name match
                    # Update role based on new division type
                    # But don't downgrade Admin/Leadership if they happen to match (unlikely)
                    if user.role != UserRole.ADMIN:
                         user.role = UserRole.SUB_DEPARTMENT_STAFF
                
                matched_user_ids.add(user.id)

    # 3. Cleanup
    print("\nCleaning up obsolete data...")
    
    # Remove Users
    obsolete_users = db.query(User).filter(User.id.notin_(matched_user_ids)).all()
    for u in obsolete_users:
        print(f"Removing User: {u.username} ({u.full_name})")
        # Try delete, fallback to deactivate
        try:
            db.delete(u)
            db.flush()
        except Exception as e:
            print(f"  Could not delete {u.username} (likely FK constraints). Deactivating.")
            db.rollback()
            u.is_active = False
            u.username = f"{u.username}_deleted_{u.id}" # Rename to free up username
            db.add(u)
            db.flush()

    # Remove Departments
    obsolete_depts = db.query(Department).filter(Department.id.notin_(matched_dept_ids)).all()
    for d in obsolete_depts:
        print(f"Removing Department: {d.name}")
        try:
            db.delete(d)
            db.flush()
        except:
            print(f"  Could not delete {d.name}. Skipping.")
            db.rollback()

    # Remove Divisions
    obsolete_divs = db.query(Division).filter(Division.id.notin_(matched_div_ids)).all()
    for d in obsolete_divs:
        print(f"Removing Division: {d.name}")
        try:
            db.delete(d)
            db.flush()
        except:
            print(f"  Could not delete {d.name}. Skipping.")
            db.rollback()

    db.commit()
    print("\nRestructure Complete!")

if __name__ == "__main__":
    run_restructure()
