from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class AdminLoginRequest(BaseModel):
    username: str = Field(..., description="Admin username (e.g. admin)")
    password: str = Field(..., description="Admin password")

class DriverRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Full legal name of the driver")
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number (e.g. +91 98950 12345 or 9895012345)")
    password: str = Field(..., min_length=4, description="PIN or password for login")
    license_number: str = Field(..., min_length=5, max_length=50, description="Commercial driving license number (e.g. KL-07-2018-0012345)")
    experience_years: int = Field(default=3, ge=0, le=50, description="Years of commercial driving experience")
    assigned_truck_plate: Optional[str] = Field(default=None, description="Assigned truck registration plate")

class DriverLoginRequest(BaseModel):
    phone: str = Field(..., description="Driver phone number")
    password: str = Field(..., description="Driver PIN or password")

class DriverUpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    license_number: Optional[str] = None
    experience_years: Optional[int] = None
    assigned_truck_plate: Optional[str] = None

class LoginRequest(BaseModel):
    phone: str = Field(..., description="E.164 phone number, e.g. +91 98950 00000 or 9895000000")
    password: str = Field(..., description="Admin PIN or password")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    phone: str
    full_name: str
    license_number: Optional[str] = None
    assigned_truck_plate: Optional[str] = None

class DriverOtpRequest(BaseModel):
    phone: str = Field(..., description="Driver phone number to send 4-digit SMS OTP")

class DriverOtpVerify(BaseModel):
    phone: str
    otp: str = Field(..., min_length=4, max_length=6, description="4 or 6-digit OTP code")

class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    phone: str
    full_name: str
    role: str
    avatar_url: Optional[str] = None
    is_active: bool = True
    license_number: Optional[str] = None
    experience_years: Optional[int] = None
    assigned_truck_plate: Optional[str] = None
