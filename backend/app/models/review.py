"""HumanReview model — records agent approval or override decisions on AI predictions."""

import uuid
from sqlalchemy import String, Text, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class HumanReview(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Captures a human agent decision to approve or correct AI triage output."""

    __tablename__ = "human_reviews"

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    was_approved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # Snapshot of AI values before override
    original_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    original_priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    original_team_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    # New values chosen by the agent (null if was_approved=True)
    corrected_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    corrected_priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    corrected_team_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Full delta for audit purposes
    change_delta: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    ticket: Mapped["Ticket"] = relationship(
        "Ticket", back_populates="human_review", lazy="select"
    )
    agent: Mapped["User | None"] = relationship(
        "User", back_populates="reviews", lazy="select"
    )

    def __repr__(self) -> str:
        action = "approved" if self.was_approved else "corrected"
        return f"<HumanReview ticket_id={self.ticket_id} action={action}>"
