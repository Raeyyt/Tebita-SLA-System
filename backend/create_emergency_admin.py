from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, UserRole
from app.auth import get_password_hash
import sys

def create_emergency_admin():
    db: Session = SessionLocal()
    try:
        username = "emergency_admin"
        password = "EmergencyPassword123!"
        
        # Check if admin user already exists
        user = db.query(User).filter(User.username == username).first()
        if user:
            print(f"User '{username}' already exists. Updating password...")
            user.hashed_password = get_password_hash(password)
            user.role = UserRole.ADMIN
            user.is_active = True
        else:
            # Create new admin user
            user = User(
                username=username,
                full_name="Emergency Recovery Admin",
                email="recovery@tebita.com",
                hashed_password=get_password_hash(password),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(user)
        
        db.commit()
        print("\n" + "="*40)
        print("✅ Emergency Admin Created/Updated Successfully!")
        print("="*40)
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("="*40)
        print("\nPlease log in at the web interface and change this password immediately.")
        
    except Exception as e:
        print(f"❌ Error creating emergency admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_emergency_admin()
