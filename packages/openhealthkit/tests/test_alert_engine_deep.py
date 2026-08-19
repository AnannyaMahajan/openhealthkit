import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from openhealthkit.alerts.engine import alert_engine
from openhealthkit.alerts.evaluator import ConditionEvaluator
from openhealthkit.models.alert import Alert, AlertRule, AlertSeverity, AlertStatus
from openhealthkit.models.health_record import HealthRecord, Observation
from openhealthkit.schemas.alert import AlertUpdateStatus


def test_condition_evaluator_operators():
    assert ConditionEvaluator.evaluate(10, ">", 5) is True
    assert ConditionEvaluator.evaluate(5, ">", 10) is False

    assert ConditionEvaluator.evaluate(5, "<", 10) is True
    assert ConditionEvaluator.evaluate(10, "<", 5) is False

    assert ConditionEvaluator.evaluate(10, ">=", 10) is True
    assert ConditionEvaluator.evaluate(9, ">=", 10) is False

    assert ConditionEvaluator.evaluate(10, "<=", 10) is True
    assert ConditionEvaluator.evaluate(11, "<=", 10) is False

    assert ConditionEvaluator.evaluate("CRITICAL", "==", "CRITICAL") is True
    assert ConditionEvaluator.evaluate("HIGH", "==", "LOW") is False

    assert ConditionEvaluator.evaluate("fever", "in", ["fever", "cough"]) is True
    assert ConditionEvaluator.evaluate("headache", "in", ["fever", "cough"]) is False

    assert ConditionEvaluator.evaluate(10, "INVALID_OP", 10) is False


@pytest.mark.asyncio
async def test_alert_engine_rule_cooldown_and_disabled(db_session: AsyncSession):
    # Create test HealthRecord
    record = HealthRecord(patient_identifier="SYNTH-PAT-003", age_years=45)
    db_session.add(record)
    await db_session.commit()

    # Create active rule with cooldown
    rule = AlertRule(
        name="High Systolic BP Alert",
        observation_type="systolic_bp_mmHg",
        condition_operator=">=",
        threshold_value="140.0",
        severity=AlertSeverity.HIGH.value,
        cooldown_minutes=30,
        is_enabled=True,
    )
    db_session.add(rule)
    await db_session.commit()

    # Observation 1 (Triggers alert)
    obs1 = Observation(health_record_id=record.id, observation_type="systolic_bp_mmHg", value_number=145.0)
    db_session.add(obs1)
    await db_session.commit()

    alerts1 = await alert_engine.evaluate_observation(db_session, obs1)
    assert len(alerts1) == 1
    assert alerts1[0].severity == "HIGH"

    # Observation 2 within cooldown window (Should be suppressed by cooldown)
    obs2 = Observation(health_record_id=record.id, observation_type="systolic_bp_mmHg", value_number=150.0)
    db_session.add(obs2)
    await db_session.commit()

    alerts2 = await alert_engine.evaluate_observation(db_session, obs2)
    assert len(alerts2) == 0  # Suppressed by cooldown

    # Disable rule and test
    rule.is_enabled = False
    await db_session.commit()

    obs3 = Observation(health_record_id=record.id, observation_type="systolic_bp_mmHg", value_number=160.0)
    db_session.add(obs3)
    await db_session.commit()

    alerts3 = await alert_engine.evaluate_observation(db_session, obs3)
    assert len(alerts3) == 0  # Disabled rule ignored


@pytest.mark.asyncio
async def test_alert_status_lifecycle(async_client: AsyncClient):
    # Admin login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin@openhealthkit.org", "password": "AdminPass123!ChangeMe"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch alerts list
    res = await async_client.get("/api/v1/alerts", headers=headers)
    assert res.status_code == 200
