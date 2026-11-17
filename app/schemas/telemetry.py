from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class TelemetryPingRequest(BaseModel):
    truck_plate: str = Field(..., description="Vehicle license plate")
    trip_id: Optional[str] = Field(None, description="Active trip ID, if currently on trip")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    heading: float = Field(default=0.0, ge=0.0, lt=360.0, description="Compass bearing in degrees")
    speed_kmh: float = Field(default=0.0, ge=0.0, description="Speed in km/h")
    battery_level: Optional[int] = Field(default=None, ge=0, le=100)

class TelemetryBroadcastPacket(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str = "telemetry_update"
    truck_plate: str
    trip_id: Optional[str] = None
    latitude: float
    longitude: float
    heading: float = 0.0
    speed_kmh: float = 0.0
    battery_level: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
