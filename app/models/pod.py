import uuid
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
