from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket.manager import ws_manager
from app.core.logging import logger

router = APIRouter(tags=["WebSockets"])

@router.websocket("/ws/dashboard")
async def websocket_dashboard_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket, channel="dashboard")
    try:
        while True:
            # Keep-alive ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type": "pong"}')
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="dashboard")
    except Exception as e:
        logger.error(f"WebSocket exception on /ws/dashboard: {e}")
        ws_manager.disconnect(websocket, channel="dashboard")

@router.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket, channel="alerts")
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type": "pong"}')
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="alerts")
    except Exception as e:
        logger.error(f"WebSocket exception on /ws/alerts: {e}")
        ws_manager.disconnect(websocket, channel="alerts")
