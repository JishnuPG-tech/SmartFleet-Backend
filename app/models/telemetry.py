from datetime import datetime, timezone
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
