from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.auth import verify_password
from app.config import settings

def debug_login():
    print(f"Using Database URL: {settings.database_url}")
    
    db: Session = SessionLocal()
    try:
        username = "admin"
        password = "admin"
        
        print(f"Attempting to find user: {username}")
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"ERROR: User '{username}' NOT FOUND in database.")
            return

        print(f"User found: {user.username}, Role: {user.role}, Active: {user.is_active}")
        print(f"Stored Hash: {user.hashed_password}")
        
        print(f"Verifying password '{password}'...")
        is_valid = verify_password(password, user.hashed_password)
        
        if is_valid:
            print("SUCCESS: Password verified correctly.")
        else:
            print("FAILURE: Password verification FAILED.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_login()
