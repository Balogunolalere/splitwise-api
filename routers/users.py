from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta
from database import users_db
from auth import get_password_hash, authenticate_user, create_access_token, get_current_user
from config import settings

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None

class User(BaseModel):
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=User)
async def register_user(user: UserCreate):
    if users_db.get(user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password
    }
    users_db.put(new_user, key=user.username)
    return User(username=user.username, email=user.email)

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return User(username=current_user["username"], email=current_user["email"])

@router.put("/me", response_model=User)
async def update_user(user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    updated_user = current_user.copy()
    if user_update.email:
        updated_user["email"] = user_update.email
    if user_update.password:
        updated_user["hashed_password"] = get_password_hash(user_update.password)
    users_db.put(updated_user, key=current_user["username"])
    return User(username=updated_user["username"], email=updated_user["email"])

@router.delete("/me")
async def delete_user(current_user: dict = Depends(get_current_user)):
    users_db.delete(current_user["username"])
    return {"message": "User deleted successfully"}
