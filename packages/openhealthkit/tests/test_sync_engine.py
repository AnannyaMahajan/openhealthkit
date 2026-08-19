from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from openhealthkit.sync.resolver import ConflictResolver, ConflictStrategy


@pytest.mark.asyncio
async def test_sync_push_pull_flow(async_client: AsyncClient):
    # Auth
    await async_client.post(
        "/api/v1/auth/register",
        json={"username": "syncworker", "email": "syncworker@ohk.org", "password": "Password123!"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "syncworker", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    now_iso = datetime.now(timezone.utc).isoformat()
    push_payload = {
        "client_id": "client-device-mac-001",
        "items": [
            {
                "client_id": "client-device-mac-001",
                "entity_type": "health_record",
                "entity_id": "550e8400-e29b-41d4-a716-446655440000",
                "action": "CREATE",
                "payload": {
                    "patient_identifier": "SYNTH-PATIENT-SYNC-100",
                    "age_years": 35,
                    "gender": "Male",
                },
                "client_timestamp": now_iso,
            }
        ],
    }

    # Push offline items
    push_res = await async_client.post("/api/v1/sync/push", json=push_payload, headers=headers)
    assert push_res.status_code == 200
    push_data = push_res.json()
    assert push_data["success_count"] == 1

    # Pull changes
    pull_payload = {"client_id": "client-device-mac-001"}
    pull_res = await async_client.post("/api/v1/sync/pull", json=pull_payload, headers=headers)
    assert pull_res.status_code == 200
    pull_data = pull_res.json()
    assert len(pull_data["items"]) >= 1


def test_conflict_resolver_all_strategies():
    resolver = ConflictResolver(default_strategy=ConflictStrategy.SERVER_WINS)
    now = datetime.now(timezone.utc)
    old = now - timedelta(hours=1)

    server_entity = {"patient_identifier": "SERVER-PATIENT", "age_years": 40}
    client_payload = {"patient_identifier": "CLIENT-PATIENT", "age_years": 42}

    # 1. SERVER_WINS
    res_srv, msg_srv = resolver.resolve(client_payload, old, server_entity, now, ConflictStrategy.SERVER_WINS)
    assert res_srv["patient_identifier"] == "SERVER-PATIENT"

    # 2. CLIENT_WINS
    res_cli, msg_cli = resolver.resolve(client_payload, old, server_entity, now, ConflictStrategy.CLIENT_WINS)
    assert res_cli["patient_identifier"] == "CLIENT-PATIENT"

    # 3. LAST_WRITE_WINS (Client newer)
    res_lww1, _ = resolver.resolve(client_payload, now, server_entity, old, ConflictStrategy.LAST_WRITE_WINS)
    assert res_lww1["patient_identifier"] == "CLIENT-PATIENT"

    # 4. LAST_WRITE_WINS (Server newer)
    res_lww2, _ = resolver.resolve(client_payload, old, server_entity, now, ConflictStrategy.LAST_WRITE_WINS)
    assert res_lww2["patient_identifier"] == "SERVER-PATIENT"

    # 5. CUSTOM Callback
    def custom_merge(cli, srv):
        merged = {**srv, **cli}
        merged["age_years"] = 99
        return merged

    resolver_custom = ConflictResolver(custom_callback=custom_merge)
    res_cust, _ = resolver_custom.resolve(client_payload, old, server_entity, now, ConflictStrategy.CUSTOM)
    assert res_cust["age_years"] == 99
