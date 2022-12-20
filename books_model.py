from fastapi import FastAPI
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

app = FastAPI()

class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str
    description: Optional[str] = Field(title="Description of the book",
                             min_length=1, 
                             max_length=100)
    rating: int = Field(ge=0)


BOOKS = []

@app.get("/")
async def read_all_books():
    return BOOKS

@app.post("/")
async def create_book(book: Book):
    BOOKS.append(book)
    return book