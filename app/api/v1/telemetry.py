from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.truck import Truck
from app.models.trip import Trip
from app.models.telemetry import TelemetryLog
from app.schemas.telemetry import TelemetryPingRequest, TelemetryBroadcastPacket
from app.services.websocket_manager import manager
from app.services.tracking_service import haversine_distance

router = APIRouter(prefix="/telemetry", tags=["GPS Telemetry Ingestion"])

@router.post("/ping")
async def ingest_telemetry_ping(req: TelemetryPingRequest, db: AsyncSession = Depends(get_db)):
    # 1. Update Truck record
    result = await db.execute(select(Truck).filter(Truck.plate == req.truck_plate.strip()))
    truck = result.scalars().first()
    if not truck:
        raise HTTPException(status_code=404, detail=f"Truck '{req.truck_plate}' not found")

    now = datetime.now(timezone.utc)
    truck.last_latitude = req.latitude
    truck.last_longitude = req.longitude
    truck.last_heading = req.heading
    truck.last_speed_kmh = req.speed_kmh
    truck.last_telemetry_at = now

    # 2. If active trip, calculate progressive distance
    if req.trip_id:
        t_res = await db.execute(select(Trip).filter(Trip.id == req.trip_id.strip()))
        trip = t_res.scalars().first()
        if trip and trip.status == "running":
            dist_from_origin = haversine_distance(
                trip.origin_lat, trip.origin_lng, req.latitude, req.longitude
            )
            trip.distance_done_km = min(trip.total_distance_km, max(trip.distance_done_km, dist_from_origin))

    # 3. Log audit trail
    log = TelemetryLog(
        truck_plate=truck.plate,
        trip_id=req.trip_id,
        latitude=req.latitude,
        longitude=req.longitude,
        heading=req.heading,
        speed_kmh=req.speed_kmh,
        battery_level=req.battery_level,
        recorded_at=now
    )
    db.add(log)
    await db.commit()

    # 4. Broadcast live telemetry packet via WebSocket
    packet = {
        "type": "telemetry_update",
        "truck_plate": truck.plate,
        "trip_id": req.trip_id,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "heading": req.heading,
        "speed_kmh": req.speed_kmh,
        "timestamp": now.isoformat()
    }
    await manager.broadcast_fleet(packet)
    if req.trip_id:
        await manager.broadcast_trip(req.trip_id, packet)

    return {"status": "success", "recorded_at": now.isoformat()}
