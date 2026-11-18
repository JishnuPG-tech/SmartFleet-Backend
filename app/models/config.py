from sqlalchemy import Column, String, Integer, DateTime, func, JSON
from app.models.base import Base

class FleetConfig(Base):
    __tablename__ = "fleet_config"

    key = Column(String(50), primary_key=True, index=True)
    data = Column(JSON, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
