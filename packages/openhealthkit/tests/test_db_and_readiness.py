import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from openhealthkit.database import get_async_db
from openhealthkit.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient):
    res = await async_client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_readiness_check_success(async_client: AsyncClient):
    res = await async_client.get("/api/v1/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_readiness_check_db_failure(async_client: AsyncClient, db_session: AsyncSession):
    from unittest.mock import AsyncMock, patch

    # Mock execute on session to raise Exception
    with patch.object(db_session, "execute", side_effect=Exception("Database connection timeout error")):
        res = await async_client.get("/api/v1/ready")
        assert res.status_code == 503
        assert res.json()["status"] == "not_ready"


