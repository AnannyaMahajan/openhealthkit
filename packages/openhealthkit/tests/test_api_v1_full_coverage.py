import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from openhealthkit.models.alert import Alert, AlertSeverity, AlertStatus
from openhealthkit.models.sync import SyncRecord, SyncState


@pytest.mark.asyncio
async def test_auth_api_routes_coverage(async_client: AsyncClient):
    # Register duplicate user error (400)
    await async_client.post(
        "/api/v1/auth/register",
        json={"username": "dupuser", "email": "dup@ohk.org", "password": "Password123!"},
    )
    dup_res = await async_client.post(
        "/api/v1/auth/register",
        json={"username": "dupuser", "email": "other@ohk.org", "password": "Password123!"},
    )
    assert dup_res.status_code == 400

    # User profile /auth/me
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "dupuser", "password": "Password123!"},
    )
    tokens = login_res.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    me_res = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "dupuser"

    # Refresh token endpoint
    ref_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert ref_res.status_code == 200
    assert "access_token" in ref_res.json()


@pytest.mark.asyncio
async def test_alerts_api_routes_coverage(async_client: AsyncClient, db_session: AsyncSession):
    # Login admin
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin@openhealthkit.org", "password": "AdminPass123!ChangeMe"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create dummy alert in DB
    alert = Alert(
        id=str(uuid.uuid4()),
        title="High BP Alert",
        description="Systolic BP exceeds threshold",
        severity=AlertSeverity.HIGH.value,
        status=AlertStatus.OPEN.value,
    )
    db_session.add(alert)
    await db_session.commit()
    await db_session.refresh(alert)

    # List alerts with filters
    list_res = await async_client.get("/api/v1/alerts?status_filter=OPEN&severity=HIGH", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


    # Update alert status ACKNOWLEDGED
    ack_res = await async_client.put(
        f"/api/v1/alerts/{alert.id}/status",
        json={"status": "ACKNOWLEDGED"},
        headers=headers,
    )
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "ACKNOWLEDGED"

    # Update alert status RESOLVED
    res_res = await async_client.put(
        f"/api/v1/alerts/{alert.id}/status",
        json={"status": "RESOLVED"},
        headers=headers,
    )
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "RESOLVED"

    # 404 update non-existent alert
    not_found = await async_client.put(
        "/api/v1/alerts/non-existent-alert/status",
        json={"status": "RESOLVED"},
        headers=headers,
    )
    assert not_found.status_code == 404


@pytest.mark.asyncio
async def test_sync_api_resolve_route(async_client: AsyncClient, db_session: AsyncSession):
    # Login admin
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin@openhealthkit.org", "password": "AdminPass123!ChangeMe"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    from datetime import datetime, timezone
    # Create sync record
    s_record = SyncRecord(
        id=str(uuid.uuid4()),
        client_id="device-01",
        entity_type="health_record",
        entity_id=str(uuid.uuid4()),
        action="UPDATE",
        payload_json="{}",
        state=SyncState.CONFLICT.value,
        client_timestamp=datetime.now(timezone.utc),
    )
    db_session.add(s_record)
    await db_session.commit()
    await db_session.refresh(s_record)


    # Resolve conflict endpoint
    res = await async_client.post(
        "/api/v1/sync/resolve",
        json={"sync_record_id": s_record.id, "resolution_strategy": "SERVER_WINS"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "resolved"


@pytest.mark.asyncio
async def test_users_api_create_user(async_client: AsyncClient, db_session: AsyncSession):
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin@openhealthkit.org", "password": "AdminPass123!ChangeMe"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_user_res = await async_client.post(
        "/api/v1/users",
        json={
            "username": "newanalyst",
            "email": "analyst@ohk.org",
            "password": "AnalystPass123!",
            "full_name": "New Analyst",
            "role_names": ["ANALYST"],
        },
        headers=headers,
    )
    assert create_user_res.status_code == 201
    assert create_user_res.json()["username"] == "newanalyst"

    # Duplicate username error 400
    dup_res = await async_client.post(
        "/api/v1/users",
        json={
            "username": "newanalyst",
            "email": "analyst2@ohk.org",
            "password": "AnalystPass123!",
        },
        headers=headers,
    )
    assert dup_res.status_code == 400

    # Inactive user login check
    from sqlalchemy.future import select
    from openhealthkit.models.user import User
    u_res = await db_session.execute(select(User).where(User.username == "newanalyst"))
    u = u_res.scalars().first()
    u.is_active = False
    await db_session.commit()

    inact_login = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "newanalyst", "password": "AnalystPass123!"},
    )
    assert inact_login.status_code == 403
    assert "deactivated" in inact_login.json()["detail"]


@pytest.mark.asyncio
async def test_observation_and_record_errors(async_client: AsyncClient):
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin@openhealthkit.org", "password": "AdminPass123!ChangeMe"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Record 404 get & delete
    assert (await async_client.get("/api/v1/records/missing-id", headers=headers)).status_code == 404
    assert (await async_client.put("/api/v1/records/missing-id", json={"age_years": 10}, headers=headers)).status_code == 404
    assert (await async_client.delete("/api/v1/records/missing-id", headers=headers)).status_code == 404

    # Observation missing health_record_id error (400)
    assert (await async_client.post("/api/v1/observations", json={"observation_type": "fever"}, headers=headers)).status_code == 422 or 400

    # Observation parent record not found error (404)
    obs_404 = await async_client.post(
        "/api/v1/observations",
        json={"health_record_id": "non-existent-rec", "observation_type": "fever"},
        headers=headers,
    )
    assert obs_404.status_code == 404

