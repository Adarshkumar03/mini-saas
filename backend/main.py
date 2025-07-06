from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
import os
from dotenv import load_dotenv
from typing import List, Dict
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Import CORS middleware
from fastapi.middleware.cors import CORSMiddleware

# Import logging configuration
from app.logging_config import configure_logging

# Import database components
from app.database import Base, engine, SessionLocal, get_db

# Import the user, issues, and dashboard routers
from app.routers import users, issues, dashboard

# Import the WebSocket manager from the new websockets module
from app.websockets import manager

# Import background tasks
from app.tasks import aggregate_daily_issue_stats

from app.init_db import init_db

# Python's built-in logging
import logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import all models to ensure they are registered with SQLAlchemy's Base
from app import models  # noqa: F401

# Initialize APScheduler
scheduler = AsyncIOScheduler()

# Lifespan context manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Configure logging first
    configure_logging()

    # Startup event
    logger.info("Application startup: Starting scheduler...")
    scheduler.add_job(aggregate_daily_issue_stats, IntervalTrigger(
        minutes=30), id='daily_issue_stats_job')
    scheduler.start()
    logger.info("Scheduler started.")
    yield
    # Shutdown event
    logger.info("Application shutdown: Shutting down scheduler...")
    scheduler.shutdown()
    logger.info("Scheduler shut down.")

# Initialize the FastAPI application with lifespan
app = FastAPI(
    title="Issues & Insights Tracker API",
    description="API for managing issues and insights within the DeepLogic AI platform.",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# --- Define any custom middleware FIRST ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(
        f"Request: {request.method} {request.url} - Headers: {dict(request.headers)}")
    response = await call_next(request)
    logger.info(
        f"Response: {request.method} {request.url} - Status: {response.status_code} - Headers: {dict(response.headers)}")
    return response

# --- Add the CORS middleware LAST so it becomes the outermost layer ---
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000",# Your SvelteKit frontend URL
    "https://mini-saas-frontend-latest.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include all your routers AFTER the middleware is configured ---
app.include_router(users.router)
app.include_router(issues.router)
app.include_router(dashboard.router)

# Example endpoint on the main app
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
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect as e:
        logger.warning(f"WebSocket disconnected: {e}")
        manager.disconnect(websocket)