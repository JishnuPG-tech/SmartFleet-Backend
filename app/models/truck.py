from datetime import datetime
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
