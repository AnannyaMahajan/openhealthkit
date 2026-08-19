import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from openhealthkit.database import Base, get_async_db
from openhealthkit.main import app
from openhealthkit.models import Role, User, Permission
from openhealthkit.utils.security import hash_password

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        # Seed default roles
        admin_role = Role(name="ADMIN", description="System Administrator")
        worker_role = Role(name="HEALTH_WORKER", description="Community Health Worker")
        analyst_role = Role(name="ANALYST", description="Public Health Analyst")
        viewer_role = Role(name="VIEWER", description="Read-only Viewer")
        session.add_all([admin_role, worker_role, analyst_role, viewer_role])
        await session.commit()
        await session.refresh(admin_role)

        # Seed default admin user
        admin_user = User(
            username="admin",
            email="admin@openhealthkit.org",
            hashed_password=hash_password("AdminPass123!ChangeMe"),
            full_name="OpenHealthKit Admin",
        )
        admin_user.roles.append(admin_role)
        session.add(admin_user)
        await session.commit()

        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()



@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_async_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
