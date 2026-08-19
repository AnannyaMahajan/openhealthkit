import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from openhealthkit.auth import create_access_token
from openhealthkit.auth.rbac import SystemRole



@pytest.mark.asyncio
async def test_unauthorized_access_missing_token(async_client: AsyncClient):
    # Endpoint requiring auth returns 401 when no Authorization header
    res = await async_client.get("/api/v1/records")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_rbac_permission_failure_forbidden(async_client: AsyncClient, db_session: AsyncSession):
    # Register a user and assign VIEWER role
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={"username": "vieweruser", "email": "viewer@ohk.org", "password": "ViewerPassword123!"},
    )
    user_id = reg_res.json()["id"]

    # Assign VIEWER role in DB
    from sqlalchemy.future import select
    from openhealthkit.models.user import User, Role
    u_res = await db_session.execute(select(User).where(User.id == user_id))
    user = u_res.scalars().first()
    r_res = await db_session.execute(select(Role).where(Role.name == "VIEWER"))
    user.roles = [r_res.scalars().first()]
    await db_session.commit()

    # Create token for viewer user
    viewer_token = create_access_token(subject=user_id, roles=["VIEWER"])
    headers = {"Authorization": f"Bearer {viewer_token}"}

    # Attempting user management as VIEWER should return 403
    res = await async_client.get("/api/v1/users", headers=headers)
    assert res.status_code == 403

    # Attempting to delete record as VIEWER should return 403
    del_res = await async_client.delete("/api/v1/records/dummy-id", headers=headers)
    assert del_res.status_code == 403



@pytest.mark.asyncio
async def test_pagination_boundaries(async_client: AsyncClient):
    # Login as admin
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin@openhealthkit.org", "password": "AdminPass123!ChangeMe"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Pagination skip/limit on /records
    res = await async_client.get("/api/v1/records?skip=0&limit=5", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # Invalid pagination limit (< 1 or > 200) returns 422 validation error
    invalid_res = await async_client.get("/api/v1/records?skip=0&limit=500", headers=headers)
    assert invalid_res.status_code == 422


@pytest.mark.asyncio
async def test_invalid_api_payload_validation(async_client: AsyncClient):
    # Invalid user registration payload (missing email and password)
    res = await async_client.post(
        "/api/v1/auth/register",
        json={"username": "invalid_user"},
    )
    assert res.status_code == 422

    # Invalid health record update (age < 0 or invalid type)
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin@openhealthkit.org", "password": "AdminPass123!ChangeMe"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    rec_res = await async_client.put(
        "/api/v1/records/non-existent-id",
        json={"age_years": "invalid_number_string"},
        headers=headers,
    )
    assert rec_res.status_code == 422
