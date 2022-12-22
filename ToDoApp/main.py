from fastapi import FastAPI
import models
from database import engine, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
async def create_database():
    return {"Database": "Created"}