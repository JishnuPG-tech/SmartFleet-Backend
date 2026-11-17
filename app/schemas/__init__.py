from app.schemas.auth import (
    LoginRequest, TokenResponse, DriverOtpRequest, DriverOtpVerify, UserProfile
)
from app.schemas.truck import TruckCreate, TruckUpdate, TruckOut, TruckStatus
from app.schemas.driver import DriverCreate, DriverOut
from app.schemas.trip import TripCreate, TripUpdateStatus, TripOut, TripStatusEnum
from app.schemas.pod import VerifyOtpRequest, CompletePodRequest, PodOut
from app.schemas.telemetry import TelemetryPingRequest, TelemetryBroadcastPacket
from app.schemas.earnings import EarningsSummaryOut
from app.schemas.alert import AlertCreate, AlertOut, AlertSeverity
