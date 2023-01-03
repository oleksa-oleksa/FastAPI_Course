import sys
sys.path.append("..")
from fastapi import Depends, HTTPException, status, APIRouter
from pydantic import BaseModel 
from typing import Optional
import models
from passlib.context import CryptContext
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWSError
from routers import auth

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"user": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class UserVerification(BaseModel):
    username: str
    old_password: str
    new_password: str

# Enhance users.py to be able to return all users within the application
@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Users).all()


# Enhance users.py to be able to get a single user by a path parameter
@router.get("/user/{user_id}")
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user_model =  db.query(models.Users).filter(models.Users.id == user_id).first()

    if user_model is not None:
        return user_model
    else:
        return "Invalid user ID!"


# Enhance users.py to be able to get a single user by a query parameter
router.get("/user/")
async def get_user_by_query(user_id: int, db: Session = Depends(get_db)):
    user_model =  db.query(models.Users).filter(models.Users.id == user_id).first()

    if user_model is not None:
        return user_model
    else:
        return "Invalid user ID!"

# Enhance users.py to be able to modify their current user's password, if passed by authentication
router.put("/user/password")
async def user_password_change(user_verification: UserVerification,
                               user: dict = Depends(auth.get_current_user),
                               db: Session = Depends(get_db)):
    if user is None:
        raise auth.get_user_exception()
    
    user_model = db.query(models.Users).filter(models.Users.id == user.get("id")).first()

    if user_model is not None:
        if user_verification.username == user_model.username and \
        auth.verify_password(user_verification.old_password, user_model.hashed_password):
            user_model.hashed_password = auth.get_password_hash(user_verification.new_password)
            db.add(user_model)
            db.commit()
            return "successful"
    return "Invalid user or request"


# Enhance users.py to be able to delete their own user.
router.delete("/user")
async def delete_own_user(user: dict = Depends(auth.get_current_user),
                          db: Session = Depends(get_db)):
    if user is None:
        raise auth.get_user_exception()
    
    user_model = db.query(models.Users).filter(models.Users.id == user.get("id")).first()

    if user_model is None:
        return "Invalid user ID!"

    db.query(models.Users).filter(models.Users.id == user.get("id")).delete()
    db.commit()

    return f"User {user.get('id')} deleted!"
