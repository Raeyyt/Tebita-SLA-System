from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.username == "admin").first()

if user:
    print(f"User found: {user.username}")
    print(f"Hashed password: {user.hashed_password}")
    
    # Reset password just in case
    new_hash = get_password_hash("admin123")
    user.hashed_password = new_hash
    db.commit()
    print("Password reset to 'admin123'")
else:
    print("User 'admin' NOT found!")

db.close()
