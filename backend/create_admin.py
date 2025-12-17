from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, UserRole
from app.auth import get_password_hash

def create_admin_user():
    db: Session = SessionLocal()
    try:
        # Check if admin user already exists
        user = db.query(User).filter(User.username == "admin").first()
        if user:
            print("Admin user already exists.")
            return

        # Create new admin user
        admin_user = User(
            username="admin",
            full_name="System Administrator",
            email="admin@tebita.com",
            hashed_password=get_password_hash("admin"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully.")
        print("Username: admin")
        print("Password: admin")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
