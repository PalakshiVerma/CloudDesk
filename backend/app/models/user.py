"""User model — stores agent/admin accounts with role-based access control."""

import uuid
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(str, PyEnum):
    """Roles controlling what actions a user is permitted to perform."""
    ADMIN = "admin"
    LEAD = "lead"
    AGENT = "agent"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents a CloudDesk support agent or administrator."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="userrole"), nullable=False, default=UserRole.AGENT
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    reviews: Mapped[list["HumanReview"]] = relationship(
        "HumanReview", back_populates="agent", lazy="select"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="actor", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
