"""Database Engine and Connection Session Management.

Configures asynchronous SQLAlchemy 2.0 connection pooling, session lifecycle,
and connectivity health checks.
"""

import time
from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger


def get_async_db_url(url: str) -> str:
    """Ensures connection string uses asyncpg driver for async SQLAlchemy."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


# Asynchronous Database Engine (Used by FastAPI runtime endpoints)
async_db_url = get_async_db_url(settings.DATABASE_URL)

async_engine: AsyncEngine = create_async_engine(
    async_db_url,
    echo=settings.DEBUG and not settings.is_production,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"timeout": 5} if "asyncpg" in async_db_url else {},
)

# Asynchronous Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Synchronous Engine (Used by Alembic migrations and synchronous scripts)
sync_db_url = settings.DATABASE_URL_SYNC
if sync_db_url.startswith("postgresql+asyncpg://"):
    sync_db_url = sync_db_url.replace("postgresql+asyncpg://", "postgresql://", 1)

sync_engine = create_engine(
    sync_db_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency provider for FastAPI route handlers.

    Yields:
        AsyncSession: Managed transactional session automatically rolled back on error.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error(f"Database session rolled back due to error: {exc}")
            raise
        finally:
            await session.close()


async def check_database_connection() -> Dict[str, Any]:
    """Lightweight health probe testing database connectivity.

    Executes a simple 'SELECT 1' with latency tracking.
    Never raises an unhandled exception—returns structured status dictionary.
    """
    start_time = time.perf_counter()
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            scalar = result.scalar()
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            if scalar == 1:
                return {
                    "status": "connected",
                    "latency_ms": latency_ms,
                    "engine": "PostgreSQL (asyncpg)",
                }
            return {
                "status": "degraded",
                "latency_ms": latency_ms,
                "message": "Unexpected response from database probe",
            }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.warning(f"Database health check failed ({latency_ms}ms): {exc}")
        return {
            "status": "disconnected",
            "latency_ms": latency_ms,
            "error": str(exc),
            "hint": "Check if PostgreSQL is running or verify DATABASE_URL in .env",
        }
