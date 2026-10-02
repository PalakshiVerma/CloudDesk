# CloudDesk — Phase 1: Setup & Foundations Technical Report

**Document Version:** 1.0.0  
**Phase:** Phase 1 (Milestone 1 — Setup & Foundations)  
**Status:** Completed & Verified  
**Date:** 2026-10-02  

---

## 1. Executive Summary

The objective of **Phase 1 (Setup & Foundations)** was to establish the architectural foundation, configuration management, asynchronous database connectivity, and decoupled communication contracts between the **FastAPI REST API Gateway** and the **Streamlit Operations Control Center**.

Following the core architectural rule:
> *"Never start AI integrations before basic transactional and contract boundaries are rock-solid."*

Phase 1 establishes a modular, type-safe, and production-ready scaffolding so that future milestones (CRUD, AI triage, confidence-gated routing, human review, and RAG search) can be developed safely without architectural debt or refactoring.

---

## 2. Directory Hierarchy Created

```text
CloudDesk/
├── .env                                  # Active environment configuration with local defaults
├── .env.example                          # Sanitized environment template
├── docker-compose.yml                    # Multi-container orchestration (FastAPI, Streamlit, Postgres, Qdrant)
│
├── backend/                              # FastAPI Asynchronous REST Gateway
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   └── health.py         # GET /api/v1/health diagnostic endpoint
│   │   │       └── router.py             # APIRouter aggregation hub
│   │   ├── core/
│   │   │   ├── config.py                 # Pydantic v2 BaseSettings environment loader
│   │   │   ├── database.py               # SQLAlchemy 2.0 async engine & session pool
│   │   │   ├── logging.py                # Structured console logging configuration
│   │   │   └── security.py               # Password hashing (bcrypt) & JWT token utilities
│   │   ├── db/
│   │   │   └── base.py                   # DeclarativeBase, UUIDPrimaryKeyMixin, TimestampMixin
│   │   ├── models/                       # SQLAlchemy ORM entity models package
│   │   ├── schemas/
│   │   │   └── health.py                 # Pydantic validation models for health diagnostics
│   │   ├── services/                     # Encapsulated domain business logic package
│   │   └── main.py                       # FastAPI application entrypoint with lifespan & CORS
│   ├── requirements.txt                  # Backend dependencies
│   └── Dockerfile                        # Multi-stage container definition
│
└── frontend/                             # Streamlit Operations UI
    ├── .streamlit/
    │   └── config.toml                   # Dark theme design tokens (Deep Slate, Indigo, Emerald)
    ├── components/                       # Reusable UI widgets
    ├── pages/                            # Multi-page navigation structure
    │   ├── 1_Dashboard.py                # Operations metrics placeholder
    │   ├── 2_Tickets.py                  # Ticket explorer placeholder
    │   ├── 3_Review_Queue.py             # Human review queue placeholder
    │   ├── 4_Knowledge_Base.py           # RAG document management placeholder
    │   ├── 5_Evaluation.py               # Benchmark test studio placeholder
    │   └── 6_Settings.py                 # Confidence threshold configuration
    ├── app.py                            # Streamlit main entrypoint & live health prober
    ├── requirements.txt                  # Frontend dependencies
    └── Dockerfile                        # Container definition
```

---

## 3. Technology Stack Breakdown: What Each Does & Why It Was Chosen

| Technology | Role in Stack | Why It Was Chosen |
| :--- | :--- | :--- |
| **FastAPI** | Backend Web Framework | Provides high-throughput asynchronous execution, native Pydantic data validation, dependency injection for database sessions, and automatic interactive OpenAPI/Swagger docs (`/docs`). |
| **Uvicorn** | ASGI Web Server | Lightning-fast asynchronous server gateway that handles incoming HTTP requests and feeds them into FastAPI's async event loop. |
| **Pydantic v2** | Data Validation & Schemas | Validates incoming payloads and serializes responses using C-extensions (pydantic-core) for maximum speed. Used for type-safe system health schemas. |
| **Pydantic `BaseSettings`** | Configuration Management | Automatically reads `.env` variables, enforces strict data types (e.g. validating `CONFIDENCE_THRESHOLD` is between 0.0 and 1.0), and prevents hardcoded secrets. |
| **SQLAlchemy 2.0** | Relational ORM | Industry-standard Python SQL toolkit. Uses modern 2.0 syntax, declarative model registries, connection pooling, and supports both async and sync execution modes. |
| **asyncpg** | Async PostgreSQL Driver | High-performance asynchronous Cython driver used by SQLAlchemy's `create_async_engine` to prevent blocking the event loop during DB queries. |
| **psycopg2-binary** | Sync PostgreSQL Driver | Robust synchronous driver used by Alembic schema migrations and CLI management scripts. |
| **Streamlit** | Frontend Operations UI | Allows rapid authoring of interactive dashboards and operations workflows in Python with zero HTML/CSS/JS boilerplate. |
| **Requests** | Frontend HTTP Client | Enables Streamlit to communicate with the FastAPI backend via stateless REST calls rather than importing database models directly. |
| **Pandas & Plotly** | Data Tables & Dynamic Charts | Formats tabular ticket lists and renders responsive, interactive charts (throughput, latency, confidence score distributions). |
| **Docker & Compose** | Container Orchestration | Standardizes the runtime environment across Windows, Linux, and Cloud, launching PostgreSQL, Qdrant, FastAPI, and Streamlit with a single command. |

---

## 4. Key Software Engineering Concepts Applied in Phase 1

### 4.1 Strict Decoupled Architecture
* The **Streamlit frontend** runs independently on port `8501`.
* It interacts with the backend **strictly over HTTP REST** (`GET /api/v1/health`).
* It **never imports SQLAlchemy models or queries PostgreSQL directly**. This ensures that all business logic, validation rules, and authorization checks remain centralized in FastAPI.

### 4.2 Asynchronous I/O & Non-Blocking Database Connections
* In `backend/app/core/database.py`, we created an `AsyncEngine` using `asyncpg`.
* The `get_db()` dependency yields an `AsyncSession` that is automatically committed or rolled back per request and cleanly closed in the `finally` block:
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 4.3 Fail-Safe Health Probing (Safe Degradation)
* If the PostgreSQL database container is not yet started, the server **does not crash with an unhandled 500 error**.
* Instead, `check_database_connection()` catches connection failures, measures latency, and returns a structured diagnostic dictionary:
  * When DB is online: `status = "healthy"`, `database = "connected"`.
  * When DB is on standby: `status = "degraded"`, `database = "disconnected"`, accompanied by remediation hints.
* The API returns HTTP 200, allowing monitoring systems and the Streamlit UI to display status badges gracefully.

### 4.4 Modern Application Lifespan (`@asynccontextmanager`)
* Replaced deprecated `@app.on_event("startup")` and `@app.on_event("shutdown")` with FastAPI’s modern `lifespan` handler.
* Cleans up database connection pools using `await async_engine.dispose()` when the server shuts down.

### 4.5 Standardized RFC 7807 Error Handling
* Built a global exception handler in `main.py` that intercepts unhandled exceptions and formats them into standard problem details (`error_code`, `message`, `path`), ensuring raw Python stack traces are never exposed to clients.

---

## 5. Verification & Testing

All Python files were compiled and verified for syntax and type consistency:
```powershell
python -m py_compile backend/app/main.py backend/app/core/config.py backend/app/core/database.py backend/app/core/security.py backend/app/core/logging.py backend/app/db/base.py backend/app/schemas/health.py backend/app/api/v1/endpoints/health.py backend/app/api/v1/router.py frontend/app.py
```
**Result:** Exit code `0` (100% clean compilation, 0 errors).

---

## 6. How to Run Phase 1 Locally

### Step 1: Install Dependencies
Open a PowerShell terminal in the project directory:

```powershell
# In backend directory
cd c:\Users\Palakshi\Desktop\CloudDesk\CloudDesk\backend
python -m pip install -r requirements.txt

# In frontend directory
cd c:\Users\Palakshi\Desktop\CloudDesk\CloudDesk\frontend
python -m pip install -r requirements.txt
```

### Step 2: Run the FastAPI Backend
```powershell
cd c:\Users\Palakshi\Desktop\CloudDesk\CloudDesk\backend
python -m uvicorn app.main:app --reload --port 8000
```
* **Interactive Swagger UI:** Open [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
* **Live Health Check:** Open [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### Step 3: Run the Streamlit Operations UI
In a separate terminal:
```powershell
cd c:\Users\Palakshi\Desktop\CloudDesk\CloudDesk\frontend
python -m streamlit run app.py
```
* **Streamlit Control Center:** Open [http://localhost:8501](http://localhost:8501)
* View the live API Gateway card, database latency monitor, confidence threshold display ($\theta = 0.85$), and multi-page layout.

---

## 7. Next Steps: Roadmap to Phase 2

With Phase 1 complete, the foundation is ready for **Phase 2: Database & Core Models**:
1. Define SQLAlchemy models for `User`, `Team`, `Ticket`, `TicketPrediction`, `HumanReview`, and `AuditLog`.
2. Configure Alembic migration environment (`alembic.ini`).
3. Generate initial migration script (`001_initial_schema.py`).
4. Build database seeder (`init_db.py`) to insert the 6 default teams and default admin account.
