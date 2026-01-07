import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import SessionLocal
from app.models import Division, Department, User

def check_db():
    db = SessionLocal()
    try:
        divisions = db.query(Division).all()
        departments = db.query(Department).all()
        users = db.query(User).all()
        
        print(f"Divisions found: {len(divisions)}")
        for d in divisions:
            print(f" - {d.id}: {d.name}")
            
        print(f"\nDepartments found: {len(departments)}")
        for d in departments:
            print(f" - {d.id}: {d.name} (Division: {d.division_id})")
            
        print(f"\nUsers found: {len(users)}")
        for u in users:
            print(f" - {u.id}: {u.username} ({u.role})")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
