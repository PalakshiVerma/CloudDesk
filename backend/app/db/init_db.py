"""Database initialisation and seed script.

Creates all tables via Alembic and seeds:
  - 6 default support teams
  - 1 default Admin user (admin@clouddesk.internal)
  - Default system settings (confidence threshold, auto-routing flag)

Run:
    python -m app.db.init_db
"""

import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal, async_engine
from app.core.logging import logger
from app.core.security import get_password_hash
from app.db.base import Base
from app.models.team import Team
from app.models.user import User, UserRole
from app.models.settings import SystemSettings


# ── Default seed data ─────────────────────────────────────────────────────────

DEFAULT_TEAMS = [
    {
        "name": "Technical Support",
        "slug": "technical-support",
        "description": "Handles product bugs, outages, and integration errors.",
    },
    {
        "name": "Billing & Finance",
        "slug": "billing-finance",
        "description": "Handles invoices, subscription changes, and refunds.",
    },
    {
        "name": "Account Management",
        "slug": "account-management",
        "description": "Handles account setup, user access, and password resets.",
    },
    {
        "name": "Security & Compliance",
        "slug": "security-compliance",
        "description": "Handles security incidents, data privacy, and compliance requests.",
    },
    {
        "name": "Integrations Team",
        "slug": "integrations-team",
        "description": "Handles API, webhook, SSO, and third-party integration issues.",
    },
    {
        "name": "Tier 1 Support",
        "slug": "tier-1-support",
        "description": "First-line support for general and unclassified inquiries.",
    },
]

DEFAULT_SETTINGS = [
    {
        "key": "confidence_threshold",
        "value": "0.85",
        "description": "Minimum AI confidence required for automatic ticket routing (0.0–1.0).",
        "is_editable": True,
    },
    {
        "key": "auto_routing_enabled",
        "value": "true",
        "description": "Whether tickets above the confidence threshold are auto-routed.",
        "is_editable": True,
    },
    {
        "key": "max_triage_retry_attempts",
        "value": "1",
        "description": "Number of times to retry AI triage on validation failure.",
        "is_editable": True,
    },
    {
        "key": "llm_timeout_seconds",
        "value": "8.0",
        "description": "Maximum seconds to wait for LLM response before falling back to human review.",
        "is_editable": True,
    },
]


async def seed_teams(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Insert default teams; skip if already present. Returns slug->id map."""
    from sqlalchemy import select
    result = await session.execute(select(Team))
    existing = {t.slug for t in result.scalars().all()}

    team_ids: dict[str, uuid.UUID] = {}
    for data in DEFAULT_TEAMS:
        if data["slug"] not in existing:
            team = Team(**data)
            session.add(team)
            await session.flush()
            logger.info(f"  + Team seeded: {data['name']}")
            team_ids[data["slug"]] = team.id
        else:
            logger.info(f"  ~ Team already exists: {data['name']}")
    return team_ids


async def seed_admin_user(session: AsyncSession) -> None:
    """Insert default admin user; skip if already present."""
    from sqlalchemy import select
    ADMIN_EMAIL = "admin@clouddesk.internal"
    result = await session.execute(
        select(User).where(User.email == ADMIN_EMAIL)
    )
    if result.scalar_one_or_none() is not None:
        logger.info(f"  ~ Admin user already exists: {ADMIN_EMAIL}")
        return

    admin = User(
        email=ADMIN_EMAIL,
        hashed_password=get_password_hash("CloudDesk@Admin#2026"),
        full_name="CloudDesk Administrator",
        role=UserRole.ADMIN,
        is_active=True,
    )
    session.add(admin)
    logger.info(f"  + Admin user seeded: {ADMIN_EMAIL}")


async def seed_system_settings(session: AsyncSession) -> None:
    """Insert default system settings; skip keys that already exist."""
    from sqlalchemy import select
    result = await session.execute(select(SystemSettings))
    existing = {s.key for s in result.scalars().all()}

    for data in DEFAULT_SETTINGS:
        if data["key"] not in existing:
            setting = SystemSettings(**data)
            session.add(setting)
            logger.info(f"  + Setting seeded: {data['key']} = {data['value']}")
        else:
            logger.info(f"  ~ Setting already exists: {data['key']}")


async def init_db() -> None:
    """Main entry point: create tables (if needed) and seed data."""
    logger.info("=" * 60)
    logger.info("CloudDesk — Database Initialisation")
    logger.info("=" * 60)

    async with AsyncSessionLocal() as session:
        try:
            logger.info("\n[1/3] Seeding teams...")
            await seed_teams(session)

            logger.info("\n[2/3] Seeding admin user...")
            await seed_admin_user(session)

            logger.info("\n[3/3] Seeding system settings...")
            await seed_system_settings(session)

            await session.commit()
            logger.info("\n[OK] Database seed complete.")
        except Exception as exc:
            await session.rollback()
            logger.error(f"[ERROR] Seed failed: {exc}", exc_info=True)
            raise

    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(init_db())
