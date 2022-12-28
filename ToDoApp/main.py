from fastapi import FastAPI, Depends
import models
from database import engine, Base, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.get("/")
async def read_all(db : Session = Depends(get_db)):
    return db.query(models.Todos).all()

@app.get("/")
async def create_database():
    return {"Database": "Created"}