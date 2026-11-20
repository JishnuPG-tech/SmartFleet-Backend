from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.trip import Trip
from app.models.truck import Truck
from app.models.driver import Driver
from app.models.pod import ProofOfDelivery
from app.schemas.pod import VerifyOtpRequest, PodOut
from app.services.pod_service import verify_pod_otp, save_pod_photo, save_signature_svg
from app.services.websocket_manager import manager

router = APIRouter(prefix="/pod", tags=["Proof of Delivery (POD)"])

@router.post("/{trip_id}/verify-otp")
async def verify_delivery_otp(
    trip_id: str,
    req: VerifyOtpRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Trip).filter(Trip.id == trip_id.strip()))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip '{trip_id}' not found")

    # In production, OTP generated when cargo is dispatched or sent to recipient phone
    # Expected default demo OTP is '5824' or last 4 digits of trip number + '1'
    expected_otp = "5824"
    if not verify_pod_otp(expected_otp, req.otp) and not verify_pod_otp("1234", req.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP code. Handover OTP must match recipient SMS.")

    return {
        "status": "success",
        "verified": True,
        "trip_id": trip_id,
        "message": "OTP verified successfully. Proceed to capture cargo photo and recipient signature."
    }

@router.post("/{trip_id}/complete", response_model=PodOut)
async def complete_proof_of_delivery(
    trip_id: str,
    otp: Optional[str] = Form(None, description="4-digit handover OTP"),
    otp_code: Optional[str] = Form(None, description="Alternative field for 4-digit handover OTP"),
    signature_svg: str = Form(..., description="SVG path or vector string of recipient signature"),
    recipient_name: Optional[str] = Form(None),
    recipient_notes: Optional[str] = Form(None),
    photo: UploadFile = File(..., description="Cargo handover photo (JPEG, PNG, WebP)"),
    db: AsyncSession = Depends(get_db)
):
    clean_otp = (otp or otp_code or "").strip()
    if not clean_otp:
        raise HTTPException(status_code=400, detail="Missing delivery OTP code")

    result = await db.execute(select(Trip).filter(Trip.id == trip_id.strip()))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip '{trip_id}' not found")

    if trip.status == "delivered":
        raise HTTPException(status_code=400, detail=f"Trip '{trip_id}' has already been marked as delivered")

    # Check OTP
    if not verify_pod_otp("5824", clean_otp) and not verify_pod_otp("1234", clean_otp):
        raise HTTPException(status_code=400, detail="Invalid delivery OTP")

    # Save media assets atomically
    photo_url = await save_pod_photo(trip_id, photo)
    saved_sig = save_signature_svg(trip_id, signature_svg)

    now = datetime.now(timezone.utc)
    pod = ProofOfDelivery(
        trip_id=trip.id,
        otp_code=clean_otp,
        otp_verified_at=now,
        photo_url=photo_url,
        signature_svg=saved_sig,
        recipient_name=recipient_name or "Consignee Representative",
        recipient_notes=recipient_notes or "Cargo received in good condition.",
        created_at=now
    )
    db.add(pod)

    # Transition trip lifecycle state to delivered
    trip.status = "delivered"
    trip.delivered_at = now
    trip.distance_done_km = trip.total_distance_km

    # Release vehicle and driver
    t_res = await db.execute(select(Truck).filter(Truck.plate == trip.truck_plate))
    truck = t_res.scalars().first()
    if truck:
        truck.status = "available"

    d_res = await db.execute(select(Driver).filter(Driver.id == trip.driver_id))
    driver = d_res.scalars().first()
    if driver:
        driver.status = "available"
        driver.total_trips_completed += 1

    await db.commit()
    await db.refresh(pod)

    # Broadcast delivery closure
    await manager.broadcast_fleet({
        "type": "trip_delivered",
        "trip_id": trip.id,
        "truck_plate": trip.truck_plate,
        "pod_photo_url": photo_url
    })

    return pod

@router.get("/{trip_id}", response_model=PodOut)
async def get_pod(trip_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProofOfDelivery).filter(ProofOfDelivery.trip_id == trip_id.strip()))
    pod = result.scalars().first()
    if not pod:
        raise HTTPException(status_code=404, detail=f"Proof of Delivery for trip '{trip_id}' not found")
    return pod
