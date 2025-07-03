# backend/app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional

# Pydantic model for creating a new user


class UserCreate(BaseModel):
    """
    Schema for user creation.
    Requires an email and a password.
    """
    email: EmailStr  # EmailStr provides basic email format validation
    password: str

# Pydantic model for displaying user data (e.g., after creation or retrieval)


class User(BaseModel):
    """
    Schema for displaying user data.
    Includes ID, email, and active status.
    Note: hashed_password is NOT included for security.
    """
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        """
        Pydantic's ORM mode.
        Tells Pydantic to read the data even if it's not a dict,
        but an ORM model (or any other arbitrary object with attributes).
        """
        orm_mode = True  # Deprecated in Pydantic v2, replaced by from_attributes = True
        # For Pydantic v2, use: from_attributes = True

# Pydantic model for updating user data (optional fields)


class UserUpdate(BaseModel):
    """
    Schema for updating user data.
    All fields are optional, allowing partial updates.
    """
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
