import json
from typing import Dict, List, Set, Any
from fastapi import WebSocket
from app.core.logging import logger

class ConnectionManager:
    def __init__(self):
        # Maps channel names (e.g. "dashboard", "alerts", "server:123") to set of active WebSockets
        self.active_channels: Dict[str, Set[WebSocket]] = {
            "dashboard": set(),
            "alerts": set()
        }
        self.all_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, channel: str = "dashboard"):
        await websocket.accept()
        self.all_connections.add(websocket)
        if channel not in self.active_channels:
            self.active_channels[channel] = set()
        self.active_channels[channel].add(websocket)
        logger.debug(f"WebSocket client connected to channel '{channel}'. Total clients: {len(self.all_connections)}")

    def disconnect(self, websocket: WebSocket, channel: str = "dashboard"):
        if websocket in self.all_connections:
            self.all_connections.remove(websocket)
        if channel in self.active_channels and websocket in self.active_channels[channel]:
            self.active_channels[channel].remove(websocket)
        logger.debug(f"WebSocket client disconnected from channel '{channel}'. Total clients: {len(self.all_connections)}")

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        if channel in self.active_channels:
            dead_sockets = set()
            payload = json.dumps(message)
            for ws in list(self.active_channels[channel]):
                try:
                    await ws.send_text(payload)
                except Exception:
                    dead_sockets.add(ws)
            for ws in dead_sockets:
                self.disconnect(ws, channel)

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        message = {
            "type": event_type,
            "data": data
        }
        # Send to dashboard & alerts channels
        await self.broadcast_to_channel("dashboard", message)
        if "ALERT" in event_type or "RECOVERED" in event_type:
            await self.broadcast_to_channel("alerts", message)

ws_manager = ConnectionManager()
