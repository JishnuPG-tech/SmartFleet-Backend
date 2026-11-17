from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.trip import Trip
from app.models.driver import Driver
from app.models.user import User
from app.schemas.earnings import EarningsSummaryOut
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/earnings", tags=["Bata Allowance & Settlements"])

@router.get("/driver/summary", response_model=EarningsSummaryOut)
async def get_driver_earnings_summary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Trip)
        .options(selectinload(Trip.pod))
        .filter(Trip.driver_id == user.id)
        .order_by(Trip.created_at.desc())
    )
    result = await db.execute(query)
    trips = result.scalars().all()

    total_earned = sum(t.allowance_amount for t in trips if t.status in ["running", "delivered"])
    settled = sum(t.allowance_amount for t in trips if t.is_paid)
    pending = total_earned - settled

    return EarningsSummaryOut(
        driver_id=user.id,
        driver_name=user.full_name,
        total_trips=len(trips),
        total_allowance_earned=total_earned,
        pending_payout_amount=pending,
        settled_payout_amount=settled,
        trips=trips
    )

@router.patch("/trips/{id}/settle")
async def settle_trip_allowance(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trip).filter(Trip.id == id.strip()))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip '{id}' not found")

    if trip.is_paid:
        return {"status": "already_settled", "trip_id": trip.id, "paid_at": trip.paid_at}

    trip.is_paid = True
    trip.paid_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "status": "success",
        "trip_id": trip.id,
        "allowance_amount": trip.allowance_amount,
        "is_paid": True,
        "paid_at": trip.paid_at
    }
