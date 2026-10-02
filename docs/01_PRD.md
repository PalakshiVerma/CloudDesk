# CloudDesk — Product Requirements Document (PRD)

**Document Version:** 1.0.0  
**Project:** CloudDesk — AI-Assisted Support Ticket Triage & Routing Platform  
**Target Domain:** B2B SaaS Workflow Management Support Operations  
**Track:** AI Application Engineering / Forward-Deployed Engineering (FDE) Practice  
**Status:** Approved for Implementation  

---

## 1. Executive Summary & Vision

**CloudDesk** is an enterprise-grade, AI-assisted decision-support platform engineered to eliminate manual ticket sorting and misrouting bottlenecks in B2B customer support operations.

In modern SaaS organizations, customer support operations suffer from the "shared queue bottleneck": every inbound support ticket arrives in a centralized inbox where generalist agents manually read, categorize, prioritize, and route the request to specialized departments. Because triage relies on human subjective judgment under high volume, misrouting rates typically hover between 20% and 35%, and initial triage delays range from 15 to 20 minutes per ticket.

CloudDesk introduces an **intelligent triage layer** positioned directly between inbound ticket channels (webhooks, email, portal) and support resolution teams. Using Large Language Models (LLMs) with strict structured output validation, semantic vector retrieval (Qdrant), and an explicit **confidence-gated routing engine**, CloudDesk:
1. Instantly classifies tickets into standardized functional categories.
2. Evaluates urgency and impact across four priority tiers.
3. Automatically routes high-confidence predictions ($\ge 0.85$) to the correct departmental queue in sub-second time.
4. Safely diverts low-confidence or ambiguous tickets ($< 0.85$) to an optimized **Human Review Queue**, ensuring human agents retain final authority over uncertain edge cases.
5. Captures an immutable audit trail of every automated decision and human correction to continuously benchmark and improve system performance.

---

## 2. Business Context & Problem Statement

### 2.1 The Customer Profile (Fictional Client)
* **Company:** CloudDesk Inc., a fast-growing B2B SaaS company providing workflow automation and team management software.
* **Customer Base:** ~4,000 active business accounts with varying Service Level Agreements (SLAs).
* **Support Staff:** 25–30 agents divided across three core departments: **Technical Support**, **Billing & Accounts**, and **Account Management**.
* **Daily Ticket Volume:** 350–500 tickets/day, growing at 15% quarter-over-quarter.

### 2.2 The "Ten Minutes Every Ticket Loses"
Support escalations are rarely pure technical bugs; more than half are **routing mistakes wearing a technical costume**.

```text
CURRENT MANUAL TRIAGE WORKFLOW (15–20 min latency, 25–30% misrouting):
[Customer Inbound] 
       │
       ▼
[General Support Queue] ──(Waits for available agent)
       │
       ▼
[Manual Agent Reading] ──(Guessed category, ambiguous tagging)
       │
       ▼
[Routing to Dept A] ────(Wrong Team: "Not our issue")
       │
       ▼
[Forwarding to Dept B] ──(Customer re-explains issue, SLA breached)
```

### 2.3 Key Operational Pain Points
1. **Prolonged Time-to-First-Action:** Tickets sit idle in the unassigned pool for 15–20 minutes before a human reviews the subject line.
2. **High Misrouting & Forwarding Overhead:** 25–30% of tickets are routed to the wrong team on first pass, multiplying internal ticket handoffs and driving customer frustration.
3. **Inconsistent Tagging:** Different agents classify identical issues under differing tags (e.g., "Subscription Error" vs. "Payment Gateway Failed" vs. "Login Bug").
4. **Buried Critical Incidents:** High-impact outages, security incidents, or payment failures sit behind routine password resets in FIFO order.
5. **Staff Burnout:** Tier-1 agents spend up to 40% of their working hours acting as manual postal sorters rather than resolving substantive customer issues.

---

## 3. Product Goals & Measurable KPIs

### 3.1 Business Goals
* **Slash Triage Latency:** Reduce median time from ticket ingestion to departmental assignment from 15–20 minutes to under 10 seconds.
* **Minimize Forwarding Rate:** Reduce downstream ticket re-routing from ~28% to under 12%.
* **Safeguard SLAs:** Guarantee 100% immediate detection and alert routing for critical/sev-1 incidents.
* **Maximize Operational Efficiency:** Automate at least 70% of routine ticket triage while preserving 100% human oversight on ambiguous cases.

### 3.2 Target Success Metrics (KPIs)
Aligned with the 100-ticket benchmark evaluation suite:

| KPI | Baseline (Manual) | CloudDesk Target | Measurement Methodology |
| :--- | :--- | :--- | :--- |
| **Classification Accuracy** | ~72% | **> 85%** | Correct category predicted vs. 100-ticket ground truth set |
| **Routing Accuracy** | ~70% | **> 85%** | Correct departmental queue assigned without forwarding |
| **Average Triage Time** | 15–20 min | **< 10 seconds** | Timestamp delta: `ticket.created_at` to `ticket.routed_at` |
| **Human Escalation Rate** | 100% manual | **< 20%** | Proportion of tickets routed to Human Review Queue |
| **Critical Urgent Recall** | ~80% | **> 90%** | Percentage of genuine Sev-1/Critical tickets flagged High/Critical |
| **Invalid AI Output Rate** | N/A | **< 2% (hard ceiling 5%)** | Malformed JSON or unparseable schema triggering fallback |

---

## 4. User Personas & Stakeholder Analysis

### 4.1 Persona 1: Sarah — Tier-1 Support Specialist (Generalist)
* **Role:** Reviews incoming ticket queues, answers routine queries, triages unassigned tickets.
* **Pain Point:** Drowning in routine password resets and invoice requests; dreads reading through 200 unclassified tickets each morning.
* **Needs from CloudDesk:** Clean Human Review Queue that surfaces only low-confidence tickets with highlighted AI reasoning and single-click "Approve" or "Correct" buttons.

### 4.2 Persona 2: Alex — Senior Technical Support Engineer (Specialist)
* **Role:** Investigates deep API failures, database anomalies, and platform integrations.
* **Pain Point:** Frequently assigned billing queries or general onboarding tickets that distract from high-severity engineering bugs.
* **Needs from CloudDesk:** High-precision ticket routing ensuring Technical Support queue receives exclusively technical and API/integration issues.

### 4.3 Persona 3: Marcus — Customer Support Operations Manager
* **Role:** Oversees team productivity, SLA compliance, staffing allocations, and tooling.
* **Pain Point:** Lacks visibility into triage bottlenecks, misroute trends, and agent workload distribution.
* **Needs from CloudDesk:** Operational analytics dashboard showcasing real-time automation rates, AI confidence distributions, triage latency, and human correction trends.

### 4.4 Persona 4: Elena — System Administrator & Security Officer
* **Role:** Manages platform integrations, API keys, compliance, and user roles.
* **Pain Point:** Fears sending proprietary customer data or credentials to external LLMs; needs zero-trust role-based access control and an unalterable audit log.
* **Needs from CloudDesk:** Robust RBAC, environment-secured credentials, PII safeguards, and complete audit trail for compliance.

---

## 5. System Taxonomy & Classification Rubric

To maintain strict operational predictability, CloudDesk standardizes support operations into exactly **7 Functional Categories**, **4 Priority Levels**, and **6 Destination Teams**.

### 5.1 The 7 Functional Categories
1. **Account:** User authentication, password resets, 2FA/MFA setup, SSO configuration, role changes, profile modifications.
2. **Billing:** Invoicing, pricing plans, annual renewals, VAT/tax exemption, receipt downloads, refund inquiries.
3. **Payment:** Failed credit card charges, payment gateway errors, duplicate debits, expired payment methods, banking decline codes.
4. **Technical:** Application errors, 500 server crashes, UI rendering bugs, data synchronization failures, export/import timeouts.
5. **Security:** Suspected unauthorized account access, data breach concerns, suspicious IP alerts, audit log export requests, vulnerability disclosures.
6. **Integration:** REST API rate limits, webhook delivery failures, third-party connector issues (Salesforce, HubSpot, Zapier), OAuth token errors.
7. **General:** Feature requests, product feedback, general "how-to" documentation questions, trial onboarding inquiries.

### 5.2 Priority Tiers
* **Critical (P1):** Complete platform outage, active security breach, severe financial transaction failures affecting all accounts, data loss. SLA: < 15 min.
* **High (P2):** Core functionality broken for a paying organization, single-tenant downtime, payment failed causing immediate account suspension. SLA: < 1 hour.
* **Medium (P3):** Feature bug with available workaround, non-blocking sync delay, billing query before renewal date. SLA: < 4 hours.
* **Low (P4):** Cosmetic glitch, general inquiry, feature suggestion, documentation clarification. SLA: < 24 hours.

### 5.3 Destination Teams
* `Technical Support`
* `Billing & Finance`
* `Account Management`
* `Security & Compliance`
* `Integrations Team`
* `Tier 1 Support` (Default fallback / General)

---

## 6. Scope of Work & Feature Prioritization (MoSCoW)

```text
PROPOSED AUTOMATED AI-TRIAGE ARCHITECTURE:
[Customer / Webhook] 
       │
       ▼
[Ingestion & Normalization]
       │
       ▼
[AI Decision Engine] ──────► [Qdrant Knowledge Base (RAG Context)]
(Category, Priority, Team, Confidence, Reason)
       │
       ├──────────────────────────────────────┐
       ▼ [Confidence >= 0.85]                 ▼ [Confidence < 0.85 OR LLM Error]
[Auto-Route to Department Queue]       [Human Review Queue]
       │                                      │
       │                                      ▼
       │                              [Agent Review & Correction]
       │                                      │
       └──────────────────┬───────────────────┘
                          ▼
            [Audit Log & Analytics Dashboard]
```

### 6.1 Must Have (P0 - MVP Core)
* **Ticket CRUD:** Create, read, update, list, and filter support tickets via REST API and Web UI.
* **Structured AI Triage:** LLM prompt execution enforcing validated JSON schema (category, priority, confidence, reason, recommended team).
* **Confidence Gating:** Strict threshold engine ($\theta = 0.85$). Auto-route if score $\ge \theta$; divert to Human Review if $< \theta$.
* **Human-in-the-Loop Review Queue:** Dedicated interface displaying low-confidence tickets, AI explanations, and single-click approve/modify controls.
* **Comprehensive Audit Trail:** Immutable logging of every AI inference, confidence score, routing decision, and human correction.
* **Mock External Webhook Integration:** Inbound webhook simulation (`POST /api/v1/webhooks/mock-helpdesk/tickets`) and outbound status callback.
* **Benchmark Evaluation Suite:** Script and dataset of 100 labeled tickets to evaluate accuracy, recall, and triage latency.

### 6.2 Should Have (P1 - Phase 2 Polish)
* **RAG Knowledge Base Integration:** Vector embedding retrieval via Qdrant to supply grounding context and suggest resolution snippets.
* **Operations Analytics Dashboard:** Visual metrics on triage throughput, auto-routing ratio, category breakdown, and agent review velocity.
* **Configurable Confidence Threshold:** Dynamic slider in admin settings allowing ops leads to adjust threshold between 0.70 and 0.95.
* **Role-Based Access Control (RBAC):** JWT authentication distinguishing Admin, Team Lead, and Support Agent privileges.

### 6.3 Could Have (P2 - Future Roadmap)
* **Similar Ticket Search:** Real-time semantic retrieval of previously resolved similar tickets.
* **Automated Customer Draft Responses:** AI-generated response drafts for agent one-click approval.
* **Multi-Language Triage:** Automatic language detection and translation triage.

### 6.4 Won't Have (Out of Scope for V1)
* Autonomous auto-reply to customers without agent approval.
* Model fine-tuning or custom LLM pre-training (utilize structured prompting over SOTA foundation models).
* Multi-agent frameworks (LangGraph, AutoGen) — keep architecture simple, explainable, and production-stable.
* Direct voice or telephonic integrations.

---

## 7. Functional Requirements

### 7.1 Ingestion & Normalization
* **FR-1.1:** System shall ingest tickets via REST API payload or external webhook JSON.
* **FR-1.2:** Incoming payloads must be validated against Pydantic schemas (subject, description, customer_email, external_id).
* **FR-1.3:** Whitespace, HTML artifacts, and raw escapes must be sanitized before AI processing.

### 7.2 AI Inference & Structured Validation
* **FR-2.1:** The backend shall transmit ticket text to the configured LLM API using strict JSON schema formatting.
* **FR-2.2:** The AI response must parse into:
  * `category`: One of the 7 valid enum strings.
  * `priority`: One of `Low`, `Medium`, `High`, `Critical`.
  * `recommended_team`: One of the 6 valid destination teams.
  * `confidence`: Float between `0.00` and `1.00`.
  * `reason`: Concise, 1–2 sentence human-readable rationale.
* **FR-2.3:** If the model returns malformed JSON or unparseable fields, the system shall execute one retry. If failure persists, the ticket is flagged `needs_review` with an internal alert.

### 7.3 Confidence-Gated Routing Engine
* **FR-3.1:** System shall evaluate `confidence >= system_threshold` (default: 0.85).
* **FR-3.2:** High-confidence tickets are assigned status `auto_routed` and dispatched to `assigned_team_id`.
* **FR-3.3:** Low-confidence tickets are assigned status `needs_review` and placed in the Human Review Queue.

### 7.4 Human Review & Correction
* **FR-4.1:** Human agents shall view pending review tickets sorted by priority and arrival time.
* **FR-4.2:** Agents can click **Approve** (accepting AI recommendation) or **Override** (selecting alternative category/priority/team).
* **FR-4.3:** Overrides must record the `user_id`, `original_ai_prediction`, `corrected_values`, and `correction_timestamp`.

### 7.5 Audit Trail & Governance
* **FR-5.1:** Every state change, routing action, and human review event must create an immutable record in `audit_logs`.
* **FR-5.2:** Audit logs must store actor ID (system or user), action type, before/after diffs, and UTC timestamp.

---

## 8. Non-Functional Requirements (NFRs)

* **Performance:** End-to-end triage processing latency must remain under 3.0 seconds per ticket at p95 (excluding network jitter).
* **Reliability:** The triage pipeline must maintain 99.9% uptime. If LLM API experiences downtime, inbound tickets must safely persist to the database in `pending_triage` status without data loss.
* **Scalability:** System architecture must support burst throughput of up to 50 concurrent ticket ingestions without database deadlocks.
* **Security:** All API credentials, JWT secrets, and database passwords must reside strictly in environment variables. No secrets in Git history.
* **Data Privacy:** Customer email addresses and ticket descriptions must be scrubbed of obvious credentials (passwords, auth tokens) prior to logging.

---

## 9. Definition of Done (DoD) for MVP

The CloudDesk platform is officially complete when:
1. An incoming ticket can successfully enter via API/webhook, execute structured AI classification, evaluate against confidence gating, auto-route or land in human review, and record a complete audit trail.
2. An agent can inspect, approve, or correct low-confidence tickets in the UI, updating ticket status in real time.
3. The mock external helpdesk round-trip webhook successfully simulates inbound ticket reception and outbound assignment notification.
4. The 100-ticket benchmark evaluation suite executes successfully, proving $>85\%$ classification accuracy, $>85\%$ routing accuracy, and $>90\%$ critical ticket recall.
5. All code is cleanly documented, tested via Pytest, and containerized via Docker Compose.
