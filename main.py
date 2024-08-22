from typing import List

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

import crud
import schemas
from database import SessionLocal

app = FastAPI()


def get_db() -> Session:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Welcome to Library!"}


@app.get("/authors/", response_model=List[schemas.Author])
def read_authors_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(2, ge=1),
    db: Session = Depends(get_db)
):
    authors = crud.get_author_list(db, skip=skip, limit=limit)
    return authors


@app.post("/authors/", response_model=schemas.Author)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    db_author = crud.get_author_by_name(db=db, name=author.name)
    if db_author:
        raise HTTPException(
            status_code=400, detail="This author already exists"
        )
    return crud.create_author(db=db, author=author)


@app.get("/authors/{author_id}", response_model=schemas.Author)
def read_author_by_id(author_id: int, db: Session = Depends(get_db)):
    authors = crud.get_author_by_id(db, author_id)
    if authors is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return authors


@app.post("/authors/{author_id}/books/", response_model=schemas.Book)
def create_book_for_author(
        author_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)
):
    db_author = crud.get_author_by_id(db=db, author_id=author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")

    return crud.create_book(db=db, book=book)


@app.get("/books/", response_model=List[schemas.Book])
def read_book_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(2, ge=1),
    db: Session = Depends(get_db)
):
    books = crud.get_books_list(db, skip=skip, limit=limit)
    return books


@app.get("/authors/{author_id}/books/", response_model=List[schemas.Book])
def read_books_by_author_id(author_id: int, db: Session = Depends(get_db)):
    books = crud.get_books_by_author_id(db, author_id=author_id)
    if not books:
        raise HTTPException(
            status_code=404, detail="No books found for this author"
        )
    return books
