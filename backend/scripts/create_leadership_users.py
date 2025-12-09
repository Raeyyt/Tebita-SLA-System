
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Division, Department, UserRole
from app.auth import get_password_hash

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./tebita.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def sanitize_username(name):
    return name.lower().replace(" ", "_").replace("&", "and").replace("-", "_").replace("__", "_").strip()

def create_leadership_users():
    print("Checking for missing leadership accounts...")
    
    # 1. Division Managers
    divisions = db.query(Division).all()
    for div in divisions:
        username = f"{sanitize_username(div.name)}_manager"
        
        existing_user = db.query(User).filter(User.username == username).first()
        if not existing_user:
            print(f"Creating Division Manager: {username} for {div.name}")
            user = User(
                username=username,
                email=f"{username}@tebita.com",
                full_name=f"{div.name} Manager",
                hashed_password=get_password_hash("password123"),
                role=UserRole.DIVISION_MANAGER,
                division_id=div.id,
                is_active=True
            )
            db.add(user)
        else:
            print(f"Division Manager exists: {username}")

    # 2. Department Heads
    departments = db.query(Department).all()
    for dept in departments:
        username = f"{sanitize_username(dept.name)}_head"
        
        existing_user = db.query(User).filter(User.username == username).first()
        if not existing_user:
            print(f"Creating Department Head: {username} for {dept.name}")
            user = User(
                username=username,
                email=f"{username}@tebita.com",
                full_name=f"{dept.name} Head",
                hashed_password=get_password_hash("password123"),
                role=UserRole.DEPARTMENT_HEAD,
                division_id=dept.division_id,
                department_id=dept.id,
                is_active=True
            )
            db.add(user)
        else:
            print(f"Department Head exists: {username}")
            
    try:
        db.commit()
        print("\nLeadership accounts created successfully!")
    except Exception as e:
        print(f"Error committing changes: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_leadership_users()
