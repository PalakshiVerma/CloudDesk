# CloudDesk — Audit Trail, Traceability & Governance Framework

**Document Version:** 1.0.0  
**Project:** CloudDesk — AI-Assisted Support Ticket Triage & Routing Platform  
**Target Audience:** Compliance Officers, Security Engineers, Lead Developers, Support Operations  
**Status:** Mandatory Operational Framework  

---

## 1. Executive Summary & Purpose

In an enterprise AI deployment, automated decision-making cannot be a "black box". Support operations demand rigorous governance, explainability, and post-incident forensic capability.

The CloudDesk Audit Trail provides an **immutable, append-only chronological event ledger** capturing:
1. Every automated machine inference, confidence score, and routing decision.
2. Every human review, approval, or override—including exact delta changes and written justifications.
3. Every external webhook dispatch and delivery status.
4. Continuous data generation for monitoring model drift and accuracy over time.

---

## 2. Audit Event Taxonomy

Every event recorded in the `audit_logs` table is assigned a standardized `event_type`:

| Event Type | Actor | Trigger Condition | Captured Payload / Context |
| :--- | :--- | :--- | :--- |
| `TICKET_CREATED` | System / Webhook / Agent | Inbound ticket ingestion. | Subject, customer email, ingestion source (`webhook`, `portal`, `api`). |
| `AI_TRIAGED` | System (LLM Engine) | LLM structured classification completed. | Model name, token counts, inference latency (ms), confidence score, category, team. |
| `AUTO_ROUTED` | System (Routing Engine) | Confidence score $\ge 0.85$. | Assigned team ID, team name, routing rule applied. |
| `ESCALATED_TO_REVIEW`| System (Routing Engine) | Confidence score $< 0.85$ or LLM failure. | Confidence score, ambiguity flags, or system degradation reason. |
| `HUMAN_APPROVED` | Agent (`user_id`) | Agent validates AI recommendation in Review Queue. | Confirmed category, priority, and team; review duration. |
| `HUMAN_OVERRIDDEN` | Agent (`user_id`) | Agent corrects one or more AI prediction fields. | Before/after delta for category, priority, and team; written override rationale. |
| `STATUS_CHANGED` | Agent / System | Ticket moves between operational states. | `old_status` $\rightarrow$ `new_status` (e.g., `in_progress` $\rightarrow$ `resolved`). |
| `SETTINGS_UPDATED` | Admin (`user_id`) | Runtime system parameters modified. | Setting key (e.g., `CONFIDENCE_THRESHOLD`), old value, new value. |

---

## 3. Audit Log Schema & Payload Structure

```json
{
  "id": "e9c1d2e3-4f5a-6b7c-8d9e-0f1a2b3c4d5e",
  "ticket_id": "b3e944d1-c124-4f81-995b-38d73bdf6721",
  "user_id": "7fa8b210-911e-45de-8219-90b4112e0001",
  "event_type": "HUMAN_OVERRIDDEN",
  "old_values": {
    "category": "Technical",
    "priority": "Medium",
    "assigned_team": "Technical Support"
  },
  "new_values": {
    "category": "Integration",
    "priority": "High",
    "assigned_team": "Integrations Team"
  },
  "event_metadata": {
    "ai_confidence": 0.680,
    "review_duration_seconds": 14.2,
    "agent_email": "sarah.smith@clouddesk.internal",
    "override_reason": "Issue is customer webhook payload dropping fields, impacts third-party billing sync."
  },
  "created_at": "2026-09-28T11:46:15.302Z"
}
```

---

## 4. Analytical Recipes & SQL Auditing Queries

### 4.1 AI Drift & Human Override Rate Query
Calculates the percentage of AI decisions that were corrected by human agents over the last 30 days:

```sql
SELECT 
    COUNT(*) FILTER (WHERE event_type = 'HUMAN_OVERRIDDEN') AS total_overrides,
    COUNT(*) FILTER (WHERE event_type IN ('HUMAN_APPROVED', 'HUMAN_OVERRIDDEN')) AS total_reviews,
    ROUND(
        (COUNT(*) FILTER (WHERE event_type = 'HUMAN_OVERRIDDEN')::numeric / 
         NULLIF(COUNT(*) FILTER (WHERE event_type IN ('HUMAN_APPROVED', 'HUMAN_OVERRIDDEN')), 0)) * 100, 
        2
    ) AS human_override_percentage
FROM audit_logs
WHERE created_at >= NOW() - INTERVAL '30 days';
```

### 4.2 Triage Latency Audit (SLA Verification)
Measures the elapsed time between ticket creation and the definitive routing decision:

```sql
SELECT 
    t.id AS ticket_id,
    t.subject,
    t.status,
    t.created_at AS ingested_at,
    a.created_at AS routed_at,
    ROUND(EXTRACT(EPOCH FROM (a.created_at - t.created_at))::numeric, 2) AS triage_latency_seconds
FROM tickets t
JOIN audit_logs a ON t.id = a.ticket_id
WHERE a.event_type IN ('AUTO_ROUTED', 'HUMAN_APPROVED', 'HUMAN_OVERRIDDEN')
ORDER BY a.created_at DESC
LIMIT 50;
```

### 4.3 Category Discrepancy Matrix (Where is the AI Wrong?)
Reveals which categories most frequently trigger human corrections:

```sql
SELECT 
    old_values->>'category' AS ai_predicted_category,
    new_values->>'category' AS human_corrected_category,
    COUNT(*) AS correction_count
FROM audit_logs
WHERE event_type = 'HUMAN_OVERRIDDEN'
GROUP BY 1, 2
ORDER BY correction_count DESC;
```

---

## 5. Security, Immutability & Data Governance

1. **Append-Only Architecture:**  
   The `audit_logs` table has no `UPDATE` or `DELETE` API endpoints. In production, database grants on `audit_logs` for application connection pools are restricted to `SELECT` and `INSERT` only.
2. **PII Redaction Guardrails:**  
   Customer credit card numbers, passwords, and authorization tokens must never be written into `event_metadata` or `new_values`. The logging service scrubs common regex patterns (e.g., `Bearer ey...`, credit card Luhn patterns) prior to insertion.
3. **Retention & Archival Policy:**  
   * **Hot Storage (PostgreSQL):** 90 days of live, queryable audit events for real-time dashboards and review history.
   * **Cold Storage:** Events older than 90 days are partitioned and archived to compressed object storage (e.g., Azure Blob Cold Tier) for long-term compliance and ML re-training sets.
