from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.pod import PodOut

class TripStatusEnum(str, Enum):
    waiting = "waiting"
    accepted = "accepted"
    running = "running"
    at_destination = "at_destination"
    breakdown = "breakdown"
    delivered = "delivered"
    failed = "failed"
    cancelled = "cancelled"


class TripBreakdownRequest(BaseModel):
    latitude: float = Field(..., description="GPS Latitude where breakdown occurred")
    longitude: float = Field(..., description="GPS Longitude where breakdown occurred")
    reason: str = Field(..., description="Reason e.g. Engine Overheating, Tyre Puncture, Accident")
    remarks: Optional[str] = None

class TripCreate(BaseModel):
    origin_city: str = Field(..., description="Origin Kerala city/hub, e.g. Kochi Port")
    origin_code: Optional[str] = "COK"
    origin_lat: Optional[float] = 9.9312
    origin_lng: Optional[float] = 76.2673
    dest_city: str = Field(..., description="Destination Kerala city/hub, e.g. Kozhikode Hub")
    dest_code: Optional[str] = "CCJ"
    dest_lat: Optional[float] = 11.2588
    dest_lng: Optional[float] = 75.7804
    cargo_title: str = Field(..., description="Cargo description, e.g. 24.5T Industrial Steel")
    weight_tons: float = Field(..., gt=0, description="Cargo weight in metric tonnes")
    truck_plate: str = Field(..., description="Assigned truck license plate")
    driver_id: str = Field(..., description="Assigned driver user ID")
    total_distance_km: Optional[float] = 180.0
    allowance_amount: int = Field(default=1500, description="Driver daily Bata allowance in INR")
    scheduled_start: Optional[datetime] = None

class TripUpdateStatus(BaseModel):
    status: TripStatusEnum
    remarks: Optional[str] = None
    distance_done_km: Optional[float] = None

class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    origin_city: str
    origin_code: str
    origin_lat: float
    origin_lng: float
    dest_city: str
    dest_code: str
    dest_lat: float
    dest_lng: float
    cargo_title: str
    weight_tons: float
    truck_plate: str
    driver_id: str
    status: str
    scheduled_start: datetime
    actual_started_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    total_distance_km: float
    distance_done_km: float
    allowance_amount: int
    is_paid: bool = False
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    pod: Optional[PodOut] = None

    # Convenience aliases for Flutter client compatibility
    @property
    def from_city(self) -> str:
        return self.origin_city

    @property
    def to_city(self) -> str:
        return self.dest_city
