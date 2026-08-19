from pydantic import BaseModel


class CategoryObservationCount(BaseModel):
    category: str
    count: int


class AlertSeverityCount(BaseModel):
    severity: str
    count: int


class SyncStatusMetrics(BaseModel):
    pending_count: int
    synced_count: int
    conflict_count: int
    failed_count: int


class AnalyticsSummaryResponse(BaseModel):
    total_users: int
    total_organizations: int
    total_communities: int
    total_health_records: int
    total_observations: int
    active_alerts_count: int
    observations_by_type: list[CategoryObservationCount]
    alerts_by_severity: list[AlertSeverityCount]
    sync_metrics: SyncStatusMetrics
    is_demo_data: bool = True
