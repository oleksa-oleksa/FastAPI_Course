import sys
sys.path.append("..")

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from starlette import status
from fastapi.templating import Jinja2Templates
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from routers import auth

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, ls=3, description="Priority must be between 0 and 3")
    complete: bool

@router.get("/test")
async def test(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request})

@router.get("/")
async def read_all(db : Session = Depends(get_db)):
    return db.query(models.Todos).all()


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()

    return templates.TemplateResponse("home.html", {"request": request, "todos": todos, "user": user})


@router.get("/todo/{todo_id}")
async def read_todo(todo_id: int, user: dict = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise auth.get_user_exception()

    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == auth.get("id")).first()

    if todo_model is not None:
        return todo_model
    raise auth.http_exception()


@router.post("/add-todo", response_class=HTMLResponse)
async def create_new_todo(request: Request, title: str = Form(...), description: str = Form(...),
                          proirity: int = Form(...), db: Session = Depends(get_db)):
    todos_model = models.Todos()
    todos_model.title = title
    todos_model.description = description
    todos_model.priority = proirity
    todos_model.complete = False
    todos_model.owner_id = 1

    db.add(todos_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)




@router.post("/")
async def create_todo(todo: Todo, user: dict = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise auth.get_user_exception()

    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return successful_response(201)

@router.put("/")
async def update_todo(todo_id: int, 
                      todo: Todo, 
                      user: dict = Depends(auth.get_current_user), 
                      db: Session = Depends(get_db)):
    
    if user is None:
        raise auth.get_user_exception()

    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == auth.get("id")).first()

    if todo_model is None:
        http_exception()
    
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add()
    db.commit()

    return successful_response(201)

@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, user: dict = Depends(auth.get_current_user), db: Session = Depends(get_db)):
     
    if user is None:
        raise auth.get_user_exception()

    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == auth.get("id")).first()


    if todo_model is None:
        http_exception()

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()

    db.commit()

    return successful_response(201)

def http_exception():
    raise HTTPException(status_code=404, detail="Todo ID not found!")

def successful_response(status_code: int):
    return {"status" : status_code,
            "transaction": "successful"}