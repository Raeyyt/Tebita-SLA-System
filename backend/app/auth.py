from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import User
from . import schemas

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    import os
    import logging
    
    # Configure logging to file
    logging.basicConfig(filename='auth_debug.log', level=logging.INFO, 
                        format='%(asctime)s - %(message)s')
    
    logging.info(f"--- AUTHENTICATE_USER CALLED ---")
    logging.info(f"CWD: {os.getcwd()}")
    logging.info(f"Username: {username}")
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        logging.error(f"User '{username}' NOT FOUND in DB")
        # Log all users in DB for debugging
        all_users = db.query(User).all()
        logging.info(f"Existing users: {[u.username for u in all_users]}")
        return None
        
    logging.info(f"User found: {user.username}, ID: {user.id}, Role: {user.role}")
    logging.info(f"Stored Hash: {user.hashed_password}")
    
    if not verify_password(password, user.hashed_password):
        logging.error("Password verification FAILED")
        return None
        
    logging.info("Authentication SUCCESS")
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
