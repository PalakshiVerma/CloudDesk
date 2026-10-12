"""API Version 1 Router Aggregation.

Central aggregation point for all v1 domain endpoint routers.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, tickets

api_router = APIRouter()

# Mount System Health & Diagnostic Endpoints
api_router.include_router(health.router, tags=["Health & Diagnostics"])

# Mount Tickets Endpoints
api_router.include_router(tickets.router)
