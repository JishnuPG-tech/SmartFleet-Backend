import random
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.trip import Trip
from app.models.truck import Truck
from app.models.driver import Driver
from app.models.user import User
from app.models.alert import OperationalAlert
from app.schemas.trip import TripCreate, TripUpdateStatus, TripOut, TripBreakdownRequest
from app.services.auth_service import get_current_user
from app.services.websocket_manager import manager

router = APIRouter(prefix="/trips", tags=["Trips & Freight Dispatch"])

@router.get("", response_model=List[TripOut])
async def list_trips(
    status: Optional[str] = Query(None, description="Filter by trip status (waiting, accepted, running, breakdown, delivered, failed)"),
    driver_id: Optional[str] = Query(None, description="Filter by assigned driver ID"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Trip).options(selectinload(Trip.pod)).order_by(Trip.created_at.desc())
    if status:
        query = query.filter(Trip.status == status.strip().lower())
    if driver_id:
        query = query.filter(Trip.driver_id == driver_id.strip())
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=TripOut)
async def create_trip(req: TripCreate, db: AsyncSession = Depends(get_db)):
    # Verify truck plate
    t_res = await db.execute(select(Truck).filter(Truck.plate == req.truck_plate.strip()))
    truck = t_res.scalars().first()
    if not truck:
        raise HTTPException(status_code=404, detail=f"Truck '{req.truck_plate}' not found")

    # Generate sequential or unique trip ID
    num = random.randint(1030, 9999)
    trip_id = f"TR-{num}"

    trip = Trip(
        id=trip_id,
        origin_city=req.origin_city,
        origin_code=req.origin_code or "COK",
        origin_lat=req.origin_lat or 9.9312,
        origin_lng=req.origin_lng or 76.2673,
        dest_city=req.dest_city,
        dest_code=req.dest_code or "CCJ",
        dest_lat=req.dest_lat or 11.2588,
        dest_lng=req.dest_lng or 75.7804,
        cargo_title=req.cargo_title,
        weight_tons=req.weight_tons,
        truck_plate=req.truck_plate.strip(),
        driver_id=req.driver_id,
        status="waiting",
        scheduled_start=req.scheduled_start or datetime.now(timezone.utc),
        total_distance_km=req.total_distance_km or 180.0,
        distance_done_km=0.0,
        allowance_amount=req.allowance_amount
    )
    db.add(trip)

    # Lock truck and driver to this trip
    truck.status = "on_trip"
    truck.assigned_driver_id = req.driver_id

    d_res = await db.execute(select(Driver).filter(Driver.id == req.driver_id))
    driver = d_res.scalars().first()
    if driver:
        driver.status = "on_trip"
        driver.current_truck_plate = req.truck_plate.strip()

    await db.commit()
    res = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.id == trip.id))
    trip_loaded = res.scalars().first()

    # Broadcast new trip dispatch
    await manager.broadcast_fleet({
        "type": "trip_created",
        "trip_id": trip.id,
        "truck_plate": trip.truck_plate,
        "driver_id": trip.driver_id,
        "status": trip.status,
        "origin": trip.origin_city,
        "dest": trip.dest_city,
        "cargo": trip.cargo_title
    })

    return trip_loaded

@router.get("/driver/active", response_model=Optional[TripOut])
async def get_driver_active_trip(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Trip)
        .options(selectinload(Trip.pod))
        .filter(Trip.driver_id == user.id, Trip.status.in_(["waiting", "accepted", "running", "breakdown"]))
        .order_by(Trip.created_at.desc())
        .limit(1)
    )
    res = await db.execute(query)
    trip = res.scalars().first()
    return trip_loaded

@router.get("/{id}", response_model=TripOut)
async def get_trip(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.id == id.strip()))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip '{id}' not found")
    return trip_loaded

@router.post("/{id}/accept", response_model=TripOut)
async def accept_trip(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.id == id.strip()))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip '{id}' not found")

    trip.status = "accepted"
    await db.commit()
    res = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.id == trip.id))
    trip_loaded = res.scalars().first()

    await manager.broadcast_fleet({
        "type": "trip_accepted",
        "trip_id": trip.id,
        "truck_plate": trip.truck_plate,
        "driver_id": trip.driver_id,
        "status": "accepted"
    })
    return trip_loaded

@router.post("/{id}/start", response_model=TripOut)
async def start_trip(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.id == id.strip()))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip '{id}' not found")

    now = datetime.now(timezone.utc)
    trip.status = "running"
    if not trip.actual_started_at:
        trip.actual_started_at = now

    t_res = await db.execute(select(Truck).filter(Truck.plate == trip.truck_plate))
    truck = t_res.scalars().first()
    if truck:
        truck.status = "on_trip"

    await db.commit()
    res = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.id == trip.id))
    trip_loaded = res.scalars().first()

    await manager.broadcast_fleet({
        "type": "trip_started",
        "trip_id": trip.id,
        "truck_plate": trip.truck_plate,
        "driver_id": trip.driver_id,
        "status": "running",
        "actual_started_at": now.isoformat()
    })
    return trip_loaded

@router.post("/{id}/breakdown", response_model=TripOut)
async def report_breakdown(id: str, req: TripBreakdownRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.id == id.strip()))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip '{id}' not found")

    now = datetime.now(timezone.utc)
    trip.status = "breakdown"

    # Update truck location and status
    t_res = await db.execute(select(Truck).filter(Truck.plate == trip.truck_plate))
    truck = t_res.scalars().first()
    if truck:
        truck.status = "breakdown"
        truck.last_latitude = req.latitude
        truck.last_longitude = req.longitude
        truck.last_telemetry_at = now

    # Create high-priority operational alert
    alert = OperationalAlert(
        truck_plate=trip.truck_plate,
        trip_id=trip.id,
        severity="danger",
        title=f"🚨 Vehicle Breakdown: {trip.truck_plate}",
        description=f"Driver reported '{req.reason}' during Trip {trip.id} ({trip.origin_city} ➔ {trip.dest_city}). GPS: {req.latitude:.4f}, {req.longitude:.4f}. {req.remarks or ''}".strip(),
        created_at=now
    )
    db.add(alert)
    await db.commit()
    res = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.id == trip.id))
    trip_loaded = res.scalars().first()

    # Broadcast emergency alert
    await manager.broadcast_fleet({
        "type": "trip_breakdown",
        "trip_id": trip.id,
        "truck_plate": trip.truck_plate,
        "driver_id": trip.driver_id,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "reason": req.reason,
        "alert_title": alert.title
    })

    return trip_loaded

@router.post("/{id}/fail", response_model=TripOut)
async def report_delivery_failed(id: str, remarks: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.id == id.strip()))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip '{id}' not found")

    now = datetime.now(timezone.utc)
    trip.status = "failed"

    t_res = await db.execute(select(Truck).filter(Truck.plate == trip.truck_plate))
    truck = t_res.scalars().first()
    if truck:
        truck.status = "available"

    alert = OperationalAlert(
        truck_plate=trip.truck_plate,
        trip_id=trip.id,
        severity="warning",
        title=f"⚠️ Delivery Incomplete: {trip.id}",
        description=f"Consignment delivery failed ({trip.origin_city} ➔ {trip.dest_city}). Reason: {remarks or 'Consignee unavailable / rejected'}",
        created_at=now
    )
    db.add(alert)
    await db.commit()
    res = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.id == trip.id))
    trip_loaded = res.scalars().first()

    await manager.broadcast_fleet({
        "type": "trip_failed",
        "trip_id": trip.id,
        "truck_plate": trip.truck_plate,
        "status": "failed"
    })
    return trip_loaded

@router.patch("/{id}/status", response_model=TripOut)
async def update_trip_status(id: str, req: TripUpdateStatus, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.id == id.strip()))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip '{id}' not found")

    new_status = req.status.value if hasattr(req.status, 'value') else req.status
    trip.status = new_status
    now = datetime.now(timezone.utc)

    if new_status == "running" and not trip.actual_started_at:
        trip.actual_started_at = now
    elif new_status == "delivered":
        trip.delivered_at = now
        trip.distance_done_km = trip.total_distance_km
        # Release truck and driver
        t_res = await db.execute(select(Truck).filter(Truck.plate == trip.truck_plate))
        truck = t_res.scalars().first()
        if truck:
            truck.status = "available"

        d_res = await db.execute(select(Driver).filter(Driver.id == trip.driver_id))
        driver = d_res.scalars().first()
        if driver:
            driver.status = "available"
            driver.total_trips_completed += 1

    if req.distance_done_km is not None:
        trip.distance_done_km = min(trip.total_distance_km, req.distance_done_km)

    await db.commit()
    res = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.id == trip.id))
    trip_loaded = res.scalars().first()

    packet = {
        "type": "trip_status_changed",
        "trip_id": trip.id,
        "truck_plate": trip.truck_plate,
        "status": trip.status,
        "distance_done_km": trip.distance_done_km
    }
    await manager.broadcast_fleet(packet)
    await manager.broadcast_trip(trip.id, packet)

    return trip_loaded
