"""Pydantic schemas for Ticket and Team entities."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.ticket import TicketCategory, TicketPriority, TicketStatus


class TeamSimple(BaseModel):
    """Minimal team info embedded in ticket responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str


class TeamResponse(TeamSimple):
    """Full team representation."""
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class TicketBase(BaseModel):
    """Shared properties for a support ticket."""
    subject: str = Field(..., min_length=3, max_length=500, description="Summary of the customer issue")
    description: str = Field(..., min_length=10, description="Full detail of the customer problem")
    customer_email: EmailStr = Field(..., description="Customer contact email")
    priority: Optional[TicketPriority] = Field(default=None, description="Urgency level")
    category: Optional[TicketCategory] = Field(default=None, description="Topic category")
    assigned_team_id: Optional[UUID] = Field(default=None, description="ID of assigned support team")


class TicketCreate(TicketBase):
    """Request payload for creating a new ticket."""
    pass


class TicketUpdate(BaseModel):
    """Request payload for updating an existing ticket."""
    subject: Optional[str] = Field(default=None, min_length=3, max_length=500)
    description: Optional[str] = Field(default=None, min_length=10)
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    assigned_team_id: Optional[UUID] = None


class TicketResponse(TicketBase):
    """Full ticket detail response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: TicketStatus
    assigned_team: Optional[TeamSimple] = None
    created_at: datetime
    updated_at: datetime


class TicketListResponse(BaseModel):
    """Paginated ticket collection response."""
    items: List[TicketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
