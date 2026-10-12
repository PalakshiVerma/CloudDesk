"""Seed rich realistic demo tickets into CloudDesk Neon database."""

import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.team import Team
from app.models.ticket import Ticket, TicketStatus, TicketPriority, TicketCategory

DEMO_TICKETS = [
    {
        "customer_email": "marcus.vance@fintechcorp.io",
        "subject": "Production Webhook endpoint returning 500 Internal Error",
        "description": "Our automated payout webhook listeners began receiving 500 errors from your webhook delivery servers at 13:45 UTC. Over 250 payment notification events have been dropped.",
        "category": TicketCategory.INTEGRATION,
        "priority": TicketPriority.CRITICAL,
        "status": TicketStatus.NEEDS_REVIEW,
        "team_slug": "integrations-team",
    },
    {
        "customer_email": "sarah.jenkins@healthflow.org",
        "subject": "Double charged on annual Enterprise renewal invoice #INV-2026-889",
        "description": "Our corporate card was charged twice ($12,400 each) on October 1st for the Enterprise plan renewal. Please refund the duplicate transaction immediately and send an updated receipt.",
        "category": TicketCategory.BILLING,
        "priority": TicketPriority.HIGH,
        "status": TicketStatus.AUTO_ROUTED,
        "team_slug": "billing-finance",
    },
    {
        "customer_email": "david.wu@quantumsoft.dev",
        "subject": "Okta SAML SSO redirect loop preventing developer logins",
        "description": "All 45 engineers on our team are stuck in an infinite redirect loop when authenticating via Okta SSO. The SAML assertion consumer service returns 'Invalid RelayState parameter'.",
        "category": TicketCategory.ACCOUNT,
        "priority": TicketPriority.CRITICAL,
        "status": TicketStatus.AUTO_ROUTED,
        "team_slug": "account-management",
    },
    {
        "customer_email": "elena.rostova@cyberguard.co",
        "subject": "Request for SOC 2 Type II compliance audit report and penetration test summary",
        "description": "Our compliance department requires your latest SOC 2 Type II compliance report, ISO 27001 certificate, and executive summary of the most recent annual third-party pentest for vendor review.",
        "category": TicketCategory.SECURITY,
        "priority": TicketPriority.MEDIUM,
        "status": TicketStatus.AUTO_ROUTED,
        "team_slug": "security-compliance",
    },
    {
        "customer_email": "khalid.mansoor@retailhub.com",
        "subject": "PostgreSQL database connection pool exhausted during flash sale",
        "description": "During our 20:00 flash sale, our application servers logged 'OperationalError: max connections exceeded'. We need emergency advice on optimizing connection pooling parameters.",
        "category": TicketCategory.TECHNICAL,
        "priority": TicketPriority.HIGH,
        "status": TicketStatus.NEEDS_REVIEW,
        "team_slug": "technical-support",
    },
    {
        "customer_email": "charlotte.b@creativestudios.net",
        "subject": "Update corporate billing address and EU VAT registration ID",
        "description": "We have recently relocated our headquarters to Dublin, Ireland. Please update our billing address and apply our new EU VAT identification number (IE987654321) to future invoices.",
        "category": TicketCategory.PAYMENT,
        "priority": TicketPriority.LOW,
        "status": TicketStatus.REVIEWED,
        "team_slug": "billing-finance",
    },
    {
        "customer_email": "tom.bradley@logistix.com",
        "subject": "How to set up automated daily CSV data export via REST API?",
        "description": "We are looking for code examples or documentation on how to configure a cron job to automatically download daily triage resolution summaries in CSV format via the v1 API.",
        "category": TicketCategory.GENERAL,
        "priority": TicketPriority.LOW,
        "status": TicketStatus.CLOSED,
        "team_slug": "tier-1-support",
    },
    {
        "customer_email": "priya.sharma@edutech.in",
        "subject": "Urgent: Locked out of root admin account after 2FA device loss",
        "description": "I lost my mobile device with the Google Authenticator app and do not have access to the backup emergency recovery codes. I am the primary billing admin for our school district account.",
        "category": TicketCategory.ACCOUNT,
        "priority": TicketPriority.CRITICAL,
        "status": TicketStatus.NEEDS_REVIEW,
        "team_slug": "account-management",
    },
    {
        "customer_email": "nathan.drake@unchartedapps.io",
        "subject": "Latency spikes over 1200ms on GraphQL query endpoint",
        "description": "Between 18:00 and 21:00 UTC yesterday, our APM reported p99 query latency jumping from 45ms to 1350ms on the /graphql endpoint. We suspect an unindexed join on ticket_predictions.",
        "category": TicketCategory.TECHNICAL,
        "priority": TicketPriority.MEDIUM,
        "status": TicketStatus.AUTO_ROUTED,
        "team_slug": "technical-support",
    },
    {
        "customer_email": "hannah.abbott@greengrocer.co.uk",
        "subject": "Stripe recurring charge declined for monthly team plan",
        "description": "We received an automated notification that our card ending in 4242 failed for the monthly team subscription ($299). We have updated the card in the portal, please retry the transaction.",
        "category": TicketCategory.PAYMENT,
        "priority": TicketPriority.MEDIUM,
        "status": TicketStatus.AUTO_ROUTED,
        "team_slug": "billing-finance",
    },
    {
        "customer_email": "alex.miller@solarpower.de",
        "subject": "API Rate limit exceeded (HTTP 429) on bulk ticket creation",
        "description": "We are migrating historical tickets from Zendesk and received HTTP 429 Too Many Requests after 500 requests. Could we temporarily request an increased rate limit of 50 req/sec for the migration?",
        "category": TicketCategory.INTEGRATION,
        "priority": TicketPriority.MEDIUM,
        "status": TicketStatus.PENDING_TRIAGE,
        "team_slug": "integrations-team",
    },
    {
        "customer_email": "claire.bennet@cheerleader.org",
        "subject": "Security audit: Inquire about data encryption at rest and in transit",
        "description": "Our corporate IT security team requires confirmation that all customer ticket descriptions and attachments are encrypted at rest with AES-256 and in transit with TLS 1.3.",
        "category": TicketCategory.SECURITY,
        "priority": TicketPriority.LOW,
        "status": TicketStatus.CLOSED,
        "team_slug": "security-compliance",
    }
]

async def seed_demo_tickets():
    async with AsyncSessionLocal() as session:
        # Fetch team mapping
        res = await session.execute(select(Team))
        teams_map = {t.slug: t.id for t in res.scalars().all()}

        created_count = 0
        for item in DEMO_TICKETS:
            # Check if ticket already exists
            existing = await session.execute(
                select(Ticket).where(Ticket.subject == item["subject"])
            )
            if existing.scalar_one_or_none() is not None:
                continue

            team_id = teams_map.get(item["team_slug"])
            ticket = Ticket(
                customer_email=item["customer_email"],
                subject=item["subject"],
                description=item["description"],
                category=item["category"],
                priority=item["priority"],
                status=item["status"],
                assigned_team_id=team_id,
            )
            session.add(ticket)
            created_count += 1

        await session.commit()
        print(f"Successfully seeded {created_count} demo tickets into Neon database!")

if __name__ == "__main__":
    asyncio.run(seed_demo_tickets())
