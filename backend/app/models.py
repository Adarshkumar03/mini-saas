# backend/app/models.py

from sqlalchemy import Column, Integer, String, Boolean
from main import Base

# Base class for our declarative models (tables)
# This Base is imported from main.py, so it's consistent across our application.
# We'll re-export it from main.py for easier import here.
# This line will be removed later when we import Base from main.py


class User(Base):
    """
    SQLAlchemy model for the 'users' table.
    Represents a user in the system with authentication details and roles.
    """
    __tablename__ = "users"  # Defines the table name in the database

    # Primary key, automatically increments
    id = Column(Integer, primary_key=True, index=True)
    # User's email, must be unique
    email = Column(String, unique=True, index=True, nullable=False)
    # Stores the hashed password
    hashed_password = Column(String, nullable=False)
    # Whether the user account is active
    is_active = Column(Boolean, default=True)
    # TODO: Add 'role' column later for RBAC (ADMIN, MAINTAINER, REPORTER)

    def __repr__(self):
        """
        String representation of the User object, useful for debugging.
        """
        return f"<User(id={self.id}, email='{self.email}')>"
