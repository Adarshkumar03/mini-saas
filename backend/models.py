# backend/models.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from database import Base  # Import Base from our database setup


class User(Base):
    """
    SQLAlchemy model for a User.
    This model represents the 'users' table in the database.
    """
    __tablename__ = "users"  # Define the table name

    # Primary key, indexed for quick lookups
    id = Column(Integer, primary_key=True, index=True)
    # User's email, must be unique and not null
    email = Column(String, unique=True, index=True, nullable=False)
    # Hashed password for security
    hashed_password = Column(String, nullable=False)
    # Whether the user account is active
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())  # Timestamp of creation
    # Timestamp of last update
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        """
        String representation of the User object, useful for debugging.
        """
        return f"<User(id={self.id}, email='{self.email}')>"
