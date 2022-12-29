from fastapi import FastAPI
from pydantic import BaseModel 
from typing import Optional
import models
from passlib.context import CryptContext

class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

def get_password_hash(password):
    return bcrypt_context.hash(password)

@app.post("/create/user")
async def create_new_user(new_user: CreateUser):
    create_user_model = models.Users()
    create_user_model.email = new_user.email
    create_user_model.first_name = new_user.first_name
    create_user_model.last_name = new_user.last_name
    create_user_model.hashed_password = get_password_hash(new_user.password)
    create_user_model.is_active = True

    return create_user_model