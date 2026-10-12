"""Ticket business logic service layer."""

import math
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket, TicketStatus, TicketPriority, TicketCategory
from app.models.team import Team
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketService:
    """Service handling CRUD operations and queries for support tickets."""

    @staticmethod
    async def create_ticket(session: AsyncSession, ticket_in: TicketCreate) -> Ticket:
        """Creates a new ticket in the database defaulting to PENDING_TRIAGE."""
        ticket = Ticket(
            subject=ticket_in.subject,
            description=ticket_in.description,
            customer_email=ticket_in.customer_email,
            status=TicketStatus.PENDING_TRIAGE,
            priority=ticket_in.priority,
            category=ticket_in.category,
            assigned_team_id=ticket_in.assigned_team_id,
        )
        session.add(ticket)
        await session.commit()
        await session.refresh(ticket, attribute_names=["assigned_team"])
        return ticket

    @staticmethod
    async def get_ticket(session: AsyncSession, ticket_id: UUID) -> Optional[Ticket]:
        """Retrieves a single ticket by its UUID with relationships loaded."""
        stmt = (
            select(Ticket)
            .options(selectinload(Ticket.assigned_team))
            .where(Ticket.id == ticket_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_tickets(
        session: AsyncSession,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        category: Optional[TicketCategory] = None,
        team_id: Optional[UUID] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Retrieves paginated tickets matching given filter criteria."""
        query = select(Ticket).options(selectinload(Ticket.assigned_team))
        count_query = select(func.count(Ticket.id))

        # Apply filters
        if status:
            query = query.where(Ticket.status == status)
            count_query = count_query.where(Ticket.status == status)
        if priority:
            query = query.where(Ticket.priority == priority)
            count_query = count_query.where(Ticket.priority == priority)
        if category:
            query = query.where(Ticket.category == category)
            count_query = count_query.where(Ticket.category == category)
        if team_id:
            query = query.where(Ticket.assigned_team_id == team_id)
            count_query = count_query.where(Ticket.assigned_team_id == team_id)
        if search:
            search_filter = or_(
                Ticket.subject.ilike(f"%{search}%"),
                Ticket.description.ilike(f"%{search}%"),
                Ticket.customer_email.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Get total count
        total_result = await session.execute(count_query)
        total = total_result.scalar_one() or 0

        # Apply ordering and pagination
        offset = (page - 1) * page_size
        query = query.order_by(Ticket.created_at.desc()).offset(offset).limit(page_size)

        result = await session.execute(query)
        items = result.scalars().all()
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    @staticmethod
    async def update_ticket(
        session: AsyncSession, ticket_id: UUID, ticket_in: TicketUpdate
    ) -> Optional[Ticket]:
        """Updates fields on an existing ticket."""
        ticket = await TicketService.get_ticket(session, ticket_id)
        if not ticket:
            return None

        update_data = ticket_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ticket, key, value)

        await session.commit()
        await session.refresh(ticket, attribute_names=["assigned_team"])
        return ticket

    @staticmethod
    async def list_teams(session: AsyncSession) -> List[Team]:
        """Returns all active teams."""
        stmt = select(Team).where(Team.is_active == True).order_by(Team.name.asc())
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_ticket_stats(session: AsyncSession) -> Dict[str, int]:
        """Aggregates summary counts of tickets across lifecycle states."""
        stmt = select(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status)
        result = await session.execute(stmt)
        counts = {status.value: 0 for status in TicketStatus}
        total = 0
        for status, count in result.all():
            counts[status.value] = count
            total += count
        counts["total"] = total
        return counts
