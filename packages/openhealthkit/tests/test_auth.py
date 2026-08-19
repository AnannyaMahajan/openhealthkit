import pytest
from httpx import AsyncClient
from openhealthkit.utils.security import hash_password, verify_password


def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


@pytest.mark.asyncio
async def test_register_and_login_flow(async_client: AsyncClient):
    # Register new user
    reg_payload = {
        "username": "testworker",
        "email": "worker@openhealthkit.org",
        "password": "WorkerPassword123!",
        "full_name": "Test Health Worker",
    }
    response = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testworker"

    # Login user
    login_payload = {
        "username_or_email": "testworker",
        "password": "WorkerPassword123!",
    }
    login_res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    tokens = login_res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Fetch current user profile using token
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    profile_res = await async_client.get("/api/v1/auth/me", headers=headers)
    assert profile_res.status_code == 200
    assert profile_res.json()["email"] == "worker@openhealthkit.org"
