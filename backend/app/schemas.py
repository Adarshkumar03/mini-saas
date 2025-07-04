# backend/app/schemas.py

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from .models import UserRole, IssueStatus, IssueSeverity # Import new Enums

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

    # Pydantic V2 configuration for ORM mode
    model_config = ConfigDict(from_attributes=True)


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

# Pydantic model for creating a new issue
class IssueCreate(BaseModel):
    """
    Schema for issue creation.
    """
    title: str
    description: Optional[str] = None
    severity: Optional[IssueSeverity] = IssueSeverity.MEDIUM # Default severity
    # status is intentionally not here, as it defaults to OPEN on creation

# Pydantic model for updating an issue
class IssueUpdate(BaseModel):
    """
    Schema for updating an issue. All fields are optional.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[IssueSeverity] = None
    status: Optional[IssueStatus] = None # Status can be updated by Maintainers/Admins

# Pydantic model for displaying issue data
class Issue(BaseModel):
    """
    Schema for displaying issue data.
    Includes all relevant fields and the owner's ID.
    """
    id: int
    title: str
    description: Optional[str] = None
    severity: IssueSeverity
    status: IssueStatus
    created_at: datetime
    updated_at: datetime
    owner_id: int # The ID of the user who created this issue

    class Config:
        model_config = ConfigDict(from_attributes=True)

