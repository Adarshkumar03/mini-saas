# backend/app/models.py

from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
# Import Base from the new database module
from .database import Base
import enum
from datetime import datetime

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
    role = Column(Enum(UserRole), default=UserRole.REPORTER, nullable=False)

    # Relationship to issues created by this user
    issues = relationship("Issue", back_populates="owner") # This is correct

    def __repr__(self):
        """
        String representation of the User object, useful for debugging.
        """
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

# Define IssueStatus Enum
class IssueStatus(str, enum.Enum):
    """
    Defines the possible statuses for an issue.
    """
    OPEN = "OPEN"
    TRIAGED = "TRIAGED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

# Define IssueSeverity Enum
class IssueSeverity(str, enum.Enum):
    """
    Defines the possible severity levels for an issue.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Issue(Base):
    """
    SQLAlchemy model for the 'issues' table.
    Represents an issue (bug report, feedback, etc.) in the system.
    """
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True) # Text for longer content (Markdown)
    severity = Column(Enum(IssueSeverity), default=IssueSeverity.MEDIUM, nullable=False)
    status = Column(Enum(IssueStatus), default=IssueStatus.OPEN, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Foreign key to link to the User who created the issue
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="issues")

    def __repr__(self):
        """
        String representation of the Issue object.
        """
        return f"<Issue(id={self.id}, title='{self.title}', status='{self.status}', owner_id={self.owner_id})>"

class DailyStats(Base):
    """
    SQLAlchemy model for the 'daily_stats' table.
    Stores aggregated issue counts by status for a given date.
    """
    __tablename__ = "daily_stats"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, unique=True) # Date for which stats are aggregated
    issue_counts_by_status = Column(JSON, nullable=False) # Stores a JSON object of counts by status

    def __repr__(self):
        return f"<DailyStats(id={self.id}, date='{self.date.strftime('%Y-%m-%d')}', counts={self.issue_counts_by_status})>"

