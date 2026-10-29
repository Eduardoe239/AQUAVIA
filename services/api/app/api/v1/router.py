from fastapi import APIRouter

from app.api.v1 import auth, consumption, devices, telemetry

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(consumption.router)
api_router.include_router(devices.router)
api_router.include_router(telemetry.router)
