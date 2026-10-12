"""Ticket REST API endpoints."""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.ticket import TicketStatus, TicketPriority, TicketCategory
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketListResponse,
    TeamResponse,
)
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new support ticket",
)
async def create_ticket(
    ticket_in: TicketCreate,
    db: AsyncSession = Depends(get_db),
):
    """Submits a new customer support ticket to the triage system."""
    return await TicketService.create_ticket(db, ticket_in)


@router.get(
    "/stats",
    summary="Get ticket lifecycle distribution metrics",
)
async def get_ticket_stats(
    db: AsyncSession = Depends(get_db),
):
    """Returns aggregated ticket count totals by status."""
    return await TicketService.get_ticket_stats(db)


@router.get(
    "/teams",
    response_model=List[TeamResponse],
    summary="List available support teams",
)
async def list_teams(
    db: AsyncSession = Depends(get_db),
):
    """Retrieves all active support escalation teams."""
    return await TicketService.list_teams(db)


@router.get(
    "",
    response_model=TicketListResponse,
    summary="List and filter support tickets",
)
async def list_tickets(
    status: Optional[TicketStatus] = Query(None, description="Filter by ticket status"),
    priority: Optional[TicketPriority] = Query(None, description="Filter by priority level"),
    category: Optional[TicketCategory] = Query(None, description="Filter by topic category"),
    team_id: Optional[UUID] = Query(None, description="Filter by assigned team UUID"),
    search: Optional[str] = Query(None, description="Search term in subject, description, or email"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """Returns paginated tickets with optional filtering."""
    return await TicketService.list_tickets(
        db,
        status=status,
        priority=priority,
        category=category,
        team_id=team_id,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Get ticket by ID",
)
async def get_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves detailed information for a specific ticket."""
    ticket = await TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found",
        )
    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Update a support ticket",
)
async def update_ticket(
    ticket_id: UUID,
    ticket_in: TicketUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Updates status, priority, category, or assigned team of a ticket."""
    ticket = await TicketService.update_ticket(db, ticket_id, ticket_in)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found",
        )
    return ticket
