# backend/main.py

from fastapi import FastAPI
import os
from dotenv import load_dotenv

# Import database components from our new database module
from app.database import Base, engine, SessionLocal, get_db

# Import the user router
from app.routers import users

# Load environment variables from .env file (already done in app.database, but harmless here)
load_dotenv()

# Import all models to ensure they are registered with SQLAlchemy's Base
# This import is crucial for Alembic to discover the models.
from app import models # noqa: F401

# Initialize the FastAPI application
app = FastAPI(
    title="Issues & Insights Tracker API",
    description="API for managing issues and insights within the DeepLogic AI platform.",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Include the user router
app.include_router(users.router)

# The get_db dependency is now imported from app.database.
# We keep the @app.get("/api/v1/hello") for now.
@app.get("/api/v1/hello")
async def read_root():
    return {"message": "Hello from FastAPI backend! Welcome to Issues & Insights Tracker."}

