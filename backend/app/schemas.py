# backend/app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from .models import UserRole # Import UserRole Enum

# Pydantic model for creating a new user
class UserCreate(BaseModel):
    """
    Schema for user creation.
    Requires an email and a password.
    Optionally allows setting a role (defaulting to REPORTER).
    """
    email: EmailStr # EmailStr provides basic email format validation
    password: str
    role: Optional[UserRole] = UserRole.REPORTER # Default role is REPORTER

# Pydantic model for displaying user data (e.g., after creation or retrieval)
class User(BaseModel):
    """
    Schema for displaying user data.
    Includes ID, email, active status, and role.
    Note: hashed_password is NOT included for security.
    """
    id: int
    email: EmailStr
    is_active: bool
    role: UserRole # Include role in the response schema

    class Config:
        """
        Pydantic's ORM mode.
        Tells Pydantic to read the data even if it's not a dict,
        but an ORM model (or any other arbitrary object with attributes).
        """
        orm_mode = True # Deprecated in Pydantic v2, replaced by from_attributes = True
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
    role: Optional[UserRole] = None # Allow updating the role

# Pydantic model for JWT Token
class Token(BaseModel):
    """
    Schema for the JWT token response.
    """
    access_token: str
    token_type: str = "bearer"

# Pydantic model for data contained within the JWT token
class TokenData(BaseModel):
    """
    Schema for the data extracted from the JWT token payload.
    """
    email: Optional[str] = None # Subject of the token, typically user's email
