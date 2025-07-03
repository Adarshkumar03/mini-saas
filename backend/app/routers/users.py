# backend/app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Relative imports for models, schemas, and crud
from .. import crud, models, schemas
from app.database import get_db  # Import the get_db dependency from app.database

# Create an APIRouter instance for user-related endpoints
router = APIRouter(
    prefix="/api/v1/users",  # All routes in this router will be prefixed with /api/v1/users
    tags=["Users"],  # Tags for organizing in OpenAPI documentation
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    Checks if a user with the given email already exists.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@router.get("/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all users with pagination.
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single user by ID.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """
    Update an existing user's information.
    """
    db_user = crud.update_user(db, user_id=user_id, user_update=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by ID.
    """
    result = crud.delete_user(db, user_id=user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    # FastAPI automatically handles 204 No Content for empty responses
    return
