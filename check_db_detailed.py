import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import SessionLocal
from app.models import Division, Department, SubDepartment, User

def check_db():
    db = SessionLocal()
    try:
        print("--- DIVISIONS ---")
        divisions = db.query(Division).all()
        for d in divisions:
            print(f"ID: {d.id} | Name: {d.name} | Type: {d.type}")
            
        print("\n--- DEPARTMENTS ---")
        departments = db.query(Department).all()
        for d in departments:
            print(f"ID: {d.id} | Name: {d.name} | Division ID: {d.division_id}")
            
        print("\n--- SUB-DEPARTMENTS ---")
        subdepts = db.query(SubDepartment).all()
        for s in subdepts:
            print(f"ID: {s.id} | Name: {s.name} | Department ID: {s.department_id}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
