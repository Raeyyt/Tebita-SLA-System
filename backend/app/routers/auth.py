from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..auth import authenticate_user, create_access_token, get_current_active_user
from ..config import settings
from .. import schemas

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    print(f"LOGIN ATTEMPT: Username='{form_data.username}', Password='{form_data.password}'")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        print(f"LOGIN FAILED: User '{form_data.username}' not found or invalid password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print(f"LOGIN SUCCESS: User '{form_data.username}' authenticated successfully")
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserRead)
async def read_users_me(current_user: schemas.UserRead = Depends(get_current_active_user)):
    return current_user
