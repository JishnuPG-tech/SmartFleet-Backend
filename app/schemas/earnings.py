from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.trip import TripOut

class EarningsSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    driver_id: str
    driver_name: str
    total_trips: int
    total_allowance_earned: int
    pending_payout_amount: int
    settled_payout_amount: int
    trips: List[TripOut] = []
