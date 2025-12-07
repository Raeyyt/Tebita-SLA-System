import sys

from app.database import SessionLocal
from app.auth import get_password_hash
from app.models import User, UserRole


def main(username: str, password: str) -> None:
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == username).first()
        if user:
            user.hashed_password = get_password_hash(password)
            user.role = UserRole.ADMIN
            user.is_active = True
            action = "updated"
        else:
            user = User(
                username=username,
                full_name=username,
                email=f"{username}@example.com",
                hashed_password=get_password_hash(password),
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(user)
            action = "created"
        session.commit()
        print(f"User '{username}' {action} successfully.")
    finally:
        session.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_admin_user.py <username> <password>")
        raise SystemExit(1)
    main(sys.argv[1], sys.argv[2])
