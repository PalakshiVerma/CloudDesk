"""Team model — represents routing destinations for support tickets."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Team(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A support team that tickets can be routed to."""

    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket", back_populates="assigned_team", lazy="select"
    )
    predictions: Mapped[list["TicketPrediction"]] = relationship(
        "TicketPrediction", back_populates="recommended_team", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Team id={self.id} slug={self.slug}>"
