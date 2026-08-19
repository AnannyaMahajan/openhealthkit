from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from openhealthkit.models.alert import Alert, AlertStatus
from openhealthkit.models.health_record import HealthRecord, Observation
from openhealthkit.models.organization import Community, Organization
from openhealthkit.models.sync import SyncRecord
from openhealthkit.models.user import User
from openhealthkit.schemas.analytics import (
    AlertSeverityCount,
    AnalyticsSummaryResponse,
    CategoryObservationCount,
    SyncStatusMetrics,
)


class AnalyticsService:
    """Service providing aggregate non-PII metrics and system activity statistics."""

    async def get_summary(self, db: AsyncSession) -> AnalyticsSummaryResponse:
        # Total counts
        user_cnt = (await db.execute(select(func.count(User.id)))).scalar() or 0
        org_cnt = (await db.execute(select(func.count(Organization.id)))).scalar() or 0
        comm_cnt = (await db.execute(select(func.count(Community.id)))).scalar() or 0
        rec_cnt = (
            await db.execute(
                select(func.count(HealthRecord.id)).where(HealthRecord.is_deleted == False)
            )
        ).scalar() or 0
        obs_cnt = (await db.execute(select(func.count(Observation.id)))).scalar() or 0

        # Open alerts count
        open_alert_cnt = (
            await db.execute(
                select(func.count(Alert.id)).where(Alert.status == AlertStatus.OPEN.value)
            )
        ).scalar() or 0

        # Observations grouped by category/type
        obs_stmt = select(Observation.observation_type, func.count(Observation.id)).group_by(
            Observation.observation_type
        )
        obs_res = await db.execute(obs_stmt)
        obs_by_type = [
            CategoryObservationCount(category=cat, count=cnt) for cat, cnt in obs_res.all()
        ]

        # Alerts grouped by severity
        alert_stmt = select(Alert.severity, func.count(Alert.id)).group_by(Alert.severity)
        alert_res = await db.execute(alert_stmt)
        alerts_by_sev = [
            AlertSeverityCount(severity=sev, count=cnt) for sev, cnt in alert_res.all()
        ]

        # Sync queue metrics
        sync_pending = (
            await db.execute(select(func.count(SyncRecord.id)).where(SyncRecord.state == "PENDING"))
        ).scalar() or 0
        sync_synced = (
            await db.execute(select(func.count(SyncRecord.id)).where(SyncRecord.state == "SYNCED"))
        ).scalar() or 0
        sync_conflict = (
            await db.execute(
                select(func.count(SyncRecord.id)).where(SyncRecord.state == "CONFLICT")
            )
        ).scalar() or 0
        sync_failed = (
            await db.execute(select(func.count(SyncRecord.id)).where(SyncRecord.state == "FAILED"))
        ).scalar() or 0

        return AnalyticsSummaryResponse(
            total_users=user_cnt,
            total_organizations=org_cnt,
            total_communities=comm_cnt,
            total_health_records=rec_cnt,
            total_observations=obs_cnt,
            active_alerts_count=open_alert_cnt,
            observations_by_type=obs_by_type,
            alerts_by_severity=alerts_by_sev,
            sync_metrics=SyncStatusMetrics(
                pending_count=sync_pending,
                synced_count=sync_synced,
                conflict_count=sync_conflict,
                failed_count=sync_failed,
            ),
            is_demo_data=False,
        )



analytics_service = AnalyticsService()
