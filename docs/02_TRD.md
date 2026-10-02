# CloudDesk — Technical Requirements Document (TRD)

**Document Version:** 1.0.0  
**Project:** CloudDesk — AI-Assisted Support Ticket Triage & Routing Platform  
**Target Environment:** Python 3.11+, FastAPI, Streamlit, PostgreSQL, Qdrant  
**Status:** Approved for Implementation  

---

## 1. Technical Architecture Overview

CloudDesk is structured as a modular, decoupled decision-support system. It integrates high-throughput REST APIs, asynchronous AI orchestration, vector-based semantic retrieval (RAG), relational transactional storage, and an interactive human-in-the-loop operations dashboard.

```text
                               ┌─────────────────────────────────┐
                               │   Streamlit Operations UI       │
                               │  (Dashboard / Review / Triage)  │
                               └────────────────┬────────────────┘
                                                │ HTTPS / REST
                                                ▼
                               ┌─────────────────────────────────┐
                               │     FastAPI Gateway & Core      │
                               │    (Validation / RBAC / Bus)    │
                               └────────────────┬────────────────┘
                                                │
         ┌──────────────────────────────┬───────┴──────────────────────┬──────────────────────────────┐
         ▼                              ▼                              ▼                              ▼
┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
│ PostgreSQL (Neon)│           │  AI Orchestrator │           │ Qdrant Vector DB │           │  External Mock   │
│ - Users & Roles  │           │ - LLM Client     │           │ - KB Embeddings  │           │  Helpdesk Webhook│
│ - Tickets        │           │ - JSON Schema    │           │ - Vector Search  │           │ - Inbound Listen │
│ - Predictions    │           │ - Confidence Gate│           │ - Semantic Sim   │           │ - Outbound Status│
│ - Audit Logs     │           │ - Fallback Queue │           └──────────────────┘           └──────────────────┘
└──────────────────┘           └──────────────────┘
```

---

## 2. Technology Stack & Rationale

| Layer | Selected Technology | Version | Rationale & Selection Criteria |
| :--- | :--- | :--- | :--- |
| **Language** | Python | 3.11+ | Lingua franca of modern AI engineering; unified runtime across FastAPI, LLM SDKs, Pytest, and data science tooling. |
| **Backend API** | FastAPI | 0.110+ | Asynchronous event loop, native Pydantic v2 data validation, automated OpenAPI/Swagger documentation generation, sub-millisecond route dispatching. |
| **Data Validation** | Pydantic | 2.6+ | Strict type enforcement, high-speed C-extension validation, seamless serialization of AI structured JSON outputs. |
| **Relational DB** | PostgreSQL / Neon | 16+ | ACID-compliant relational storage, JSONB indexing for AI prediction payloads, foreign-key referential integrity across audit histories. |
| **ORM & Migrations** | SQLAlchemy & Alembic | 2.0+ / 1.13+ | Declarative typing, robust connection pooling, automated schema versioning and deterministic database migrations. |
| **Vector Database** | Qdrant | 1.8+ | Enterprise vector search engine; payload filtering, cosine similarity search, lightweight local Docker footprint and cloud compatibility. |
| **AI / LLM API** | OpenAI API / Compatible | GPT-4o-mini | High reasoning fidelity, native JSON mode (`response_format={"type": "json_object"}`), low token latency, cost-effective inference. |
| **Embeddings** | OpenAI / SentenceTransformers | `text-embedding-3-small` / MiniLM | High semantic dense vector clustering, 1536/384 dimensions, cosine distance metric. |
| **Frontend UI** | Streamlit | 1.32+ | Rapid data application prototyping, native state management, clean data tables, interactive metric widgets, responsive layouts. |
| **Security & Auth** | Passlib (bcrypt) + PyJWT | 1.7+ / 2.8+ | Industry-standard password hashing, stateless token-based authentication with expiration and role claims. |
| **Testing Engine** | Pytest + HTTPX | 8.0+ / 0.27+ | Fixture-based unit testing, AsyncClient for API test isolation, deterministic mock LLM fixtures for CI pipelines. |
| **Containerization**| Docker & Docker Compose | 24+ / 2.24+ | Multi-service orchestration guaranteeing cross-platform reproducibility across Windows, Linux, and Cloud environments. |

---

## 3. Modular System Architecture

The codebase adheres strictly to layered clean architecture principles, separating concerns between route transport, domain services, persistence layers, and external integrations.

```text
CloudDesk/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py          # User authentication & tokens
│   │   │       │   ├── tickets.py       # Ticket CRUD & status updates
│   │   │       │   ├── triage.py        # AI triage execution endpoints
│   │   │       │   ├── reviews.py       # Human review & override endpoints
│   │   │       │   ├── dashboard.py     # Analytics & metric aggregates
│   │   │       │   ├── knowledge.py     # RAG document management
│   │   │       │   ├── evaluation.py    # Evaluation dataset benchmark runner
│   │   │       │   └── webhooks.py      # Mock external helpdesk webhooks
│   │   │       └── router.py            # APIRouter aggregation
│   │   ├── core/
│   │   │   ├── config.py                # Pydantic Settings & env configuration
│   │   │   ├── security.py              # JWT encoding/decoding & bcrypt hashing
│   │   │   ├── database.py              # SQLAlchemy engine & session factory
│   │   │   └── logging.py               # Structured logging configuration
│   │   ├── db/
│   │   │   ├── base.py                  # Declarative base model registry
│   │   │   └── init_db.py               # Database seeder (teams, admin user)
│   │   ├── models/                      # SQLAlchemy ORM entity definitions
│   │   │   ├── user.py
│   │   │   ├── team.py
│   │   │   ├── ticket.py
│   │   │   ├── prediction.py
│   │   │   ├── review.py
│   │   │   ├── audit.py
│   │   │   └── knowledge.py
│   │   ├── schemas/                     # Pydantic request/response schemas
│   │   │   ├── user.py
│   │   │   ├── ticket.py
│   │   │   ├── ai.py
│   │   │   ├── review.py
│   │   │   ├── dashboard.py
│   │   │   └── webhook.py
│   │   ├── services/                    # Encapsulated business logic
│   │   │   ├── ticket_service.py        # Lifecycle state transitions
│   │   │   ├── ai_service.py            # LLM client & schema validation
│   │   │   ├── routing_service.py       # Confidence threshold gating logic
│   │   │   ├── review_service.py        # Human approval & override logic
│   │   │   ├── rag_service.py           # Qdrant embedding search & grounding
│   │   │   ├── audit_service.py         # Structured event recording
│   │   │   └── evaluation_service.py    # Accuracy, recall, & latency scoring
│   │   └── main.py                      # FastAPI application bootstrap
│   ├── alembic/                         # Database migration scripts
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
│   ├── app.py                           # Streamlit multi-page entry point
│   ├── components/
│   │   ├── metric_cards.py              # KPI indicator cards
│   │   ├── ticket_table.py              # Filterable ticket data grid
│   │   └── review_modal.py              # Human override action modal
│   ├── pages/
│   │   ├── 1_Dashboard.py               # Ops throughput & metrics
│   │   ├── 2_Tickets.py                 # Ticket explorer & detail view
│   │   ├── 3_Review_Queue.py            # Low-confidence triage station
│   │   ├── 4_Knowledge_Base.py          # RAG document management
│   │   ├── 5_Evaluation.py              # Model benchmarking studio
│   │   └── 6_Settings.py                # Confidence threshold & config
│   └── requirements.txt
├── tests/
│   ├── conftest.py                      # Pytest fixtures & test DB setup
│   ├── test_api_tickets.py              # Ticket CRUD tests
│   ├── test_ai_triage.py                # AI prompt & schema validation tests
│   ├── test_routing_engine.py           # Threshold gating tests
│   ├── test_human_review.py             # Human review override tests
│   └── test_evaluation_benchmark.py     # 100-ticket test suite execution
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 4. AI & Decision Pipeline Specification

### 4.1 Inference Lifecycle
When a ticket is created or submitted for triage:
1. **Pre-processing:** Subject and description text are normalized; excessive whitespace, HTML tags, and null characters are stripped.
2. **Context Enrichment (RAG Optional):** The ticket text is converted into a dense vector embedding and queried against Qdrant to retrieve top-3 relevant knowledge base articles.
3. **Structured Prompt Execution:** The LLM is invoked with a strict system prompt and Pydantic-enforced JSON schema.
4. **Validation Guardrail:** The model output is parsed via `AIPredictionOutput.model_validate_json()`. If parsing fails, one retry is executed with explicit error feedback.
5. **Confidence Gating:** The validated confidence score is compared against `settings.CONFIDENCE_THRESHOLD` (0.85).
6. **State Dispatch:**
   * If `confidence >= 0.85`: Ticket status updated to `auto_routed`, assigned team populated, outbound webhook dispatched (if external).
   * If `confidence < 0.85` or LLM unavailable: Ticket status updated to `needs_review`, dispatched to human review queue with detailed reasoning.
7. **Audit Record:** Prediction metadata, latency, prompt tokens, and routing outcome are committed to `ticket_predictions` and `audit_logs`.

### 4.2 Fail-Safe & Circuit Breaking
* If OpenAI API returns HTTP 429 (Rate Limit) or 5xx, or request exceeds 8000ms timeout:
  * Do NOT crash the API.
  * Log warning with error trace.
  * Assign fallback status: `status = "needs_review"`.
  * Populate AI prediction reason: `"AI classification degraded: upstream provider unavailable. Diverted to manual review."`
  * Preserve ticket integrity in PostgreSQL.

---

## 5. Security, Identity & Compliance

### 5.1 Role-Based Access Control (RBAC)
* **`ADMIN`:** Full read/write access to system settings, confidence thresholds, user accounts, and evaluation suites.
* **`TEAM_LEAD`:** Access to all tickets, departmental assignment changes, team analytics, and review queues.
* **`AGENT`:** Read access to assigned tickets, capability to approve/correct tickets in the review queue.

### 5.2 Secret & Credential Management
* All credentials (`OPENAI_API_KEY`, `DATABASE_URL`, `JWT_SECRET_KEY`, `QDRANT_API_KEY`) must load exclusively via environment variables using `pydantic-settings`.
* `.env` files are added to `.gitignore`. A sanitized `.env.example` provides documentation for development setups.

---

## 6. Database Migration & Concurrency Strategy

* Schema modifications are governed exclusively via Alembic revisions.
* Relational constraints: `ticket_id` enforces `ON DELETE CASCADE` across `ticket_predictions`, `human_reviews`, and `audit_logs` to maintain clean test environments.
* Indexing Strategy:
  * B-Tree index on `tickets(status)` for instantaneous queue filtering.
  * B-Tree index on `tickets(assigned_team_id)` for departmental routing.
  * B-Tree index on `audit_logs(ticket_id)` and `audit_logs(created_at DESC)` for high-velocity timeline queries.
