from fastapi import FastAPI
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

app = FastAPI()

class Book(BaseModel):
    id: UUID
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)
    description: Optional[str] = Field(title="Description of the book",
                             min_length=1, 
                             max_length=100)
    rating: int = Field(ge=0, le=100)

    class Config:
        schema_extra = {
            "example": {
                "id": "a9c36b90-0368-4224-a721-050805560da3",
                "title": "Ukraine is beautiful and free",
                "author": "Live Ukraine",
                "description": "This is a text",
                "rating": 50
            }
        }


BOOKS = []

@app.get("/")
async def read_all_books(books_to_return : Optional[int] = None):
    if len(BOOKS) < 1:
        create_book_no_api()

    if books_to_return and len(BOOKS) >= books_to_return > 0:
        idx = 0
        read_books = []
        while idx < books_to_return:
            read_books.append(BOOKS[idx])
            idx += 1
        return read_books

    return BOOKS

@app.get("/books/{book_id}")
async def read_book(book_id: UUID):
    for book in BOOKS:
        if book.id == book_id:
            return book


@app.post("/")
async def create_book(book: Book):
    BOOKS.append(book)
    return book


@app.put("/{book_id}")
async def update_book(book_id: UUID, book: Book):
    counter = 0
    

def create_book_no_api():
    book_1 = Book(id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
                  title = "Title_1",
                  author="Author_1",
                  description="Description_1",
                  rating=13)

    book_2 = Book(id="3fa85f64-5717-4562-b3fc-2c963f66e456",
                  title = "Title_2",
                  author="Author_2",
                  description="Description_2",
                  rating=75)   
    
    book_3 = Book(id="3fa85f64-5717-4562-b3fc-2c963f66e123",
                  title = "Title_3",
                  author="Author_3",
                  description="Description_3",
                  rating=60)   

    book_4 = Book(id="3fa85f64-5717-4562-b3fc-3e963f66e456",
                  title = "Title_4",
                  author="Author_4",
                  description="Description_4",
                  rating=67)

    BOOKS.append(book_1)
    BOOKS.append(book_2)
    BOOKS.append(book_3)
    BOOKS.append(book_4)