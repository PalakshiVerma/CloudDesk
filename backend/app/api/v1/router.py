"""API Version 1 Router Aggregation.

Central aggregation point for all v1 domain endpoint routers.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health

api_router = APIRouter()

# Mount System Health & Diagnostic Endpoints
api_router.include_router(health.router, tags=["Health & Diagnostics"])

# Additional domain routers (tickets, triage, reviews, etc.) are attached in subsequent milestones
