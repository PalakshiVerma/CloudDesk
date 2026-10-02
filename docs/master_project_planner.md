# CloudDesk — Simple Master Project Planner

A straightforward, step-by-step roadmap to build **CloudDesk** — an AI-powered support ticket triage and routing platform.

---

## 📌 How the Project Works (In Simple Terms)

1. **A support ticket arrives** (via web form or webhook).
2. **AI reads it** and predicts:
   - **Category** (Account, Billing, Payment, Technical, Security, Integration, General)
   - **Priority** (Low, Medium, High, Critical)
   - **Recommended Team** (Technical Support, Billing & Finance, etc.)
   - **Confidence Score** (0% to 100%)
3. **Smart Decision Engine**:
   - If confidence is **85% or higher** ➔ **Auto-Route** directly to that team.
   - If confidence is **below 85%** ➔ Send to the **Human Review Queue** for an agent to click **Approve** or **Edit/Override**.
4. **Everything is tracked**: All actions are logged into an audit trail and visualized on a live Operations Dashboard.

---

## 🗺️ Project Phases Overview

```text
Phase 1: Setup & Foundations        ➔ Get backend & frontend running
Phase 2: Database & Models          ➔ Create tables and seed default teams
Phase 3: Basic Ticket System (CRUD) ➔ Create, view, and list tickets
Phase 4: AI Triage Engine           ➔ Connect LLM to classify tickets
Phase 5: Auto-Routing & Review      ➔ 85% confidence rule & review queue UI
Phase 6: Knowledge Base & RAG       ➔ Add Qdrant search for support runbooks
Phase 7: Audit Trail & Dashboard    ➔ Event logging & KPI metrics dashboard
Phase 8: Webhooks & 100-Ticket Test ➔ Test with mock helpdesk & 100 real tickets
Phase 9: Deployment & Production    ➔ Dockerize full stack & cloud deploy
```

---

## 🚀 Phase-by-Phase Task Breakdown

---

### Phase 1: Setup & Foundations
**Goal:** Set up the project folders, install packages, configure environment settings, and make sure the backend and frontend can talk to each other.

* [x] **Task 1.1: Set up backend requirements**
  * **File:** `backend/requirements.txt`
  * Add dependencies: FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic, asyncpg, psycopg2, OpenAI, Qdrant client, Pytest.
* [x] **Task 1.2: Set up frontend requirements**
  * **File:** `frontend/requirements.txt`
  * Add dependencies: Streamlit, Requests, Pandas, Plotly.
* [x] **Task 1.3: Configure environment variables**
  * **Files:** `.env.example`, `.env`
  * Set up database connection URL, OpenAI API key, Qdrant URL, and default confidence threshold (`0.85`).
* [x] **Task 1.4: Create backend settings loader**
  * **File:** `backend/app/core/config.py`
  * Use Pydantic `BaseSettings` to safely load environment variables into the backend.
* [x] **Task 1.5: Set up database connection engine**
  * **File:** `backend/app/core/database.py`
  * Connect SQLAlchemy to PostgreSQL with connection pooling.
* [x] **Task 1.6: Create FastAPI starter server**
  * **File:** `backend/app/main.py`
  * Create FastAPI app with a simple `GET /api/v1/health` endpoint that checks if the database is reachable.
* [x] **Task 1.7: Create Streamlit starter app**
  * **File:** `frontend/app.py`
  * Set up the base multi-page layout and a sidebar showing server connection status.

**How to verify:**
* Run backend: `uvicorn app.main:app --port 8000` ➔ Visiting `http://localhost:8000/api/v1/health` returns `{"status": "healthy"}`.
* Run frontend: `streamlit run app.py` ➔ Streamlit opens at `http://localhost:8501` showing green "Connected" status.

---

### Phase 2: Database & Core Models
**Goal:** Create PostgreSQL tables to store tickets, users, teams, AI predictions, human reviews, and audit logs.

* [ ] **Task 2.1: Define database base model**
  * **File:** `backend/app/db/base.py`
  * Set up shared fields for all tables (`id` as UUID, `created_at`, `updated_at`).
* [ ] **Task 2.2: Create User and Team models**
  * **Files:** `backend/app/models/user.py`, `backend/app/models/team.py`
  * Create `users` table (email, password hash, role: Admin/Lead/Agent).
  * Create `teams` table (name, slug, description).
* [ ] **Task 2.3: Create Ticket model**
  * **File:** `backend/app/models/ticket.py`
  * Create `tickets` table (subject, description, customer email, status, priority, category, assigned team ID).
* [ ] **Task 2.4: Create Prediction and Review models**
  * **Files:** `backend/app/models/prediction.py`, `backend/app/models/review.py`
  * Create `ticket_predictions` table (AI category, priority, confidence score, reason).
  * Create `human_reviews` table (agent ID, approved or overridden, old values vs new values, override reason).
* [ ] **Task 2.5: Create Audit and Settings models**
  * **Files:** `backend/app/models/audit.py`, `backend/app/models/settings.py`
  * Create `audit_logs` table (event type, changes JSON, timestamp).
  * Create `system_settings` table (key-value store for threshold and configuration).
* [ ] **Task 2.6: Run Alembic migrations and seed data**
  * **Files:** `backend/alembic/versions/001_initial_schema.py`, `backend/app/db/init_db.py`
  * Run migrations to create all tables in PostgreSQL.
  * Seed the 6 default teams:
    1. Technical Support
    2. Billing & Finance
    3. Account Management
    4. Security & Compliance
    5. Integrations Team
    6. Tier 1 Support
  * Seed a default Admin user (`admin@clouddesk.internal`).

**How to verify:**
* Run migration: `alembic upgrade head`.
* Query database: Verify all tables exist and `teams` has 6 rows.

---

### Phase 3: Basic Ticket System (CRUD)
**Goal:** Allow creating, viewing, updating, and listing tickets via the API and in the Streamlit UI before adding any AI.

* [ ] **Task 3.1: Create Ticket Pydantic schemas**
  * **File:** `backend/app/schemas/ticket.py`
  * Define request and response schemas for ticket creation, listing, and updates.
* [ ] **Task 3.2: Build Ticket Service**
  * **File:** `backend/app/services/ticket_service.py`
  * Write functions to create a ticket in database (`pending_triage`), get ticket by ID, and list tickets with status filters.
* [ ] **Task 3.3: Build Ticket REST API endpoints**
  * **File:** `backend/app/api/v1/endpoints/tickets.py`
  * `POST /api/v1/tickets` ➔ Create a new ticket.
  * `GET /api/v1/tickets` ➔ List tickets with pagination and status/category filters.
  * `GET /api/v1/tickets/{id}` ➔ Get full ticket details.
* [ ] **Task 3.4: Build basic JWT Authentication**
  * **Files:** `backend/app/core/security.py`, `backend/app/api/v1/endpoints/auth.py`
  * Add login endpoint (`POST /api/v1/auth/login`) returning a JWT token for agents.
* [ ] **Task 3.5: Build Streamlit Ticket Explorer page**
  * **File:** `frontend/pages/2_Tickets.py`
  * Build a filterable table showing all tickets with status badges.
  * Clicking a ticket opens a drawer with its full description.
  * Add a "Create Ticket" form to submit test tickets.
* [ ] **Task 3.6: Write tests for Ticket CRUD**
  * **File:** `tests/test_api_tickets.py`
  * Test creating, fetching, and filtering tickets using Pytest.

**How to verify:**
* Run `pytest tests/test_api_tickets.py` ➔ All pass.
* Open Streamlit `Tickets` page ➔ Submit a ticket via the form and see it appear in the table.

---

### Phase 4: AI Triage Engine
**Goal:** Connect OpenAI (with a mock fallback for offline work) to read ticket text and output structured JSON classification.

* [ ] **Task 4.1: Define AI output schema**
  * **File:** `backend/app/schemas/ai.py`
  * Enforce strict fields:
    * `category`: one of 7 categories.
    * `priority`: Low, Medium, High, or Critical.
    * `recommended_team`: one of 6 teams.
    * `confidence`: decimal between 0.00 and 1.00.
    * `reason`: short 1–2 sentence explanation.
* [ ] **Task 4.2: Build the AI prompt system**
  * **File:** `backend/app/core/prompts.py`
  * Write the system prompt with taxonomy definitions, priority rules, and few-shot examples.
  * Add input sanitization: truncate text over 3,000 characters (prevents token limit errors).
* [ ] **Task 4.3: Implement AI Triage Service**
  * **File:** `backend/app/services/ai_service.py`
  * Send ticket to OpenAI GPT-4o-mini using JSON mode (`temperature=0.0`).
  * Add automatic 1-retry if the JSON output fails validation.
  * Add an 8-second timeout: if OpenAI is slow/down, safely flag ticket for human review instead of crashing.
* [ ] **Task 4.4: Build Mock AI Service for offline development & tests**
  * **File:** `backend/app/services/mock_ai_service.py`
  * Heuristic classifier that runs locally without API keys or internet (e.g. keywords like "charged twice" ➔ Payment, 95% confidence).
* [ ] **Task 4.5: Write unit tests for AI schema validation**
  * **File:** `tests/test_ai_triage.py`
  * Verify bad categories are rejected, confidence bounds work, and mock AI classifies accurately.

**How to verify:**
* Run `pytest tests/test_ai_triage.py` ➔ All tests pass.
* Test with sample text *"I was charged twice for Pro plan"* ➔ AI correctly returns `Payment`, `High`, `confidence >= 0.90`.

---

### Phase 5: Auto-Routing & Human Review Queue
**Goal:** Build the confidence threshold rule ($\ge 85\%$ auto-routes; $< 85\%$ goes to review) and create the split-screen Human Review workstation.

* [ ] **Task 5.1: Build Confidence Gating Engine**
  * **File:** `backend/app/services/routing_service.py`
  * If `confidence >= 0.85` ➔ set ticket status to `auto_routed` and assign team.
  * If `confidence < 0.85` (or AI error) ➔ set ticket status to `needs_review`.
  * Save the AI prediction in `ticket_predictions`.
* [ ] **Task 5.2: Build Review & Override Service**
  * **File:** `backend/app/services/review_service.py`
  * `approve_ticket`: Agent confirms AI choice ➔ status becomes `reviewed`.
  * `correct_ticket`: Agent picks different category/team and gives a reason ➔ saves delta to `human_reviews`.
* [ ] **Task 5.3: Build Review API endpoints**
  * **File:** `backend/app/api/v1/endpoints/reviews.py`
  * `GET /api/v1/reviews/queue` ➔ Get tickets waiting for review.
  * `POST /api/v1/reviews/{id}/approve` ➔ One-click approval.
  * `POST /api/v1/reviews/{id}/correct` ➔ Submit human correction.
* [ ] **Task 5.4: Build Streamlit Human Review Queue page**
  * **File:** `frontend/pages/3_Review_Queue.py`
  * Split-screen interface:
    * **Left:** Customer ticket content (subject, description, email).
    * **Right:** AI suggestion, confidence meter chip, and reasoning.
  * Action buttons:
    * Green **[Approve Decision]** button.
    * Edit section: dropdowns to change Category/Team + text box for reason + **[Submit Correction]** button.
* [ ] **Task 5.5: Write tests for routing and human reviews**
  * **Files:** `tests/test_routing_engine.py`, `tests/test_human_review.py`
  * Test threshold edge cases (0.85 passes, 0.84 gets routed to review) and test override actions.

**How to verify:**
* Submit an ambiguous ticket (e.g. *"Slow export and also send invoice"* with 65% confidence).
* Open `Review Queue` page ➔ Ticket appears. Click "Approve" or "Override" and verify it moves out of the review queue.

---

### Phase 6: Knowledge Base & RAG (Smart Runbooks)
**Goal:** Store company support runbooks in Qdrant vector database so the AI can look up relevant articles to improve classification and suggest troubleshooting steps.

* [ ] **Task 6.1: Connect Qdrant vector database**
  * **File:** `backend/app/core/qdrant.py`
  * Initialize Qdrant client and create `support_knowledge` vector collection.
* [ ] **Task 6.2: Build Embedding & RAG Service**
  * **Files:** `backend/app/services/embedding_service.py`, `backend/app/services/rag_service.py`
  * Split runbook documents into chunks.
  * Generate text embeddings and store them in Qdrant with document metadata.
  * Search function: Given ticket text, retrieve top-2 matching runbook snippets.
  * Graceful fallback: If Qdrant is offline, triage proceeds normally without RAG.
* [ ] **Task 6.3: Seed standard support runbooks**
  * **Directory:** `backend/app/db/seed_runbooks/`
  * Add markdown runbooks: Stripe Billing Troubleshooting, SAML SSO Setup, Webhook Retries.
* [ ] **Task 6.4: Connect RAG to AI Triage Prompt**
  * **File:** `backend/app/services/ai_service.py`
  * Inject retrieved runbook snippets into the prompt so AI can suggest resolutions.
* [ ] **Task 6.5: Build Streamlit Knowledge Base page**
  * **File:** `frontend/pages/4_Knowledge_Base.py`
  * Upload runbook files.
  * View list of indexed documents.
  * Semantic Search tester: Type a query and see matching runbook chunks with similarity scores.

**How to verify:**
* Search *"SAML certificate expired"* on the Knowledge Base page ➔ Okta SSO runbook appears with high match score.

---

### Phase 7: Activity History (Audit Logs) & Ops Dashboard
**Goal:** Record every single decision in an immutable audit ledger and build an executive Operations Dashboard with real-time metrics.

* [ ] **Task 7.1: Build Audit Logging Service**
  * **File:** `backend/app/services/audit_service.py`
  * Automatically log events: `TICKET_CREATED`, `AI_TRIAGED`, `AUTO_ROUTED`, `ESCALATED_TO_REVIEW`, `HUMAN_APPROVED`, `HUMAN_OVERRIDDEN`.
  * Redact sensitive info (strip passwords, auth tokens, credit cards).
* [ ] **Task 7.2: Build Analytics calculation queries**
  * **File:** `backend/app/services/analytics_service.py`
  * Compute: Total tickets, % auto-routed (target $>80\%$), % escalated (target $<20\%$), average triage time (target $<10$s), Sev-1 alert count.
* [ ] **Task 7.3: Build Dashboard API endpoints**
  * **File:** `backend/app/api/v1/endpoints/dashboard.py`
  * `GET /api/v1/dashboard/stats` ➔ Returns KPI numbers.
  * `GET /api/v1/dashboard/categories` ➔ Returns ticket counts by category.
  * `GET /api/v1/dashboard/throughput` ➔ Returns 24-hour volume data.
* [ ] **Task 7.4: Build Streamlit Operations Dashboard page**
  * **File:** `frontend/pages/1_Dashboard.py`
  * Red Alert Banner at top if there are Critical/Sev-1 tickets.
  * KPI metric cards (Total Ingested, Auto-Route %, Review Queue Count, Avg Latency).
  * Category breakdown donut chart.
  * 24-hour throughput chart comparing auto-routed vs human-reviewed tickets.
* [ ] **Task 7.5: Build Settings page**
  * **File:** `frontend/pages/6_Settings.py`
  * Interactive slider to change the confidence threshold (e.g. adjust between 0.70 and 0.95).

**How to verify:**
* Open `Dashboard` page in Streamlit ➔ Verify metric cards show real numbers from the database.
* Move the slider on `Settings` page ➔ Verify the threshold updates in backend.

---

### Phase 8: Webhook Integration & 100-Ticket Test Benchmark
**Goal:** Connect external helpdesk systems via webhooks and run a 100-ticket benchmark test to prove the system reaches $>85\%$ accuracy.

* [ ] **Task 8.1: Build Mock Helpdesk Webhook**
  * **File:** `backend/app/api/v1/endpoints/webhooks.py`
  * `POST /api/v1/webhooks/mock-helpdesk/tickets`: Receives simulated Zendesk/Freshdesk payload, triages ticket, and sends back an assignment callback.
* [ ] **Task 8.2: Create 100-Ticket Labeled Ground Truth Dataset**
  * **File:** `tests/data/evaluation_set.json`
  * 100 realistic support tickets with known correct categories and priorities (15 Account, 20 Billing, 16 Payment, 25 Technical, 10 Security, 12 Integration, 10 General).
* [ ] **Task 8.3: Build Benchmark Test Runner**
  * **File:** `backend/app/services/evaluation_service.py`
  * Runs triage across all 100 tickets with bounded concurrency (prevents database connection overload).
  * Calculates: Classification Accuracy, Routing Accuracy, Critical Recall, and Confusion Matrix.
* [ ] **Task 8.4: Build Streamlit Evaluation Studio page**
  * **File:** `frontend/pages/5_Evaluation.py`
  * **[Run Benchmark (100 Tickets)]** button with a live progress bar.
  * Scorecard showing if targets passed ($>85\%$ accuracy, $>90\%$ critical recall).
  * Interactive 7x7 confusion matrix heatmap.
  * Error drill-down: inspect any tickets that AI misclassified.
* [ ] **Task 8.5: Write Automated Benchmark Pytest**
  * **File:** `tests/test_evaluation_benchmark.py`
  * Pytest test that runs the benchmark in CI and asserts that KPIs meet target thresholds.

**How to verify:**
* Run `pytest tests/test_evaluation_benchmark.py -v` ➔ Passes with $>85\%$ accuracy.
* Click "Run Benchmark" on the Evaluation page in Streamlit ➔ Scorecard and confusion matrix render smoothly.

---

### Phase 9: Deployment & Production Launch
**Goal:** Package the entire application into production-ready Docker containers, verify multi-container orchestration, and prepare for cloud deployment.

* [ ] **Task 9.1: Create Backend Dockerfile**
  * **File:** `backend/Dockerfile`
  * Multi-stage Python 3.11 Dockerfile installing dependencies and running Uvicorn with non-root user.
* [ ] **Task 9.2: Create Frontend Dockerfile**
  * **File:** `frontend/Dockerfile`
  * Lightweight Dockerfile for Streamlit running on port `8501`.
* [ ] **Task 9.3: Configure Docker Compose orchestration**
  * **File:** `docker-compose.yml`
  * Orchestrate 4 services:
    1. `postgres` (PostgreSQL 16 with health check)
    2. `qdrant` (Qdrant vector engine with health check)
    3. `backend` (FastAPI, depends on healthy postgres & qdrant)
    4. `frontend` (Streamlit, depends on backend)
* [ ] **Task 9.4: Production configuration & security checklist**
  * **File:** `.env.production.example`
  * Enforce production rules: strong JWT secret, secure database credentials, CORS domain restrictions, debug mode turned off.
* [ ] **Task 9.5: Create Cloud Deployment Guide (Azure / Neon)**
  * **File:** `docs/AZURE_DEPLOYMENT.md`
  * Step-by-step instructions for:
    * Deploying PostgreSQL on Neon.tech or Azure Database for PostgreSQL.
    * Deploying Backend & Frontend on Azure Container Apps.
    * Managing API keys with Azure Key Vault.
* [ ] **Task 9.6: End-to-End Smoke Test**
  * Run `docker compose up --build` on a fresh terminal.
  * Ingest 5 sample tickets through the UI and webhook.
  * Verify end-to-end flow: Ingest ➔ AI Triage ➔ Auto-Route / Review ➔ Audit Log ➔ Dashboard update.

**How to verify:**
* Run `docker compose up --build` ➔ All 4 containers start cleanly.
* Access `http://localhost:8501` and verify full app functionality without any errors.

---

## 📊 Summary Checklist

| Phase | What Gets Built | Estimated Time |
| :--- | :--- | :--- |
| **Phase 1** | Project scaffolding, config, database connection, health checks | 1–2 Days |
| **Phase 2** | PostgreSQL tables, SQLAlchemy models, Alembic migrations, team seed data | 2–3 Days |
| **Phase 3** | Ticket CRUD APIs, JWT auth, Streamlit Ticket Explorer page | 2–3 Days |
| **Phase 4** | OpenAI client, Pydantic validation, system prompt, mock AI fallback | 2–3 Days |
| **Phase 5** | 85% Confidence routing engine, Streamlit Review Queue page | 2–3 Days |
| **Phase 6** | Qdrant vector storage, support runbooks RAG, Knowledge Base page | 2–3 Days |
| **Phase 7** | Audit event ledger, real-time KPI queries, Operations Dashboard page | 2–3 Days |
| **Phase 8** | Webhook simulator, 100-ticket benchmark dataset, Evaluation Studio page | 2–3 Days |
| **Phase 9** | Dockerfiles, Docker Compose multi-container setup, Cloud deployment guide | 2 Days |

---

## 🏁 Definition of Done for CloudDesk

The project is 100% complete when:
1. A ticket can be created from the UI or external webhook.
2. AI automatically classifies it, assesses priority, and recommends a team.
3. High-confidence tickets ($\ge 85\%$) are automatically routed in $<2$ seconds.
4. Low-confidence tickets ($< 85\%$) wait in the Review Queue where an agent can approve or override them with one click.
5. All actions appear in the Audit Trail and update the live Dashboard.
6. The 100-ticket test benchmark proves $>85\%$ classification accuracy.
7. `docker compose up` starts the entire system with zero setup errors.
