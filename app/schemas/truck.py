from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class TruckStatus(str, Enum):
    available = "available"
    on_trip = "on_trip"
    in_workshop = "in_workshop"

class TruckCreate(BaseModel):
    plate: str = Field(..., description="License plate, e.g. KL 11 AB 1234")
    model: str = Field(..., description="Make and model, e.g. BharatBenz 2823R")
    capacity_tons: float = Field(..., gt=0, description="Payload capacity in metric tonnes")
    assigned_driver_id: Optional[str] = None
    status: TruckStatus = TruckStatus.available

class TruckUpdate(BaseModel):
    model: Optional[str] = None
    capacity_tons: Optional[float] = None
    status: Optional[TruckStatus] = None
    assigned_driver_id: Optional[str] = None

class TruckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plate: str
    model: str
    capacity_tons: float
    status: str
    assigned_driver_id: Optional[str] = None
    last_latitude: Optional[float] = None
    last_longitude: Optional[float] = None
    last_heading: float = 0.0
    last_speed_kmh: float = 0.0
    last_telemetry_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
