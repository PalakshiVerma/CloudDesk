"""Health Check Schemas.

Defines Pydantic v2 validation models for system health and diagnostics.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    """Component health information for PostgreSQL relational database."""
    status: str = Field(..., description="Connection status: connected, degraded, or disconnected")
    latency_ms: Optional[float] = Field(None, description="Probe round-trip latency in milliseconds")
    engine: Optional[str] = Field(None, description="Database driver/engine identifier")
    error: Optional[str] = Field(None, description="Error detail if disconnected")
    hint: Optional[str] = Field(None, description="Remediation suggestion")


class SystemHealthResponse(BaseModel):
    """Complete diagnostic health response payload."""
    status: str = Field(..., description="Overall status: healthy, degraded, or unhealthy")
    app_name: str = Field(..., description="Application identifier")
    version: str = Field(..., description="Semantic version string")
    environment: str = Field(..., description="Current running environment")
    uptime_seconds: float = Field(..., description="Seconds since backend initialization")
    timestamp: datetime = Field(..., description="UTC timestamp of the health check probe")
    components: Dict[str, Any] = Field(..., description="Diagnostic status of sub-systems")
