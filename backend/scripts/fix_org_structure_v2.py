"""
Fix Organization Hierarchy v2.
Treats leaf nodes as SubDepartments AND Users.
Cleans up obsolete SubDepartments.
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
                "IT Department",
                "Maintenance",
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
            "Marketing and Sales Department": []
        }
    }
}

def normalize_username(role_name):
    return role_name.lower().replace(" ", "_").replace("&", "and").replace("-", "_").replace("(", "").replace(")", "")

def run_fix():
    print("Starting Organization Fix v2...")
    
    matched_div_ids = set()
    matched_dept_ids = set()
    matched_subdept_ids = set()
    matched_user_ids = set()

    # 1. Preserve Admin
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if admin:
        print(f"Preserving Admin: {admin.username}")
        matched_user_ids.add(admin.id)
    else:
        # Should exist from previous run, but just in case
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
        matched_div_ids.add(division.id)

        for dept_name, sub_units in div_data["departments"].items():
            # Sync Department
            department = db.query(Department).filter(Department.name == dept_name, Department.division_id == division.id).first()
            if not department:
                department = db.query(Department).filter(Department.name == dept_name).first()
                if department:
                    department.division_id = division.id
                else:
                    print(f"Creating Department: {dept_name}")
                    department = Department(name=dept_name, division_id=division.id, description=dept_name)
                    db.add(department)
                    db.flush()
            matched_dept_ids.add(department.id)

            # Sync SubDepartments (Leaf Nodes)
            for unit_name in sub_units:
                # Create/Sync SubDepartment
                subdept = db.query(SubDepartment).filter(SubDepartment.name == unit_name, SubDepartment.department_id == department.id).first()
                if not subdept:
                    print(f"Creating SubDepartment: {unit_name}")
                    subdept = SubDepartment(name=unit_name, department_id=department.id, description=unit_name)
                    db.add(subdept)
                    db.flush()
                matched_subdept_ids.add(subdept.id)

                # Create/Sync User for this SubDepartment
                username = normalize_username(unit_name)
                user = db.query(User).filter(User.username == username).first()
                
                if not user:
                    # Try finding by full name if username changed?
                    user = db.query(User).filter(User.full_name == unit_name).first()

                if not user:
                    print(f"Creating User: {unit_name} ({username})")
                    user = User(
                        username=username,
                        full_name=unit_name,
                        email=f"{username}@tebita.com",
                        hashed_password=get_password_hash("password123"),
                        role=UserRole.SUB_DEPARTMENT_STAFF,
                        division_id=division.id,
                        department_id=department.id,
                        subdepartment_id=subdept.id,
                        is_active=True
                    )
                    db.add(user)
                    db.flush()
                else:
                    # Update existing user
                    print(f"Updating User: {user.username} -> {subdept.name}")
                    user.division_id = division.id
                    user.department_id = department.id
                    user.subdepartment_id = subdept.id
                    user.full_name = unit_name
                    if user.role != UserRole.ADMIN:
                        user.role = UserRole.SUB_DEPARTMENT_STAFF
                
                matched_user_ids.add(user.id)

    # 3. Cleanup
    print("\nCleaning up obsolete data...")

    # Remove Obsolete SubDepartments
    obsolete_subs = db.query(SubDepartment).filter(SubDepartment.id.notin_(matched_subdept_ids)).all()
    for s in obsolete_subs:
        print(f"Removing SubDepartment: {s.name}")
        # Unlink users first to avoid constraint errors (though we delete users next)
        users_in_sub = db.query(User).filter(User.subdepartment_id == s.id).all()
        for u in users_in_sub:
            u.subdepartment_id = None
        db.flush()
        db.delete(s)
    
    # Remove Obsolete Users
    obsolete_users = db.query(User).filter(User.id.notin_(matched_user_ids)).all()
    for u in obsolete_users:
        print(f"Removing User: {u.username}")
        db.delete(u)

    # Remove Obsolete Departments
    obsolete_depts = db.query(Department).filter(Department.id.notin_(matched_dept_ids)).all()
    for d in obsolete_depts:
        print(f"Removing Department: {d.name}")
        db.delete(d)

    # Remove Obsolete Divisions
    obsolete_divs = db.query(Division).filter(Division.id.notin_(matched_div_ids)).all()
    for d in obsolete_divs:
        print(f"Removing Division: {d.name}")
        db.delete(d)

    db.commit()
    print("\nFix Complete!")

if __name__ == "__main__":
    run_fix()
