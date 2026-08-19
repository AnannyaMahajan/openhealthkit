from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from openhealthkit import __version__
from openhealthkit.config import settings
from openhealthkit.database import get_async_db
from openhealthkit.utils.logger import logger

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "openhealthkit-api",
        "version": __version__,
    }


@router.get("/ready")
async def readiness_check(response: Response, db: AsyncSession = Depends(get_async_db)):
    try:
        # Simple DB connectivity probe
        await db.execute(select(1))
        return {
            "status": "ready",
            "database": "connected",
            "version": __version__,
        }
    except Exception as exc:
        logger.error(f"Readiness probe database failure: {exc}")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        db_status = (
            f"error: {exc!s}" if settings.ENV_MODE == "development" else "unavailable"
        )
        return {
            "status": "not_ready",
            "database": db_status,
            "version": __version__,
        }

