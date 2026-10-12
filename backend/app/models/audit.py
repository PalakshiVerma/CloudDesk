"""AuditLog model — immutable event ledger recording every system action."""

import uuid
from enum import Enum as PyEnum
from sqlalchemy import String, Text, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AuditEventType(str, PyEnum):
    """Canonical event types emitted throughout the triage lifecycle."""
    TICKET_CREATED = "TICKET_CREATED"
    AI_TRIAGED = "AI_TRIAGED"
    AUTO_ROUTED = "AUTO_ROUTED"
    ESCALATED_TO_REVIEW = "ESCALATED_TO_REVIEW"
    HUMAN_APPROVED = "HUMAN_APPROVED"
    HUMAN_OVERRIDDEN = "HUMAN_OVERRIDDEN"
    TICKET_CLOSED = "TICKET_CLOSED"
    SETTINGS_CHANGED = "SETTINGS_CHANGED"
    WEBHOOK_RECEIVED = "WEBHOOK_RECEIVED"


class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An immutable record of a single state-changing event in the system."""

    __tablename__ = "audit_logs"

    event_type: Mapped[AuditEventType] = mapped_column(
        Enum(AuditEventType, name="auditeventtype"),
        nullable=False,
        index=True,
    )
    ticket_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Redacted JSON snapshot of what changed
    changes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Short human-readable summary
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # Relationships
    ticket: Mapped["Ticket | None"] = relationship(
        "Ticket", back_populates="audit_logs", lazy="select"
    )
    actor: Mapped["User | None"] = relationship(
        "User", back_populates="audit_logs", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<AuditLog event={self.event_type} ticket_id={self.ticket_id}>"
