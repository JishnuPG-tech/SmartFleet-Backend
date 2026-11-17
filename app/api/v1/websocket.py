import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import manager

router = APIRouter(tags=["Real-time Telemetry WebSockets"])

@router.websocket("/ws/v1/fleet")
async def websocket_fleet_endpoint(websocket: WebSocket):
    await manager.connect_fleet(websocket)
    try:
        while True:
            # Keepalive ping-pong
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect_fleet(websocket)
    except Exception:
        manager.disconnect_fleet(websocket)

@router.websocket("/ws/v1/trip/{trip_id}")
async def websocket_trip_endpoint(websocket: WebSocket, trip_id: str):
    await manager.connect_trip(trip_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect_trip(trip_id, websocket)
    except Exception:
        manager.disconnect_trip(trip_id, websocket)
