# backend/main.py

from fastapi import FastAPI
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
    raise ValueError("DATABASE_URL environment variable not set. Please create a .env file.")

# Create the SQLAlchemy engine
# The `connect_args` are specific to SQLite, but it's good practice to include them
# if you were to switch to SQLite for testing. For PostgreSQL, they are not strictly needed
# but don't hurt.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True # Ensures connections are still alive
)

# Create a SessionLocal class
# This will be the actual database session. Each instance of SessionLocal will be a database session.
# The `autocommit=False` means that changes are not committed to the database automatically.
# The `autoflush=False` means that the session will not flush pending changes to the database
# until commit or a query is made that requires the data.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our declarative models (tables)
Base = declarative_base()

# Initialize the FastAPI application
app = FastAPI(
    title="Issues & Insights Tracker API",
    description="API for managing issues and insights within the DeepLogic AI platform.",
    version="0.1.0",
    docs_url="/api/docs", # OpenAPI documentation will be available at /api/docs
    redoc_url="/api/redoc" # ReDoc documentation will be available at /api/redoc
)

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

@app.get("/api/v1/hello")
async def read_root():
    """
    A simple endpoint to test if the API is running.
    Returns a greeting message.
    """
    return {"message": "Hello from FastAPI backend! Welcome to Issues & Insights Tracker."}

