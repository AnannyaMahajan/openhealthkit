from fastapi import APIRouter

from openhealthkit.api.v1.alerts import router as alerts_router
from openhealthkit.api.v1.analytics import router as analytics_router
from openhealthkit.api.v1.auth import router as auth_router
from openhealthkit.api.v1.health import router as health_router
from openhealthkit.api.v1.observations import router as observations_router
from openhealthkit.api.v1.records import router as records_router
from openhealthkit.api.v1.sync import router as sync_router
from openhealthkit.api.v1.users import router as users_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(health_router)
v1_router.include_router(auth_router)
v1_router.include_router(users_router)
v1_router.include_router(records_router)
v1_router.include_router(observations_router)
v1_router.include_router(alerts_router)
v1_router.include_router(sync_router)
v1_router.include_router(analytics_router)
