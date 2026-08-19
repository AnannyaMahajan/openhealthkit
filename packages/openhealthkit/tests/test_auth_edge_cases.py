import pytest
from httpx import AsyncClient
from openhealthkit.auth import create_access_token, decode_token
from openhealthkit.config import settings


@pytest.mark.asyncio
async def test_auth_password_validation(async_client: AsyncClient):
    # Weak password test (too short)
    res = await async_client.post(
        "/api/v1/auth/register",
        json={"username": "weakuser", "email": "weak@ohk.org", "password": "123"},
    )
    assert res.status_code == 422

    # Weak password (no uppercase)
    res2 = await async_client.post(
        "/api/v1/auth/register",
        json={"username": "weakuser", "email": "weak@ohk.org", "password": "password123!"},
    )
    assert res2.status_code == 422


@pytest.mark.asyncio
async def test_auth_login_invalid_credentials(async_client: AsyncClient):
    res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "nonexistent", "password": "Password123!"},
    )
    assert res.status_code == 401
    assert "Invalid credentials" in res.json()["detail"]


@pytest.mark.asyncio
async def test_auth_refresh_token_handling(async_client: AsyncClient):
    # Invalid refresh token
    res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_jwt_token_string"},
    )
    assert res.status_code == 401

    # Valid login and refresh token exchange
    await async_client.post(
        "/api/v1/auth/register",
        json={"username": "refuser", "email": "refuser@ohk.org", "password": "Password123!"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "refuser", "password": "Password123!"},
    )
    ref_token = login_res.json()["refresh_token"]

    new_token_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": ref_token},
    )
    assert new_token_res.status_code == 200
    assert "access_token" in new_token_res.json()


@pytest.mark.asyncio
async def test_jwt_decoding_edge_cases():
    # Valid token creation and decoding
    token = create_access_token(subject="user-123", roles=["ADMIN"])
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"

    # Expired or invalid token returns None
    assert decode_token("invalid.token.structure") is None

