# backend/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os
from dotenv import load_dotenv
from typing import List, Dict # Import for type hinting

# Import database components from our new database module
from app.database import Base, engine, SessionLocal, get_db

# Import the user and issues routers
from app.routers import users, issues

# Load environment variables from .env file (already done in app.database, but harmless here)
load_dotenv()

# Import all models to ensure they are registered with SQLAlchemy's Base
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
# Include the issues router
app.include_router(issues.router)

from app.websockets import manager

# The get_db dependency is now imported from app.database.
# We keep the @app.get("/api/v1/hello") for now.
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
    await manager.connect(websocket) # Connect the client
    try:
        while True:
            # Keep the connection alive. Clients might send messages, but for now,
            # we primarily broadcast from the server.
            # You could add logic here to receive messages from clients if needed.
            await websocket.receive_text() # Wait for messages from the client (keeps connection open)
    except WebSocketDisconnect:
        manager.disconnect(websocket) # Disconnect client on WebSocketDisconnect
        print("Client disconnected from WebSocket")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

