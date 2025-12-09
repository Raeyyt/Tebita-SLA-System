import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent dir to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import User, Division, Department

# Setup DB
engine = create_engine("sqlite:///./tebita.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def list_users():
    users = db.query(User).all()
    with open("users_dump.txt", "w", encoding="utf-8") as f:
        f.write(f"{'Username':<30} | {'Role':<20} | {'Div ID':<8} | {'Dept ID':<8} | {'Full Name':<40}\n")
        f.write("-" * 120 + "\n")
        for u in users:
            f.write(f"{u.username:<30} | {str(u.role):<20} | {str(u.division_id):<8} | {str(u.department_id):<8} | {u.full_name:<40}\n")
    print("User list written to users_dump.txt")

if __name__ == "__main__":
    list_users()
