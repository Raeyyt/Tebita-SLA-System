from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from app.auth import get_password_hash
import sys

def clean_username(name):
    """Clean name for username usage"""
    return name.lower().replace(' ', '_').replace('&', 'and').replace('(', '').replace(')', '').replace('-', '_').replace('__', '_')

def create_all_users():
    db = SessionLocal()
    try:
        print("Starting automatic user creation...")
        default_password = "password123"
        hashed_password = get_password_hash(default_password)
        
        # 1. Create Admin
        admin_username = "admin"
        if not db.query(models.User).filter(models.User.username == admin_username).first():
            admin = models.User(
                username=admin_username,
                full_name="System Administrator",
                email="admin@tebita.com",
                hashed_password=hashed_password,
                role=models.UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            print(f"Created Admin: {admin_username}")
        
        # 2. Create Division Managers
        divisions = db.query(models.Division).all()
        for div in divisions:
            username = f"{clean_username(div.name)}_manager"
            if not db.query(models.User).filter(models.User.username == username).first():
                user = models.User(
                    username=username,
                    full_name=f"Manager of {div.name}",
                    email=f"{username}@tebita.com",
                    hashed_password=hashed_password,
                    role=models.UserRole.DIVISION_MANAGER,
                    division_id=div.id,
                    is_active=True
                )
                db.add(user)
                print(f"Created Division Manager: {username}")
        
        # 3. Create Department Heads
        departments = db.query(models.Department).all()
        for dept in departments:
            username = f"{clean_username(dept.name)}_head"
            if not db.query(models.User).filter(models.User.username == username).first():
                user = models.User(
                    username=username,
                    full_name=f"Head of {dept.name}",
                    email=f"{username}@tebita.com",
                    hashed_password=hashed_password,
                    role=models.UserRole.DEPARTMENT_HEAD,
                    division_id=dept.division_id,
                    department_id=dept.id,
                    is_active=True
                )
                db.add(user)
                print(f"Created Department Head: {username}")
        
        # 4. Create Sub-Department Staff
        subdepts = db.query(models.SubDepartment).all()
        for sub in subdepts:
            username = f"{clean_username(sub.name)}_staff"
            if not db.query(models.User).filter(models.User.username == username).first():
                user = models.User(
                    username=username,
                    full_name=f"Staff of {sub.name}",
                    email=f"{username}@tebita.com",
                    hashed_password=hashed_password,
                    role=models.UserRole.SUB_DEPARTMENT_STAFF,
                    division_id=sub.department.division_id,
                    department_id=sub.department_id,
                    subdepartment_id=sub.id,
                    is_active=True
                )
                db.add(user)
                print(f"Created Sub-Department Staff: {username}")
        
        db.commit()
        print("\nAll users created successfully!")
        print(f"Default password for all new users: {default_password}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_all_users()
