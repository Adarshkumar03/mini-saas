# backend/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL - This should ideally come from environment variables
# For now, we'll hardcode it, but we'll improve this later with `python-dotenv`
DATABASE_URL = "postgresql://postgres:Mniaki%4022yo@localhost:5432/issues_insights_db"

# Create the SQLAlchemy engine
# `echo=True` will log all SQL statements to the console (useful for debugging)
engine = create_engine(DATABASE_URL, echo=True)

# Create a SessionLocal class
# This will be our database session factory. Each request will get its own session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base.
# All our SQLAlchemy models will inherit from this Base.
Base = declarative_base()

# Dependency to get a database session for FastAPI endpoints


def get_db():
    """
    Dependency function to provide a database session.
    It yields a session and ensures it's closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
