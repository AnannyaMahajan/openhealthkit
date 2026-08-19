from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from openhealthkit.analytics.service import analytics_service
from openhealthkit.auth import SystemPermission, require_permission
from openhealthkit.database import get_async_db
from openhealthkit.models.user import User
from openhealthkit.schemas.analytics import AnalyticsSummaryResponse

router = APIRouter(prefix="/analytics", tags=["Analytics & Reporting"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.ANALYTICS_READ)),
):
    return await analytics_service.get_summary(db)
