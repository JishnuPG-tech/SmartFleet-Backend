import json
import logging
from typing import Dict, List, Set, Any
from fastapi import WebSocket

logger = logging.getLogger("smartfleet.websocket")

class ConnectionManager:
    """
    Manages real-time WebSocket subscriber connections for:
    1. Entire fleet live GPS streaming (/ws/v1/fleet)
    2. Single trip route tracking stream (/ws/v1/trip/{trip_id})
    """
    def __init__(self):
        # Global fleet map subscribers
        self.fleet_connections: Set[WebSocket] = set()
        # Per-trip subscribers
        self.trip_connections: Dict[str, Set[WebSocket]] = {}

    async def connect_fleet(self, websocket: WebSocket):
        await websocket.accept()
        self.fleet_connections.add(websocket)
        logger.info(f"Fleet WebSocket client connected. Active fleet listeners: {len(self.fleet_connections)}")

    def disconnect_fleet(self, websocket: WebSocket):
        self.fleet_connections.discard(websocket)
        logger.info(f"Fleet WebSocket client disconnected. Active fleet listeners: {len(self.fleet_connections)}")

    async def connect_trip(self, trip_id: str, websocket: WebSocket):
        await websocket.accept()
        if trip_id not in self.trip_connections:
            self.trip_connections[trip_id] = set()
        self.trip_connections[trip_id].add(websocket)
        logger.info(f"Trip [{trip_id}] WebSocket client connected. Active: {len(self.trip_connections[trip_id])}")

    def disconnect_trip(self, trip_id: str, websocket: WebSocket):
        if trip_id in self.trip_connections:
            self.trip_connections[trip_id].discard(websocket)
            if not self.trip_connections[trip_id]:
                del self.trip_connections[trip_id]
        logger.info(f"Trip [{trip_id}] WebSocket client disconnected.")

    async def broadcast_fleet(self, message: Dict[str, Any]):
        """Broadcast live telemetry packet or alert to all fleet map listeners"""
        payload = json.dumps(message, default=str)
        dead_connections = []
        for connection in list(self.fleet_connections):
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Error sending to fleet WS: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.fleet_connections.discard(dead)

    async def broadcast_trip(self, trip_id: str, message: Dict[str, Any]):
        """Broadcast status or progress packet to specific trip listeners"""
        if trip_id not in self.trip_connections:
            return

        payload = json.dumps(message, default=str)
        dead_connections = []
        for connection in list(self.trip_connections[trip_id]):
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Error sending to trip [{trip_id}] WS: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.trip_connections[trip_id].discard(dead)

manager = ConnectionManager()
