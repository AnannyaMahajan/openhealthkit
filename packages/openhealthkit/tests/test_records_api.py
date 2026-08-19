import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_record_crud_and_endpoints(async_client: AsyncClient):
    # Register user (gets HEALTH_WORKER role by default)
    await async_client.post(
        "/api/v1/auth/register",
        json={"username": "recworker", "email": "recworker@ohk.org", "password": "Password123!"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "recworker", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Health Record
    rec_payload = {
        "patient_identifier": "SYNTH-PATIENT-TEST-001",
        "age_years": 28,
        "gender": "Female",
        "observations": [
            {
                "observation_type": "water_turbidity_ntu",
                "value_number": 2.5,
                "unit": "NTU",
            }
        ],
    }
    create_res = await async_client.post("/api/v1/records", json=rec_payload, headers=headers)
    assert create_res.status_code == 201
    rec = create_res.json()
    assert rec["patient_identifier"] == "SYNTH-PATIENT-TEST-001"
    rec_id = rec["id"]

    # Get Single Health Record
    get_res = await async_client.get(f"/api/v1/records/{rec_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == rec_id

    # Update Health Record
    update_res = await async_client.put(
        f"/api/v1/records/{rec_id}",
        json={"age_years": 29},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["age_years"] == 29

    # List Health Records
    list_res = await async_client.get("/api/v1/records", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Observations API: Create Observation
    obs_res = await async_client.post(
        "/api/v1/observations",
        json={
            "health_record_id": rec_id,
            "observation_type": "fever_body_temp_c",
            "value_number": 38.5,
            "unit": "°C",
        },
        headers=headers,
    )
    assert obs_res.status_code == 201

    # Observations API: List Observations
    list_obs_res = await async_client.get(
        f"/api/v1/observations?health_record_id={rec_id}", headers=headers
    )
    assert list_obs_res.status_code == 200
    assert len(list_obs_res.json()) >= 1

    # Verify HEALTH_WORKER receives 403 FORBIDDEN when attempting to delete without RECORDS_DELETE permission
    del_forbidden_res = await async_client.delete(f"/api/v1/records/{rec_id}", headers=headers)
    assert del_forbidden_res.status_code == 403

    # Admin Login to test deletion permission & user management
    admin_login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin@openhealthkit.org", "password": "AdminPass123!ChangeMe"},
    )
    assert admin_login_res.status_code == 200
    admin_token = admin_login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Analytics summary endpoint
    analytics_res = await async_client.get("/api/v1/analytics/summary", headers=admin_headers)
    assert analytics_res.status_code == 200

    # User management endpoints
    users_res = await async_client.get("/api/v1/users", headers=admin_headers)
    assert users_res.status_code == 200

    roles_res = await async_client.get("/api/v1/users/roles", headers=admin_headers)
    assert roles_res.status_code == 200

    # Delete Record as Admin
    del_res = await async_client.delete(f"/api/v1/records/{rec_id}", headers=admin_headers)
    assert del_res.status_code == 204

