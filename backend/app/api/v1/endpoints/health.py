"""System Health & Diagnostics Endpoints.

Provides health checks, uptime tracking, and component status verification.
"""

from datetime import datetime, timezone
import time
from fastapi import APIRouter, status
from app.core.config import settings
from app.core.database import check_database_connection
from app.schemas.health import SystemHealthResponse

router = APIRouter()

# Track startup timestamp for calculating uptime
_STARTUP_TIME = time.perf_counter()


@router.get(
    "/health",
    response_model=SystemHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System Health & Diagnostic Check",
    description="Probes the core API, database connectivity, and environment status.",
)
async def health_check() -> SystemHealthResponse:
    """Performs deep health check across API and database connections.

    Returns:
        SystemHealthResponse with sub-system diagnostics and latency metrics.
    """
    uptime_seconds = round(time.perf_counter() - _STARTUP_TIME, 2)
    db_status = await check_database_connection()

    overall_status = "healthy"
    if db_status.get("status") != "connected":
        overall_status = "degraded"

    components = {
        "database": db_status,
        "configuration": {
            "loaded": True,
            "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
            "llm_model": settings.LLM_MODEL,
            "qdrant_target": settings.QDRANT_URL,
        },
    }

    return SystemHealthResponse(
        status=overall_status,
        app_name=settings.APP_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        uptime_seconds=uptime_seconds,
        timestamp=datetime.now(timezone.utc),
        components=components,
    )
