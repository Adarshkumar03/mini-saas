# backend/app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Check if DATABASE_URL is set
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable not set. Please create a .env file.")

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our declarative models (tables)
Base = declarative_base()

# Dependency to get a database session


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
