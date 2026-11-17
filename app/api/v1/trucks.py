from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.truck import Truck
from app.schemas.truck import TruckCreate, TruckUpdate, TruckOut

router = APIRouter(prefix="/trucks", tags=["Trucks (Fleet Inventory)"])

@router.get("", response_model=List[TruckOut])
async def list_trucks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Truck).order_by(Truck.plate))
    return result.scalars().all()

@router.post("", response_model=TruckOut)
async def create_truck(req: TruckCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Truck).filter(Truck.plate == req.plate.strip()))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail=f"Truck with plate '{req.plate}' already exists")

    truck = Truck(
        plate=req.plate.strip(),
        model=req.model.strip(),
        capacity_tons=req.capacity_tons,
        assigned_driver_id=req.assigned_driver_id,
        status=req.status.value if hasattr(req.status, 'value') else req.status
    )
    db.add(truck)
    await db.commit()
    await db.refresh(truck)
    return truck

@router.get("/{plate}", response_model=TruckOut)
async def get_truck(plate: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Truck).filter(Truck.plate == plate.strip()))
    truck = result.scalars().first()
    if not truck:
        raise HTTPException(status_code=404, detail=f"Truck '{plate}' not found")
    return truck

@router.patch("/{plate}", response_model=TruckOut)
async def update_truck(plate: str, req: TruckUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Truck).filter(Truck.plate == plate.strip()))
    truck = result.scalars().first()
    if not truck:
        raise HTTPException(status_code=404, detail=f"Truck '{plate}' not found")

    if req.model is not None:
        truck.model = req.model
    if req.capacity_tons is not None:
        truck.capacity_tons = req.capacity_tons
    if req.status is not None:
        truck.status = req.status.value if hasattr(req.status, 'value') else req.status
    if req.assigned_driver_id is not None:
        truck.assigned_driver_id = req.assigned_driver_id

    await db.commit()
    await db.refresh(truck)
    return truck
