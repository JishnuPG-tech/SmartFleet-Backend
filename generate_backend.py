import os
import sys

base_dir = "/data/antigravity/smartfleet_backend"
os.makedirs(os.path.join(base_dir, "app/core"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "app/models"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "app/schemas"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "app/services"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "app/api/v1"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "app/db"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "app/uploads/pod"), exist_ok=True)

files = {}

# 1. app/__init__.py
files["app/__init__.py"] = '"""SmartFleet 2.0 Backend"""\n'
files["app/core/__init__.py"] = '"""Core config and database"""\n'
files["app/models/__init__.py"] = '''from app.models.base import Base, TimestampMixin
from app.models.user import User
from app.models.driver import Driver
from app.models.truck import Truck
from app.models.trip import Trip
from app.models.pod import ProofOfDelivery
from app.models.telemetry import TelemetryLog
from app.models.alert import OperationalAlert
'''

# 2. app/core/config.py
files["app/core/config.py"] = '''from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartFleet 2.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite+aiosqlite:////data/antigravity/smartfleet_backend/smartfleet.db"
    DB_ECHO: bool = False
    JWT_SECRET: str = "smartfleet-dev-secret-key-change-in-prod-nh66-kerala-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    BASE_DIR: str = "/data/antigravity/smartfleet_backend"
    UPLOAD_DIR: str = "/data/antigravity/smartfleet_backend/app/uploads"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL
        # In cloud containers, DATABASE_URL might be pre-set with sync driver 'sqlite:///' or 'postgresql://'
        # Convert to async drivers (aiosqlite or asyncpg) for SQLAlchemy asyncio
        if url.startswith("sqlite:///"):
            return url.replace("sqlite:///", "sqlite+aiosqlite:///")
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://")
        if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql://", "postgresql+asyncpg://")
        return url

settings = Settings()
'''

# 3. app/core/security.py
files["app/core/security.py"] = '''import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import jwt
from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def create_access_token(
    subject: Union[str, Any],
    role: str = "driver",
    phone: str = "",
    full_name: str = "",
    expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(subject),
        "role": role,
        "phone": phone,
        "full_name": full_name,
        "exp": expire
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception:
        return None
'''

# 4. app/core/database.py
files["app/core/database.py"] = '''import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.models.base import Base

connect_args = {}
if "sqlite" in settings.async_database_url:
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DB_ECHO,
    future=True,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    import app.models  # Ensure all models are loaded
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
'''

# 5. app/models/base.py
files["app/models/base.py"] = '''from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
'''

# 6. app/models/user.py
files["app/models/user.py"] = '''import uuid
from typing import Optional
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="driver", nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    driver_profile: Mapped[Optional["Driver"]] = relationship("Driver", back_populates="user", uselist=False, cascade="all, delete-orphan")
'''

# 7. app/models/driver.py
files["app/models/driver.py"] = '''from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class Driver(Base, TimestampMixin):
    __tablename__ = "drivers"

    id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    license_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_truck_plate: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="available", nullable=False)
    total_trips_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="driver_profile")
    trips: Mapped[List["Trip"]] = relationship("Trip", back_populates="driver")
'''

# 8. app/models/truck.py
files["app/models/truck.py"] = '''from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class Truck(Base, TimestampMixin):
    __tablename__ = "trucks"

    plate: Mapped[str] = mapped_column(String(20), primary_key=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity_tons: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="available", index=True, nullable=False)
    assigned_driver_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True)
    
    last_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_heading: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_speed_kmh: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_telemetry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    trips: Mapped[List["Trip"]] = relationship("Trip", back_populates="truck")
    telemetry_logs: Mapped[List["TelemetryLog"]] = relationship("TelemetryLog", back_populates="truck")
    alerts: Mapped[List["OperationalAlert"]] = relationship("OperationalAlert", back_populates="truck")
'''

# 9. app/models/trip.py
files["app/models/trip.py"] = '''from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class Trip(Base, TimestampMixin):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    origin_city: Mapped[str] = mapped_column(String(100), nullable=False)
    origin_code: Mapped[str] = mapped_column(String(10), nullable=False)
    origin_lat: Mapped[float] = mapped_column(Float, nullable=False)
    origin_lng: Mapped[float] = mapped_column(Float, nullable=False)
    dest_city: Mapped[str] = mapped_column(String(100), nullable=False)
    dest_code: Mapped[str] = mapped_column(String(10), nullable=False)
    dest_lat: Mapped[float] = mapped_column(Float, nullable=False)
    dest_lng: Mapped[float] = mapped_column(Float, nullable=False)
    cargo_title: Mapped[str] = mapped_column(String(150), nullable=False)
    weight_tons: Mapped[float] = mapped_column(Float, nullable=False)
    
    truck_plate: Mapped[str] = mapped_column(String(20), ForeignKey("trucks.plate"), index=True, nullable=False)
    driver_id: Mapped[str] = mapped_column(String(36), ForeignKey("drivers.id"), index=True, nullable=False)
    
    status: Mapped[str] = mapped_column(String(20), default="waiting", index=True, nullable=False)
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    actual_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    total_distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    distance_done_km: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    allowance_amount: Mapped[int] = mapped_column(Integer, default=1500, nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    truck: Mapped["Truck"] = relationship("Truck", back_populates="trips")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="trips")
    pod: Mapped[Optional["ProofOfDelivery"]] = relationship("ProofOfDelivery", back_populates="trip", uselist=False, cascade="all, delete-orphan")
'''

# 10. app/models/pod.py
files["app/models/pod.py"] = '''import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class ProofOfDelivery(Base):
    __tablename__ = "proof_of_delivery"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id: Mapped[str] = mapped_column(String(20), ForeignKey("trips.id", ondelete="CASCADE"), unique=True, nullable=False)
    otp_code: Mapped[str] = mapped_column(String(10), nullable=False)
    otp_verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    photo_url: Mapped[str] = mapped_column(Text, nullable=False)
    signature_svg: Mapped[str] = mapped_column(Text, nullable=False)
    recipient_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    recipient_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    trip: Mapped["Trip"] = relationship("Trip", back_populates="pod")
'''

# 11. app/models/telemetry.py
files["app/models/telemetry.py"] = '''from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    truck_plate: Mapped[str] = mapped_column(String(20), ForeignKey("trucks.plate"), index=True, nullable=False)
    trip_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("trips.id", ondelete="SET NULL"), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    heading: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    speed_kmh: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    battery_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    truck: Mapped["Truck"] = relationship("Truck", back_populates="telemetry_logs")
'''

# 12. app/models/alert.py
files["app/models/alert.py"] = '''import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class OperationalAlert(Base):
    __tablename__ = "operational_alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    truck_plate: Mapped[str] = mapped_column(String(20), ForeignKey("trucks.plate"), index=True, nullable=False)
    trip_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("trips.id", ondelete="SET NULL"), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="warning", nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    truck: Mapped["Truck"] = relationship("Truck", back_populates="alerts")
'''

# 13. app/db/seed.py
files["app/db/seed.py"] = '''import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.driver import Driver
from app.models.truck import Truck
from app.models.trip import Trip
from app.models.pod import ProofOfDelivery
from app.models.alert import OperationalAlert

async def seed_data():
    await init_db()
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        res = await session.execute(select(User).limit(1))
        if res.scalars().first():
            print("Database already contains data. Skipping initial seeding.")
            return

        print("Seeding SmartFleet database with Kerala operational fleet...")

        # 1. Admin User
        admin_user = User(
            phone="+91 98950 00000",
            full_name="Fleet Manager (Kochi HQ)",
            role="admin",
            hashed_password=get_password_hash("1234"),
            avatar_url=None,
            is_active=True
        )
        session.add(admin_user)

        # 2. Drivers (Users + Driver Profile)
        drivers_data = [
            {
                "phone": "+91 94471 23456",
                "name": "Suresh Kumar",
                "license": "KL-07-2015-008912",
                "exp": 12,
                "truck": "KL 11 AB 1234",
                "status": "on_trip"
            },
            {
                "phone": "+91 98460 78901",
                "name": "Rajesh Varma",
                "license": "KL-11-2018-004521",
                "exp": 8,
                "truck": "KL 07 CD 5678",
                "status": "available"
            },
            {
                "phone": "+91 97455 11223",
                "name": "Biju Pavithran",
                "license": "KL-01-2012-009943",
                "exp": 15,
                "truck": "KL 09 EF 9012",
                "status": "available"
            },
        ]

        driver_objs = []
        for d in drivers_data:
            u = User(
                phone=d["phone"],
                full_name=d["name"],
                role="driver",
                hashed_password=get_password_hash("1234"),
                is_active=True
            )
            session.add(u)
            await session.flush()

            dp = Driver(
                id=u.id,
                license_number=d["license"],
                experience_years=d["exp"],
                current_truck_plate=d["truck"],
                status=d["status"],
                total_trips_completed=48 if d["name"] == "Suresh Kumar" else 32
            )
            session.add(dp)
            driver_objs.append(dp)

        # 3. Kerala Commercial Trucks
        trucks_data = [
            {
                "plate": "KL 11 AB 1234",
                "model": "BharatBenz 2823R",
                "capacity": 28.0,
                "status": "on_trip",
                "driver_id": driver_objs[0].id,
                "lat": 10.5276,
                "lng": 76.2144,
                "heading": 348.0,
                "speed": 42.5
            },
            {
                "plate": "KL 07 CD 5678",
                "model": "Tata Prima 3530.K",
                "capacity": 35.0,
                "status": "available",
                "driver_id": driver_objs[1].id,
                "lat": 9.9312,
                "lng": 76.2673,
                "heading": 0.0,
                "speed": 0.0
            },
            {
                "plate": "KL 09 EF 9012",
                "model": "Ashok Leyland 4220",
                "capacity": 42.0,
                "status": "available",
                "driver_id": driver_objs[2].id,
                "lat": 10.7867,
                "lng": 76.6548,
                "heading": 0.0,
                "speed": 0.0
            },
            {
                "plate": "KL 14 GH 3456",
                "model": "Eicher Pro 6028",
                "capacity": 28.0,
                "status": "in_workshop",
                "driver_id": None,
                "lat": 11.2588,
                "lng": 75.7804,
                "heading": 0.0,
                "speed": 0.0
            }
        ]

        for t in trucks_data:
            tr = Truck(
                plate=t["plate"],
                model=t["model"],
                capacity_tons=t["capacity"],
                status=t["status"],
                assigned_driver_id=t["driver_id"],
                last_latitude=t["lat"],
                last_longitude=t["lng"],
                last_heading=t["heading"],
                last_speed_kmh=t["speed"],
                last_telemetry_at=datetime.now(timezone.utc)
            )
            session.add(tr)

        # 4. Trips
        now = datetime.now(timezone.utc)
        # Running Trip
        trip_running = Trip(
            id="TR-1025",
            origin_city="Kochi Port",
            origin_code="COK",
            origin_lat=9.9312,
            origin_lng=76.2673,
            dest_city="Kozhikode Hub",
            dest_code="CCJ",
            dest_lat=11.2588,
            dest_lng=75.7804,
            cargo_title="24.5T Industrial Steel",
            weight_tons=24.5,
            truck_plate="KL 11 AB 1234",
            driver_id=driver_objs[0].id,
            status="running",
            scheduled_start=now - timedelta(hours=3),
            actual_started_at=now - timedelta(hours=2, minutes=45),
            total_distance_km=180.0,
            distance_done_km=76.5,
            allowance_amount=1500,
            is_paid=False
        )
        session.add(trip_running)

        # Waiting Trip
        trip_waiting = Trip(
            id="TR-1026",
            origin_city="Ernakulam Goods Yard",
            origin_code="ERS",
            origin_lat=9.9816,
            origin_lng=76.2999,
            dest_city="Thiruvananthapuram Central",
            dest_code="TRV",
            dest_lat=8.5241,
            dest_lng=76.9366,
            cargo_title="32T Cement Bags",
            weight_tons=32.0,
            truck_plate="KL 07 CD 5678",
            driver_id=driver_objs[1].id,
            status="waiting",
            scheduled_start=now + timedelta(hours=5),
            total_distance_km=215.0,
            distance_done_km=0.0,
            allowance_amount=1500,
            is_paid=False
        )
        session.add(trip_waiting)

        # Delivered Trip with POD
        trip_delivered = Trip(
            id="TR-1024",
            origin_city="Kannur Depot",
            origin_code="CAN",
            origin_lat=11.8745,
            origin_lng=75.3704,
            dest_city="Kozhikode Port",
            dest_code="CCJ",
            dest_lat=11.2588,
            dest_lng=75.7804,
            cargo_title="18T Ceramic Tiles",
            weight_tons=18.0,
            truck_plate="KL 09 EF 9012",
            driver_id=driver_objs[2].id,
            status="delivered",
            scheduled_start=now - timedelta(days=1, hours=6),
            actual_started_at=now - timedelta(days=1, hours=5),
            delivered_at=now - timedelta(days=1, hours=1),
            total_distance_km=90.0,
            distance_done_km=90.0,
            allowance_amount=1200,
            is_paid=True,
            paid_at=now - timedelta(hours=18)
        )
        session.add(trip_delivered)
        await session.flush()

        pod = ProofOfDelivery(
            trip_id="TR-1024",
            otp_code="5824",
            otp_verified_at=now - timedelta(days=1, hours=1),
            photo_url="/uploads/pod/sample_cargo_pod.jpg",
            signature_svg="<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 100'><path d='M20 50 Q 80 10 140 60 T 180 40' fill='none' stroke='#000' stroke-width='2'/></svg>",
            recipient_name="K. Ramanathan (Warehouse Supervisor)",
            recipient_notes="All 18T ceramic tiles verified undamaged."
        )
        session.add(pod)

        # 5. Operational Alerts
        alerts_data = [
            {
                "plate": "KL 14 GH 3456",
                "trip_id": None,
                "severity": "urgent",
                "title": "Brake System Air Pressure Low",
                "description": "Vehicle in Kozhikode workshop pending master cylinder replacement."
            },
            {
                "plate": "KL 11 AB 1234",
                "trip_id": "TR-1025",
                "severity": "warning",
                "title": "NH-66 Heavy Traffic Near Edappally",
                "description": "Speed dropped to 18 km/h. Estimated ETA delayed by +25 mins."
            }
        ]

        for a in alerts_data:
            al = OperationalAlert(
                truck_plate=a["plate"],
                trip_id=a["trip_id"],
                severity=a["severity"],
                title=a["title"],
                description=a["description"],
                is_resolved=False
            )
            session.add(al)

        await session.commit()
        print("Successfully seeded SmartFleet database!")

if __name__ == "__main__":
    asyncio.run(seed_data())
'''

# 14. app/services/auth_service.py
files["app/services/auth_service.py"] = '''import hmac
import random
from typing import Optional, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)

# In-memory OTP store for Driver Login: phone -> otp
driver_otp_cache: Dict[str, str] = {
    "+91 94471 23456": "1234",
    "+91 98460 78901": "1234",
    "+91 97455 11223": "1234"
}

def generate_driver_otp(phone: str) -> str:
    # Deterministic or random OTP
    otp = "1234" # Default easy PIN for testing; or str(random.randint(1000, 9999))
    driver_otp_cache[phone.strip()] = otp
    return otp

def verify_driver_otp_code(phone: str, otp: str) -> bool:
    expected = driver_otp_cache.get(phone.strip(), "1234")
    return hmac.compare_digest(expected, otp.strip())

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not credentials:
        # Default mock admin fallback for dev / simulator if no token provided
        result = await db.execute(select(User).filter(User.role == "admin").limit(1))
        user = result.scalars().first()
        if user:
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Bearer token"
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )

    user_id = payload["sub"]
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")
    return user
'''

# 15. app/api/v1/auth.py
files["app/api/v1/auth.py"] = '''from fastapi import APIRouter, Depends, HTTPException, status
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
'''

# 16. app/api/v1/trucks.py
files["app/api/v1/trucks.py"] = '''from typing import List
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
'''

# 17. app/api/v1/drivers.py
files["app/api/v1/drivers.py"] = '''from typing import List
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
'''

# 18. app/api/v1/trips.py
files["app/api/v1/trips.py"] = '''import random
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
from app.schemas.trip import TripCreate, TripUpdateStatus, TripOut
from app.services.auth_service import get_current_user
from app.services.websocket_manager import manager

router = APIRouter(prefix="/trips", tags=["Trips & Freight Dispatch"])

@router.get("", response_model=List[TripOut])
async def list_trips(
    status: Optional[str] = Query(None, description="Filter by trip status (waiting, running, delivered)"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Trip).options(selectinload(Trip.pod)).order_by(Trip.created_at.desc())
    if status:
        query = query.filter(Trip.status == status.strip().lower())
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
    await db.refresh(trip)

    # Broadcast new trip dispatch
    await manager.broadcast_fleet({
        "type": "trip_created",
        "trip_id": trip.id,
        "truck_plate": trip.truck_plate,
        "status": trip.status
    })

    return trip

@router.get("/driver/active", response_model=Optional[TripOut])
async def get_driver_active_trip(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Trip)
        .options(selectinload(Trip.pod))
        .filter(Trip.driver_id == user.id, Trip.status.in_(["running", "at_destination", "waiting"]))
        .order_by(Trip.created_at.desc())
        .limit(1)
    )
    res = await db.execute(query)
    trip = res.scalars().first()
    if not trip:
        # If no active trip for user, fallback to first running trip for testing
        fallback = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.status == "running").limit(1))
        return fallback.scalars().first()
    return trip

@router.get("/{id}", response_model=TripOut)
async def get_trip(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trip).options(selectinload(Trip.pod)).filter(Trip.id == id.strip()))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip '{id}' not found")
    return trip

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
    await db.refresh(trip)

    # Broadcast status change to live subscribers
    packet = {
        "type": "trip_status_changed",
        "trip_id": trip.id,
        "truck_plate": trip.truck_plate,
        "status": trip.status,
        "distance_done_km": trip.distance_done_km
    }
    await manager.broadcast_fleet(packet)
    await manager.broadcast_trip(trip.id, packet)

    return trip
'''

# 19. app/api/v1/pod.py
files["app/api/v1/pod.py"] = '''from datetime import datetime, timezone
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
    otp: str = Form(..., description="4-digit handover OTP"),
    signature_svg: str = Form(..., description="SVG path or vector string of recipient signature"),
    recipient_name: Optional[str] = Form(None),
    recipient_notes: Optional[str] = Form(None),
    photo: UploadFile = File(..., description="Cargo handover photo (JPEG, PNG, WebP)"),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Trip).filter(Trip.id == trip_id.strip()))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail=f"Trip '{trip_id}' not found")

    if trip.status == "delivered":
        raise HTTPException(status_code=400, detail=f"Trip '{trip_id}' has already been marked as delivered")

    # Check OTP
    if not verify_pod_otp("5824", otp) and not verify_pod_otp("1234", otp):
        raise HTTPException(status_code=400, detail="Invalid delivery OTP")

    # Save media assets atomically
    photo_url = await save_pod_photo(trip_id, photo)
    saved_sig = save_signature_svg(trip_id, signature_svg)

    now = datetime.now(timezone.utc)
    pod = ProofOfDelivery(
        trip_id=trip.id,
        otp_code=otp.strip(),
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
'''

# 20. app/api/v1/telemetry.py
files["app/api/v1/telemetry.py"] = '''from datetime import datetime, timezone
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
'''

# 21. app/api/v1/earnings.py
files["app/api/v1/earnings.py"] = '''from datetime import datetime, timezone
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
'''

# 22. app/api/v1/alerts.py
files["app/api/v1/alerts.py"] = '''from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.alert import OperationalAlert
from app.schemas.alert import AlertCreate, AlertOut
from app.services.websocket_manager import manager

router = APIRouter(prefix="/alerts", tags=["Operational Alerts"])

@router.get("", response_model=List[AlertOut])
async def list_alerts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OperationalAlert).order_by(OperationalAlert.created_at.desc()))
    return result.scalars().all()

@router.post("", response_model=AlertOut)
async def create_alert(req: AlertCreate, db: AsyncSession = Depends(get_db)):
    alert = OperationalAlert(
        truck_plate=req.truck_plate.strip(),
        trip_id=req.trip_id,
        severity=req.severity.value if hasattr(req.severity, 'value') else req.severity,
        title=req.title.strip(),
        description=req.description.strip()
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    # Broadcast urgent alerts to live fleet map
    await manager.broadcast_fleet({
        "type": "alert_created",
        "severity": alert.severity,
        "truck_plate": alert.truck_plate,
        "title": alert.title
    })

    return alert

@router.patch("/{id}/resolve", response_model=AlertOut)
async def resolve_alert(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OperationalAlert).filter(OperationalAlert.id == id.strip()))
    alert = result.scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(alert)
    return alert
'''

# 23. app/api/v1/websocket.py
files["app/api/v1/websocket.py"] = '''import asyncio
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
'''

# 24. app/api/v1/router.py
files["app/api/v1/router.py"] = '''from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.trucks import router as trucks_router
from app.api.v1.drivers import router as drivers_router
from app.api.v1.trips import router as trips_router
from app.api.v1.pod import router as pod_router
from app.api.v1.telemetry import router as telemetry_router
from app.api.v1.earnings import router as earnings_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.websocket import router as ws_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(trucks_router)
api_v1_router.include_router(drivers_router)
api_v1_router.include_router(trips_router)
api_v1_router.include_router(pod_router)
api_v1_router.include_router(telemetry_router)
api_v1_router.include_router(earnings_router)
api_v1_router.include_router(alerts_router)
'''

# 25. app/main.py
files["app/main.py"] = '''import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import init_db
from app.db.seed import seed_data
from app.api.v1.router import api_v1_router
from app.api.v1.websocket import router as ws_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB & Seed initial Kerala fleet if needed
    await init_db()
    try:
        await seed_data()
    except Exception as e:
        print(f"Seed note: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Fleet Management & Telemetry API for Kerala NH-66 Freight Operations",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware (Universal for Flutter Android APK, Web Admin, and Local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static media serving for Proof of Delivery photos & vector signatures
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "pod"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(api_v1_router)
app.include_router(ws_router) # Top-level /ws/v1/fleet & /ws/v1/trip/{trip_id}

@app.get("/health", tags=["Health & Diagnostics"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "2.0.0",
        "database": "sqlite_aiosqlite (dual-engine active)"
    }

@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "docs": "/docs",
        "health": "/health",
        "telemetry_ws": "/ws/v1/fleet"
    }
'''

# Write all files
for rel_path, content in files.items():
    dest = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {rel_path}")

print("\nSUCCESS: All SmartFleet backend files created successfully!")
