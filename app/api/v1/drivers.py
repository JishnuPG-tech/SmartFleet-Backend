from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverOut

router = APIRouter(prefix="/drivers", tags=["Drivers (Fleet Personnel)"])

@router.get("", response_model=List[DriverOut])
async def list_drivers(db: AsyncSession = Depends(get_db)):
    query = select(Driver, User).join(User, Driver.id == User.id).order_by(User.full_name)
    result = await db.execute(query)
    drivers_out = []
    for d, u in result.all():
        drivers_out.append(DriverOut(
            id=d.id,
            phone=u.phone,
            full_name=u.full_name,
            license_number=d.license_number,
            experience_years=d.experience_years,
            current_truck_plate=d.current_truck_plate,
            status=d.status,
            total_trips_completed=d.total_trips_completed,
            created_at=d.created_at,
            updated_at=d.updated_at
        ))
    return drivers_out

@router.post("", response_model=DriverOut)
async def create_driver(req: DriverCreate, db: AsyncSession = Depends(get_db)):
    # Check phone or license duplicate
    existing_u = await db.execute(select(User).filter(User.phone == req.phone.strip()))
    if existing_u.scalars().first():
        raise HTTPException(status_code=400, detail="User with this phone number already exists")

    user = User(
        phone=req.phone.strip(),
        full_name=req.full_name.strip(),
        role="driver",
        is_active=True
    )
    db.add(user)
    await db.flush()

    driver = Driver(
        id=user.id,
        license_number=req.license_number.strip(),
        experience_years=req.experience_years,
        current_truck_plate=req.current_truck_plate,
        status="available"
    )
    db.add(driver)
    await db.commit()
    await db.refresh(driver)
    await db.refresh(user)

    return DriverOut(
        id=driver.id,
        phone=user.phone,
        full_name=user.full_name,
        license_number=driver.license_number,
        experience_years=driver.experience_years,
        current_truck_plate=driver.current_truck_plate,
        status=driver.status,
        total_trips_completed=driver.total_trips_completed,
        created_at=driver.created_at,
        updated_at=driver.updated_at
    )

@router.get("/{id}", response_model=DriverOut)
async def get_driver(id: str, db: AsyncSession = Depends(get_db)):
    query = select(Driver, User).join(User, Driver.id == User.id).filter(Driver.id == id)
    result = await db.execute(query)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Driver not found")
    d, u = row
    return DriverOut(
        id=d.id,
        phone=u.phone,
        full_name=u.full_name,
        license_number=d.license_number,
        experience_years=d.experience_years,
        current_truck_plate=d.current_truck_plate,
        status=d.status,
        total_trips_completed=d.total_trips_completed,
        created_at=d.created_at,
        updated_at=d.updated_at
    )
