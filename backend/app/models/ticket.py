"""Ticket model — core entity representing an incoming customer support request."""

import uuid
from enum import Enum as PyEnum
from sqlalchemy import String, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class TicketStatus(str, PyEnum):
    """Lifecycle state of a ticket through the triage pipeline."""
    PENDING_TRIAGE = "pending_triage"
    AUTO_ROUTED = "auto_routed"
    NEEDS_REVIEW = "needs_review"
    REVIEWED = "reviewed"
    CLOSED = "closed"


class TicketPriority(str, PyEnum):
    """Urgency level assigned to a ticket."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCategory(str, PyEnum):
    """The topic domain the ticket belongs to."""
    ACCOUNT = "Account"
    BILLING = "Billing"
    PAYMENT = "Payment"
    TECHNICAL = "Technical"
    SECURITY = "Security"
    INTEGRATION = "Integration"
    GENERAL = "General"


class Ticket(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A customer support ticket submitted for AI triage and routing."""

    __tablename__ = "tickets"

    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    customer_email: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, name="ticketstatus"),
        nullable=False,
        default=TicketStatus.PENDING_TRIAGE,
        index=True,
    )
    priority: Mapped[TicketPriority | None] = mapped_column(
        Enum(TicketPriority, name="ticketpriority"), nullable=True
    )
    category: Mapped[TicketCategory | None] = mapped_column(
        Enum(TicketCategory, name="ticketcategory"), nullable=True, index=True
    )
    assigned_team_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    assigned_team: Mapped["Team"] = relationship(
        "Team", back_populates="tickets", lazy="select"
    )
    prediction: Mapped["TicketPrediction | None"] = relationship(
        "TicketPrediction", back_populates="ticket", uselist=False, lazy="select"
    )
    human_review: Mapped["HumanReview | None"] = relationship(
        "HumanReview", back_populates="ticket", uselist=False, lazy="select"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="ticket", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Ticket id={self.id} status={self.status} priority={self.priority}>"
