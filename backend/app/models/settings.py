"""SystemSettings model — key-value store for runtime-configurable system parameters."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SystemSettings(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Runtime-configurable system parameters stored as key-value pairs.

    Examples:
        - key="confidence_threshold" value="0.85"
        - key="auto_routing_enabled" value="true"
    """

    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_editable: Mapped[bool] = mapped_column(default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<SystemSettings key={self.key} value={self.value}>"
