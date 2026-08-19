from collections.abc import AsyncGenerator, Generator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from openhealthkit.config import DatabaseType, settings


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy models in OpenHealthKit."""

    pass


# Sync Engine & Session
connect_args = {}
if settings.DATABASE_TYPE == DatabaseType.SQLITE:
    connect_args = {"check_same_thread": False}

sync_engine = create_engine(
    settings.sync_database_url,
    connect_args=connect_args,
    echo=(settings.ENV_MODE == "development"),
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Async Engine & Session
async_connect_args = {}
if settings.DATABASE_TYPE == DatabaseType.SQLITE:
    async_connect_args = {"check_same_thread": False}

async_engine: AsyncEngine = create_async_engine(
    settings.async_database_url,
    connect_args=async_connect_args,
    echo=(settings.ENV_MODE == "development"),
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# SQLite PRAGMA configuration for foreign key enforcement
@event.listens_for(sync_engine, "connect")
def set_sqlite_pragma_sync(dbapi_connection, connection_record):
    if settings.DATABASE_TYPE == DatabaseType.SQLITE:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining async database session in FastAPI routers."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Generator[Session, None, None]:
    """Dependency or utility function for sync database sessions."""
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def init_db() -> None:
    """Initialize database tables using metadata (useful for quickstart / testing)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
