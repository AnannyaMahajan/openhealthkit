from datetime import datetime

from pydantic import BaseModel, ConfigDict

from openhealthkit.models.alert import AlertSeverity, AlertStatus


class AlertRuleCreate(BaseModel):
    name: str
    observation_type: str
    condition_operator: str = ">"  # >, <, ==, >=, <=, in
    threshold_value: float
    severity: AlertSeverity = AlertSeverity.HIGH
    cooldown_minutes: int = 60
    is_enabled: bool = True


class AlertRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    observation_type: str
    condition_operator: str
    threshold_value: float
    severity: str
    cooldown_minutes: int
    is_enabled: bool
    created_at: datetime


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    rule_id: str | None = None
    title: str
    description: str
    severity: str
    status: str
    health_record_id: str | None = None
    observation_id: str | None = None
    created_at: datetime
    updated_at: datetime
    acknowledged_at: datetime | None = None
    acknowledged_by_id: str | None = None
    resolved_at: datetime | None = None
    resolved_by_id: str | None = None


class AlertUpdateStatus(BaseModel):
    status: AlertStatus
