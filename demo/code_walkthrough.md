# Building a REST API with FastAPI

## Architecture Overview

- **Framework:** FastAPI with Uvicorn ASGI server
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Auth:** JWT tokens via `python-jose`
- **Validation:** Pydantic models for request and response schemas
- **Testing:** Pytest with HTTPX async test client

## Project Setup

Install dependencies and scaffold the project:

```bash
mkdir bookstore-api && cd bookstore-api
python -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose
```

Create the entry point in `main.py`:

```python
from fastapi import FastAPI
from routes import books, auth

app = FastAPI(title="Bookstore API", version="1.0.0")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(books.router, prefix="/books", tags=["Books"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

## Defining the Data Model

```python
from sqlalchemy import Column, Integer, String, Float
from database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, index=True)
    price = Column(Float, default=0.0)
    stock = Column(Integer, default=0)
```

> **Note:** Always index columns you filter or join on. The `isbn` field gets a unique index because it is our primary lookup key.

## API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Create a new user account | No |
| POST | `/auth/login` | Get a JWT access token | No |
| GET | `/books` | List all books with pagination | No |
| GET | `/books/{id}` | Get a single book by ID | No |
| POST | `/books` | Add a new book to inventory | Yes |
| PUT | `/books/{id}` | Update book details | Yes |
| DELETE | `/books/{id}` | Remove a book from inventory | Yes |

## Route Implementation

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Book
from schemas import BookCreate, BookResponse

router = APIRouter()

@router.get("/", response_model=list[BookResponse])
def list_books(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(Book).offset(skip).limit(limit).all()

@router.post("/", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    if db.query(Book).filter(Book.isbn == book.isbn).first():
        raise HTTPException(status_code=409, detail="ISBN already exists")
    new_book = Book(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book
```

## Running and Testing

Start the dev server and verify the health endpoint:

```bash
uvicorn main:app --reload --port 8000
curl http://localhost:8000/health
```

Example response:

```json
{
  "status": "ok"
}
```

> **Tip:** Visit `http://localhost:8000/docs` to explore the auto-generated Swagger UI. FastAPI builds interactive documentation from your type hints and Pydantic models for free.

## Project Checklist

- [x] Initialize project structure and virtual environment
- [x] Configure SQLAlchemy database connection
- [x] Define `Book` model and Pydantic schemas
- [x] Implement CRUD routes for `/books`
- [ ] Add JWT authentication middleware
- [ ] Write integration tests with Pytest
- [ ] Set up Alembic for database migrations
- [ ] Containerize with Docker and add CI pipeline
