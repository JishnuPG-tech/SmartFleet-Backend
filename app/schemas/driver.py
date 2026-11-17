from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class DriverCreate(BaseModel):
    phone: str = Field(..., description="Mobile number, e.g. +91 94471 23456")
    full_name: str = Field(..., description="Driver full name")
    license_number: str = Field(..., description="Heavy vehicle driving license number")
    experience_years: int = Field(default=0, ge=0)
    current_truck_plate: Optional[str] = None

class DriverOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    phone: str
    full_name: str
    license_number: str
    experience_years: int
    current_truck_plate: Optional[str] = None
    status: str = "available"
    total_trips_completed: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
