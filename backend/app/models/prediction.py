"""TicketPrediction model — stores the AI triage output for each ticket."""

import uuid
from sqlalchemy import Float, String, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class TicketPrediction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Stores the structured AI classification output for one ticket."""

    __tablename__ = "ticket_predictions"

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    # Mirrors TicketCategory & TicketPriority enums stored as strings for flexibility
    ai_category: Mapped[str] = mapped_column(String(50), nullable=False)
    ai_priority: Mapped[str] = mapped_column(String(20), nullable=False)
    recommended_team_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
    )
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    was_auto_routed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    ticket: Mapped["Ticket"] = relationship(
        "Ticket", back_populates="prediction", lazy="select"
    )
    recommended_team: Mapped["Team | None"] = relationship(
        "Team", back_populates="predictions", lazy="select"
    )

    def __repr__(self) -> str:
        return (
            f"<TicketPrediction ticket_id={self.ticket_id} "
            f"confidence={self.confidence_score:.2f} category={self.ai_category}>"
        )
