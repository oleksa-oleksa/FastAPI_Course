from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel 
from typing import Optional
import models
from passlib.context import CryptContext
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWSError

SECRET_KEY = "gkjhsdnti43985ujrjkngoqewi48093rn^%$674g3jkrh3"
ALGORITHM = "HS256"

class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_password_hash(password):
    return bcrypt_context.hash(password)

def authentificate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.username == username)

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def verify_password(plain_password, hash_password):
    return bcrypt_context.verify(plain_password, hash_password)


def create_access_token(username: str, user_id: int, expires_delta = Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})

    return jwt.encode(encode, SECRET_KEY)

async def get_current_user(token: str = Depends(oauth2_bearer)):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=404, detail="User not found!")
        return {"username": username, "id": user_id}
    except JWSError:

@app.post("/create/user")
async def create_new_user(new_user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = models.Users()
    create_user_model.email = new_user.email
    create_user_model.first_name = new_user.first_name
    create_user_model.last_name = new_user.last_name
    create_user_model.hashed_password = get_password_hash(new_user.password)
    create_user_model.is_active = True

    db.add(create_new_user)
    db.commit()

@app.post("/token")
async def login_for_access_tolen(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authentificate_user(form_data.username, form_data.passsword, db)

    if not user: 
        raise HTTPException(status_code=404, detail="User not found!")
    token_expires = timedelta(minutes=20)
    token = create_access_token(user.username, 
                                user.id, 
                                expires_delta=token_expires)
    return {"token": token}

