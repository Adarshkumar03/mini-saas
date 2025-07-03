# backend/app/models.py

from sqlalchemy import Column, Integer, String, Boolean, Enum
# Import Base from the new database module
from .database import Base
import enum # Import enum for Python Enum type

# Define UserRole Enum
class UserRole(str, enum.Enum):
    """
    Defines the possible roles for a user in the application.
    """
    REPORTER = "REPORTER"
    MAINTAINER = "MAINTAINER"
    ADMIN = "ADMIN"

class User(Base):
    """
    SQLAlchemy model for the 'users' table.
    Represents a user in the system with authentication details and roles.
    """
    __tablename__ = "users" # Defines the table name in the database

    id = Column(Integer, primary_key=True, index=True) # Primary key, automatically increments
    email = Column(String, unique=True, index=True, nullable=False) # User's email, must be unique
    hashed_password = Column(String, nullable=False) # Stores the hashed password
    is_active = Column(Boolean, default=True) # Whether the user account is active
    # Add 'role' column with a default value of REPORTER
    role = Column(Enum(UserRole), default=UserRole.REPORTER, nullable=False)

    def __repr__(self):
        """
        String representation of the User object, useful for debugging.
        """
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

