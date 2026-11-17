from typing import Optional, List
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
