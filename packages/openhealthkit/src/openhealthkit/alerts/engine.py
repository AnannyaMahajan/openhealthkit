from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from openhealthkit.alerts.evaluator import ConditionEvaluator
from openhealthkit.models.alert import Alert, AlertRule, AlertStatus, Notification
from openhealthkit.models.health_record import Observation
from openhealthkit.utils.logger import logger
from openhealthkit.utils.time import utc_now


class AlertEngine:
    """Core Rule-Based Alert Engine supporting threshold evaluation, cooldown, and notification dispatching."""

    async def evaluate_observation(self, db: AsyncSession, observation: Observation) -> list[Alert]:
        triggered_alerts: list[Alert] = []

        # Find enabled rules matching observation_type
        stmt = select(AlertRule).where(
            AlertRule.observation_type == observation.observation_type,
            AlertRule.is_enabled == True,
        )
        res = await db.execute(stmt)
        rules = res.scalars().all()

        for rule in rules:
            target_value = (
                observation.value_number
                if observation.value_number is not None
                else observation.value_text
            )

            is_triggered = ConditionEvaluator.evaluate(
                target_value, rule.condition_operator, rule.threshold_value
            )

            if is_triggered:
                # Check cooldown window
                if await self._is_in_cooldown(
                    db, rule.id, observation.health_record_id, rule.cooldown_minutes
                ):
                    logger.info(
                        f"Alert rule '{rule.name}' triggered for observation {observation.id} but skipped due to cooldown ({rule.cooldown_minutes} mins)."
                    )
                    continue

                # Create Alert
                title = f"Alert [{rule.severity}]: {rule.name}"
                desc = (
                    f"Observation '{observation.observation_type}' value ({target_value} {observation.unit or ''}) "
                    f"satisfied rule '{rule.name}' ({rule.condition_operator} {rule.threshold_value})"
                )

                alert = Alert(
                    rule_id=rule.id,
                    title=title,
                    description=desc,
                    severity=rule.severity,
                    status=AlertStatus.OPEN.value,
                    health_record_id=observation.health_record_id,
                    observation_id=observation.id,
                )
                db.add(alert)
                await db.flush()  # obtain alert.id

                # Dispatch notification log
                notification = Notification(
                    alert_id=alert.id,
                    channel="console",
                    status="SENT",
                    payload_json=f'{{"alert_id": "{alert.id}", "severity": "{alert.severity}"}}',
                )
                db.add(notification)
                triggered_alerts.append(alert)
                logger.warning(f"🚨 TRIGGERED ALERT: {title} - {desc}")

                # Notify plugins
                from openhealthkit.plugins.manager import plugin_manager

                await plugin_manager.dispatch_event(
                    "on_alert_triggered", alert=alert, observation=observation
                )

        return triggered_alerts

    async def _is_in_cooldown(
        self, db: AsyncSession, rule_id: str, health_record_id: str, cooldown_minutes: int
    ) -> bool:
        cutoff = utc_now() - timedelta(minutes=cooldown_minutes)
        stmt = select(Alert).where(
            Alert.rule_id == rule_id,
            Alert.health_record_id == health_record_id,
            Alert.created_at >= cutoff,
        )
        res = await db.execute(stmt)
        existing = res.scalars().first()
        return existing is not None


alert_engine = AlertEngine()
