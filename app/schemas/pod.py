from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator

class VerifyOtpRequest(BaseModel):
    otp: str = Field(..., min_length=4, max_length=6, description="4-digit handover OTP")

    @model_validator(mode="before")
    @classmethod
    def normalize_otp_field(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "otp" not in data and "otp_code" in data:
                data["otp"] = data["otp_code"]
        return data

class CompletePodRequest(BaseModel):
    recipient_name: Optional[str] = None
    recipient_notes: Optional[str] = None

class PodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    trip_id: str
    otp_code: str
    otp_verified_at: datetime
    photo_url: str
    signature_svg: str
    recipient_name: Optional[str] = None
    recipient_notes: Optional[str] = None
    created_at: Optional[datetime] = None
