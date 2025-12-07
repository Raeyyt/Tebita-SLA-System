from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.auth import get_password_hash
import sys

def create_subdept_users():
    db = SessionLocal()
    try:
        # Get all subdepartments
        subdepts = db.query(models.SubDepartment).all()
        print(f"Found {len(subdepts)} subdepartments.")
        
        created_users = []
        
        for sub in subdepts:
            # Create Head User
            head_username = f"{sub.name.lower().replace(' ', '_').replace('&', 'and')}_head"
            # Truncate if too long (though DB limit is usually generous)
            head_username = head_username[:50]
            
            # Check if exists
            existing = db.query(models.User).filter(models.User.username == head_username).first()
            if not existing:
                head_user = models.User(
                    email=f"{head_username}@tebita.com",
                    username=head_username,
                    full_name=f"Head of {sub.name}",
                    hashed_password=get_password_hash("password123"),
                    role=models.UserRole.SUB_DEPARTMENT_HEAD,
                    is_active=True,
                    division_id=sub.department.division_id,
                    department_id=sub.department_id,
                    subdepartment_id=sub.id
                )
                db.add(head_user)
                created_users.append({"username": head_username, "role": "HEAD", "subdept": sub.name})
                print(f"Created head user: {head_username}")
            else:
                print(f"User {head_username} already exists.")

            # Create Staff User
            staff_username = f"{sub.name.lower().replace(' ', '_').replace('&', 'and')}_staff"
            staff_username = staff_username[:50]
            
            existing_staff = db.query(models.User).filter(models.User.username == staff_username).first()
            if not existing_staff:
                staff_user = models.User(
                    email=f"{staff_username}@tebita.com",
                    username=staff_username,
                    full_name=f"Staff of {sub.name}",
                    hashed_password=get_password_hash("password123"),
                    role=models.UserRole.SUB_DEPARTMENT_STAFF,
                    is_active=True,
                    division_id=sub.department.division_id,
                    department_id=sub.department_id,
                    subdepartment_id=sub.id
                )
                db.add(staff_user)
                created_users.append({"username": staff_username, "role": "STAFF", "subdept": sub.name})
                print(f"Created staff user: {staff_username}")
            else:
                print(f"User {staff_username} already exists.")
        
        db.commit()
        
        print("\n" + "="*50)
        print("CREATED USERS SUMMARY")
        print("="*50)
        print(f"{'Username':<40} | {'Role':<10} | {'Sub-Department'}")
        print("-" * 80)
        for u in created_users:
            print(f"{u['username']:<40} | {u['role']:<10} | {u['subdept']}")
        print("="*50)
        print("Default password for all users: password123")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_subdept_users()
