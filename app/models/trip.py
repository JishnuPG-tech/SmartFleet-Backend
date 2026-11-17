from datetime import datetime, timezone
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
