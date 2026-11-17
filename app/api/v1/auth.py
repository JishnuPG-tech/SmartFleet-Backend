import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.models.driver import Driver
from app.models.truck import Truck
from app.schemas.auth import (
    AdminLoginRequest,
    DriverRegisterRequest,
    DriverLoginRequest,
    DriverUpdateProfileRequest,
    LoginRequest,
    TokenResponse,
    DriverOtpRequest,
    DriverOtpVerify,
    UserProfile
)
from app.services.auth_service import (
    generate_driver_otp, verify_driver_otp_code, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication & Session"])

@router.post("/admin-login", response_model=TokenResponse)
async def admin_login(req: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    expected_username = os.environ.get("ADMIN_USERNAME", "admin").strip()
    expected_password = os.environ.get("ADMIN_PASSWORD", "SmartFleet@2026").strip()

    req_user = req.username.strip()
    req_pass = req.password.strip()

    is_valid_env_admin = (req_user == expected_username and req_pass == expected_password)

    # Check if admin user exists in DB
    result = await db.execute(select(User).filter(User.role == "admin"))
    admin_user = result.scalars().first()

    if not is_valid_env_admin:
        if admin_user and admin_user.hashed_password:
            if not verify_password(req_pass, admin_user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid admin username or password"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin username or password"
            )

    # Ensure admin user exists in DB
    if not admin_user:
        admin_user = User(
            phone="+919800000000",
            full_name="Fleet Administrator",
            role="admin",
            hashed_password=get_password_hash(expected_password),
            is_active=True
        )
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)

    token = create_access_token(
        subject=admin_user.id,
        role="admin",
        phone=admin_user.phone,
        full_name=admin_user.full_name
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role="admin",
        user_id=admin_user.id,
        phone=admin_user.phone,
        full_name=admin_user.full_name
    )

@router.post("/driver-register", response_model=TokenResponse)
async def driver_register(req: DriverRegisterRequest, db: AsyncSession = Depends(get_db)):
    clean_phone = req.phone.strip()
    # Check phone uniqueness
    res_phone = await db.execute(
        select(User).filter((User.phone == clean_phone) | (User.phone.like(f"%{clean_phone[-10:]}%")))
    )
    if res_phone.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Driver with phone {clean_phone} is already registered. Please log in."
        )

    # Check license uniqueness
    clean_lic = req.license_number.strip().upper()
    res_lic = await db.execute(
        select(Driver).filter(Driver.license_number == clean_lic)
    )
    if res_lic.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Driving license {clean_lic} is already registered."
        )

    # Create User
    new_user = User(
        phone=clean_phone,
        full_name=req.full_name.strip(),
        role="driver",
        hashed_password=get_password_hash(req.password.strip()),
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Create Driver
    clean_truck = req.assigned_truck_plate.strip().upper() if req.assigned_truck_plate else None
    driver = Driver(
        id=new_user.id,
        license_number=clean_lic,
        experience_years=req.experience_years,
        current_truck_plate=clean_truck,
        status="available",
        total_trips_completed=0
    )
    db.add(driver)

    # If truck assigned, associate driver with truck
    if clean_truck:
        t_res = await db.execute(select(Truck).filter(Truck.plate == clean_truck))
        truck = t_res.scalars().first()
        if truck:
            truck.assigned_driver_id = new_user.id

    await db.commit()

    token = create_access_token(
        subject=new_user.id,
        role="driver",
        phone=new_user.phone,
        full_name=new_user.full_name
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role="driver",
        user_id=new_user.id,
        phone=new_user.phone,
        full_name=new_user.full_name,
        license_number=clean_lic,
        assigned_truck_plate=clean_truck
    )

@router.post("/driver-login", response_model=TokenResponse)
async def driver_login(req: DriverLoginRequest, db: AsyncSession = Depends(get_db)):
    clean_phone = req.phone.strip()
    result = await db.execute(
        select(User).filter((User.phone == clean_phone) | (User.phone.like(f"%{clean_phone[-10:]}%")))
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Driver phone number not registered. Please sign up."
        )

    if not user.hashed_password or not verify_password(req.password.strip(), user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid PIN or password"
        )

    # Fetch driver profile
    d_res = await db.execute(select(Driver).filter(Driver.id == user.id))
    driver = d_res.scalars().first()

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
        full_name=user.full_name,
        license_number=driver.license_number if driver else None,
        assigned_truck_plate=driver.current_truck_plate if driver else None
    )

@router.put("/driver-profile", response_model=UserProfile)
async def update_driver_profile(
    req: DriverUpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if req.full_name:
        user.full_name = req.full_name.strip()

    d_res = await db.execute(select(Driver).filter(Driver.id == user.id))
    driver = d_res.scalars().first()

    if not driver:
        driver = Driver(
            id=user.id,
            license_number=req.license_number or f"KL-TEMP-{user.phone[-6:]}",
            experience_years=req.experience_years or 3,
            status="available"
        )
        db.add(driver)

    if req.license_number:
        driver.license_number = req.license_number.strip().upper()
    if req.experience_years is not None:
        driver.experience_years = req.experience_years
    if req.assigned_truck_plate is not None:
        driver.current_truck_plate = req.assigned_truck_plate.strip().upper() if req.assigned_truck_plate else None
        if driver.current_truck_plate:
            t_res = await db.execute(select(Truck).filter(Truck.plate == driver.current_truck_plate))
            truck = t_res.scalars().first()
            if truck:
                truck.assigned_driver_id = user.id

    await db.commit()
    await db.refresh(user)
    if driver:
        await db.refresh(driver)

    return UserProfile(
        id=user.id,
        phone=user.phone,
        full_name=user.full_name,
        role=user.role,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        license_number=driver.license_number if driver else None,
        experience_years=driver.experience_years if driver else None,
        assigned_truck_plate=driver.current_truck_plate if driver else None
    )

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
    lic_num = None
    exp_yrs = None
    if user.role == "driver":
        d_res = await db.execute(select(Driver).filter(Driver.id == user.id))
        driver = d_res.scalars().first()
        if driver:
            assigned_plate = driver.current_truck_plate
            lic_num = driver.license_number
            exp_yrs = driver.experience_years

    return UserProfile(
        id=user.id,
        phone=user.phone,
        full_name=user.full_name,
        role=user.role,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        license_number=lic_num,
        experience_years=exp_yrs,
        assigned_truck_plate=assigned_plate
    )
