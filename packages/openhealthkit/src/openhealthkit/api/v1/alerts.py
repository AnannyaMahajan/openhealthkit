from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from openhealthkit.auth import SystemPermission, require_permission
from openhealthkit.database import get_async_db
from openhealthkit.models.alert import Alert, AlertRule, AlertStatus
from openhealthkit.models.user import User
from openhealthkit.schemas.alert import (
    AlertRead,
    AlertRuleCreate,
    AlertRuleRead,
    AlertUpdateStatus,
)
from openhealthkit.utils.time import utc_now

router = APIRouter(prefix="/alerts", tags=["Alerts & Rules"])


@router.get("", response_model=list[AlertRead])
async def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: str | None = None,
    severity: str | None = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.ALERTS_READ)),
):
    stmt = select(Alert)
    if status_filter:
        stmt = stmt.where(Alert.status == status_filter.upper())
    if severity:
        stmt = stmt.where(Alert.severity == severity.upper())

    stmt = stmt.order_by(Alert.created_at.desc()).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.put("/{alert_id}/status", response_model=AlertRead)
async def update_alert_status(
    alert_id: str,
    req: AlertUpdateStatus,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.ALERTS_MANAGE)),
):
    stmt = select(Alert).where(Alert.id == alert_id)
    res = await db.execute(stmt)
    alert = res.scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = req.status.value
    if req.status == AlertStatus.ACKNOWLEDGED:
        alert.acknowledged_at = utc_now()
        alert.acknowledged_by_id = current_user.id
    elif req.status == AlertStatus.RESOLVED:
        alert.resolved_at = utc_now()
        alert.resolved_by_id = current_user.id

    await db.commit()
    await db.refresh(alert)
    return alert


@router.get("/rules", response_model=list[AlertRuleRead])
async def list_alert_rules(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.ALERTS_READ)),
):
    stmt = select(AlertRule)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/rules", response_model=AlertRuleRead, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    req: AlertRuleCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_permission(SystemPermission.ALERTS_MANAGE)),
):
    rule = AlertRule(
        name=req.name,
        observation_type=req.observation_type,
        condition_operator=req.condition_operator,
        threshold_value=req.threshold_value,
        severity=req.severity.value,
        cooldown_minutes=req.cooldown_minutes,
        is_enabled=req.is_enabled,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule
