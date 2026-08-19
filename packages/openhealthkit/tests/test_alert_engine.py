import pytest
from httpx import AsyncClient
from openhealthkit.alerts.evaluator import ConditionEvaluator


def test_condition_evaluator_all_operators():
    # Greater than
    assert ConditionEvaluator.evaluate(10.5, ">", 5.0) is True
    assert ConditionEvaluator.evaluate(2.0, ">", 5.0) is False

    # Less than
    assert ConditionEvaluator.evaluate(3.0, "<", 5.0) is True
    assert ConditionEvaluator.evaluate(8.0, "<", 5.0) is False

    # Greater than or equal
    assert ConditionEvaluator.evaluate(140.0, ">=", 140.0) is True
    assert ConditionEvaluator.evaluate(139.9, ">=", 140.0) is False

    # Less than or equal
    assert ConditionEvaluator.evaluate(37.0, "<=", 37.0) is True
    assert ConditionEvaluator.evaluate(37.1, "<=", 37.0) is False

    # Equals
    assert ConditionEvaluator.evaluate("CRITICAL", "==", "CRITICAL") is True
    assert ConditionEvaluator.evaluate("HIGH", "==", "LOW") is False

    # In collection
    assert ConditionEvaluator.evaluate("high", "in", ["high", "critical"]) is True
    assert ConditionEvaluator.evaluate("low", "in", ["high", "critical"]) is False

    # Unknown operator returns False
    assert ConditionEvaluator.evaluate(10, "UNKNOWN", 10) is False


@pytest.mark.asyncio
async def test_alert_api_lifecycle(async_client: AsyncClient):
    # Admin Login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin@openhealthkit.org", "password": "AdminPass123!ChangeMe"},
    )
    if login_res.status_code == 200:
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create Alert Rule
        rule_payload = {
            "name": "High Fever Trigger Rule",
            "observation_type": "fever_body_temp_c",
            "condition_operator": ">=",
            "threshold_value": "39.0",
            "severity": "CRITICAL",
            "cooldown_minutes": 15,
        }
        rule_res = await async_client.post("/api/v1/alerts/rules", json=rule_payload, headers=headers)
        assert rule_res.status_code == 201

        # List Alert Rules
        rules_list_res = await async_client.get("/api/v1/alerts/rules", headers=headers)
        assert rules_list_res.status_code == 200
        assert len(rules_list_res.json()) >= 1

        # List Alerts
        alerts_res = await async_client.get("/api/v1/alerts", headers=headers)
        assert alerts_res.status_code == 200
