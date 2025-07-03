# backend/app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from typing import Optional, List # Import Optional and List for type hinting

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password using the configured hashing algorithm.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    Retrieves a single user by their ID.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Retrieves a single user by their email address.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    Retrieves a list of users with pagination.
    """
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Creates a new user in the database.
    Hashes the password before storing it.
    Assigns the specified role or default REPORTER role.
    """
    hashed_password = get_password_hash(user.password)
    # Use user.role if provided, otherwise default to UserRole.REPORTER
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role if user.role else models.UserRole.REPORTER # Ensure role is set
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """
    Updates an existing user's information.
    Handles optional fields and password hashing if password is provided.
    """
    db_user: Optional[models.User] = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        if user_update.email is not None:
            db_user.email = str(user_update.email) # Explicitly cast to str
        if user_update.password is not None:
            db_user.hashed_password = get_password_hash(user_update.password)
        if user_update.is_active is not None:
            db_user.is_active = user_update.is_active
        if user_update.role is not None:
            db_user.role = user_update.role # Update role
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> Optional[dict]:
    """
    Deletes a user from the database.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    return None
