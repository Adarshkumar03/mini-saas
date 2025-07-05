# backend/app/websockets.py

from fastapi import WebSocket
from typing import List, Any, Dict
import json # <--- Import json

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    # === MODIFIED BROADCAST METHOD ===
    async def broadcast(self, payload: Dict[str, Any]):
        """
        Broadcasts a JSON-serialized payload to all active WebSocket connections.
        """
        # Convert the dictionary payload to a JSON string
        message = json.dumps(payload)
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except RuntimeError:
                # This can happen if a connection is closing.
                # It's safe to just remove it.
                self.disconnect(connection)

manager = ConnectionManager()