# backend/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os
from dotenv import load_dotenv
from typing import List, Dict
from contextlib import asynccontextmanager # Import for lifespan management

from apscheduler.schedulers.asyncio import AsyncIOScheduler # Import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger # Import IntervalTrigger

# Import database components
from app.database import Base, engine, SessionLocal, get_db

# Import the user, issues, and dashboard routers
from app.routers import users, issues, dashboard

# Import the WebSocket manager from the new websockets module
from app.websockets import manager

# Import background tasks
from app.tasks import aggregate_daily_issue_stats # Import the background task

# Load environment variables
load_dotenv()

# Import all models to ensure they are registered with SQLAlchemy's Base
from app import models # noqa: F401

# Initialize APScheduler
scheduler = AsyncIOScheduler()

# Lifespan context manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager to handle startup and shutdown events.
    Used to start and stop the APScheduler.
    """
    # Startup event
    print("Application startup: Starting scheduler...")
    # Schedule the daily stats aggregation job
    # For testing, you can set a shorter interval (e.g., minutes=1)
    # For production, set to days=1 or a specific cron schedule
    scheduler.add_job(aggregate_daily_issue_stats, IntervalTrigger(minutes=30), id='daily_issue_stats_job')
    scheduler.start()
    print("Scheduler started.")
    yield
    # Shutdown event
    print("Application shutdown: Shutting down scheduler...")
    scheduler.shutdown()
    print("Scheduler shut down.")

# Initialize the FastAPI application with lifespan
app = FastAPI(
    title="Issues & Insights Tracker API",
    description="API for managing issues and insights within the DeepLogic AI platform.",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan # Link the lifespan context manager
)

# Include the user router
app.include_router(users.router)
# Include the issues router
app.include_router(issues.router)
# Include the dashboard router
app.include_router(dashboard.router)


# The get_db dependency is imported from app.database.
@app.get("/api/v1/hello")
async def read_root():
    return {"message": "Hello from FastAPI backend! Welcome to Issues & Insights Tracker."}

# WebSocket endpoint for real-time updates
@app.websocket("/ws/issues")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time issue updates.
    Clients connect here to receive notifications about new issues or status changes.
    """
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep the connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected from WebSocket")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

