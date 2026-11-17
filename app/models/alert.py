import uuid
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
