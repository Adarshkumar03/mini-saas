# backend/app/websockets.py

from fastapi import WebSocket
from typing import List

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = [] # List to hold active WebSocket connections

    async def connect(self, websocket: WebSocket):
        await websocket.accept() # Accept the WebSocket connection
        self.active_connections.append(websocket) # Add to active connections

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket) # Remove from active connections

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message) # Send a message to a specific client

    async def broadcast(self, message: str):
        """
        Broadcasts a message to all active WebSocket connections.
        """
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except RuntimeError: # Handle cases where connection might be closing
                self.disconnect(connection) # Remove broken connection

manager = ConnectionManager() # Create an instance of the ConnectionManager
