from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class AlertSeverity(str, Enum):
    urgent = "urgent"
    warning = "warning"
    info = "info"

class AlertCreate(BaseModel):
    truck_plate: str = Field(..., description="Target vehicle plate")
    trip_id: Optional[str] = None
    severity: AlertSeverity = AlertSeverity.warning
    title: str = Field(..., max_length=150)
    description: str

class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    truck_plate: str
    trip_id: Optional[str] = None
    severity: str
    title: str
    description: str
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
