from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class WeightPresetItem(BaseModel):
    label: str
    val: float

class HubLocationItem(BaseModel):
    city: str
    code: str
    name: str
    lat: float
    lng: float

class BroadcastBanner(BaseModel):
    title: str
    message: str
    severity: str = "warning" # info, warning, critical
    active: bool = True

class FleetMetadataResponse(BaseModel):
    cargos: List[str]
    weights: List[WeightPresetItem]
    hubs: List[HubLocationItem]
    driver_allowance_default: int = 1500
    system_status: str = "operational"
    notice_banner: Optional[BroadcastBanner] = None
    version: int = 1

class CargoAddRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)

class WeightAddRequest(BaseModel):
    label: str
    val: float

class HubAddRequest(BaseModel):
    city: str
    code: str
    name: str
    lat: float
    lng: float

class BroadcastRequest(BaseModel):
    title: str
    message: str
    severity: str = "warning"
