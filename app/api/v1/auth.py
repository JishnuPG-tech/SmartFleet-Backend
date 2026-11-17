from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.models.driver import Driver
from app.schemas.auth import (
    LoginRequest, TokenResponse, DriverOtpRequest, DriverOtpVerify, UserProfile
)
from app.services.auth_service import (
    generate_driver_otp, verify_driver_otp_code, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication & Session"])

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    phone_clean = req.phone.strip()
    result = await db.execute(select(User).filter((User.phone == phone_clean) | (User.phone.like(f"%{phone_clean[-10:]}%"))))
    user = result.scalars().first()
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password"
        )

    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password"
        )

    token = create_access_token(
        subject=user.id,
        role=user.role,
        phone=user.phone,
        full_name=user.full_name
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        phone=user.phone,
        full_name=user.full_name
    )

@router.post("/driver-otp-request")
async def request_driver_otp(req: DriverOtpRequest):
    otp = generate_driver_otp(req.phone)
    return {
        "status": "success",
        "message": f"4-digit OTP sent successfully to {req.phone}",
        "otp_debug": otp
    }

@router.post("/driver-otp-verify", response_model=TokenResponse)
async def verify_driver_otp(req: DriverOtpVerify, db: AsyncSession = Depends(get_db)):
    if not verify_driver_otp_code(req.phone, req.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code")

    phone_clean = req.phone.strip()
    result = await db.execute(select(User).filter((User.phone == phone_clean) | (User.phone.like(f"%{phone_clean[-10:]}%"))))
    user = result.scalars().first()

    if not user:
        # Auto-create driver user if first time
        user = User(
            phone=phone_clean,
            full_name=f"Driver {phone_clean[-4:]}",
            role="driver",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        driver = Driver(
            id=user.id,
            license_number=f"KL-TEMP-{phone_clean[-6:]}",
            experience_years=3,
            status="available"
        )
        db.add(driver)
        await db.commit()

    token = create_access_token(
        subject=user.id,
        role="driver",
        phone=user.phone,
        full_name=user.full_name
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role="driver",
        user_id=user.id,
        phone=user.phone,
        full_name=user.full_name
    )

@router.get("/me", response_model=UserProfile)
async def get_me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    assigned_plate = None
    if user.role == "driver":
        d_res = await db.execute(select(Driver).filter(Driver.id == user.id))
        driver = d_res.scalars().first()
        if driver:
            assigned_plate = driver.current_truck_plate

    return UserProfile(
        id=user.id,
        phone=user.phone,
        full_name=user.full_name,
        role=user.role,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        assigned_truck_plate=assigned_plate
    )
