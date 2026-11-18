from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.trucks import router as trucks_router
from app.api.v1.drivers import router as drivers_router
from app.api.v1.trips import router as trips_router
from app.api.v1.pod import router as pod_router
from app.api.v1.telemetry import router as telemetry_router
from app.api.v1.earnings import router as earnings_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.websocket import router as ws_router
from app.api.v1.config import router as config_router
from app.api.v1.updater import router as updater_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(trucks_router)
api_v1_router.include_router(drivers_router)
api_v1_router.include_router(trips_router)
api_v1_router.include_router(pod_router)
api_v1_router.include_router(telemetry_router)
api_v1_router.include_router(earnings_router)
api_v1_router.include_router(alerts_router)
api_v1_router.include_router(config_router)

api_v1_router.include_router(updater_router)
