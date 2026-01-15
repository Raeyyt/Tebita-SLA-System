from app.database import SessionLocal
from app import models
import sys

def list_hierarchy():
    db = SessionLocal()
    try:
        divisions = db.query(models.Division).all()
        for div in divisions:
            print(f"Division: {div.name} (ID: {div.id})")
            depts = db.query(models.Department).filter(models.Department.division_id == div.id).all()
            for dept in depts:
                print(f"  Department: {dept.name} (ID: {dept.id})")
                subs = db.query(models.SubDepartment).filter(models.SubDepartment.department_id == dept.id).all()
                for sub in subs:
                    print(f"    Sub-Department: {sub.name} (ID: {sub.id})")
    finally:
        db.close()

if __name__ == "__main__":
    list_hierarchy()
