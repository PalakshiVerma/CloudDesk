"""CloudDesk — Intelligent Support Ticket Triage & Routing Platform.

Streamlit Operations Control Center & Frontend Application Shell.
"""

import os
import time
from datetime import datetime
import requests
import streamlit as st

# Configure page layout and visual identity
st.set_page_config(
    page_title="CloudDesk — Support Triage Ops",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for rich aesthetics, glassmorphism, and status badges
st.markdown(
    """
    <style>
    /* Global Background and Canvas */
    .stApp {
        background-color: #0B0F17;
        color: #F8FAFC;
    }
    
    /* Metric and Card Styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.5);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-success {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-danger {
        background-color: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .badge-info {
        background-color: rgba(99, 102, 241, 0.15);
        color: #818CF8;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    /* Header typography */
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(120deg, #F8FAFC 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Resolve Backend Gateway URL
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1")


def check_backend_health(api_url: str):
    """Probes the FastAPI backend health endpoint."""
    target_url = f"{api_url.rstrip('/')}/health"
    start_time = time.perf_counter()
    try:
        response = requests.get(target_url, timeout=3.0)
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        if response.status_code == 200:
            data = response.json()
            return {
                "online": True,
                "latency_ms": latency,
                "data": data,
                "status_code": response.status_code,
            }
        return {
            "online": False,
            "latency_ms": latency,
            "error": f"HTTP {response.status_code}",
            "status_code": response.status_code,
        }
    except requests.exceptions.RequestException as exc:
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "online": False,
            "latency_ms": latency,
            "error": str(exc),
            "status_code": None,
        }


# ==============================================================================
# SIDEBAR NAVIGATION & CONFIGURATION
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚡ **CloudDesk Control**")
    st.caption("AI Decision-Support System")
    st.markdown("---")

    st.subheader("🌐 Connection Settings")
    configured_api = st.text_input(
        "Backend Gateway URL",
        value=BACKEND_API_URL,
        help="Target URL for FastAPI REST endpoints",
    )

    st.markdown("---")
    st.subheader("📌 System Milestones")
    st.markdown(
        """
        - 🟢 **M1: Foundation & Scaffold** *(Active)*
        - ⚪ **M2: Core Ticket CRUD**
        - ⚪ **M3: AI Triage Engine**
        - ⚪ **M4: Routing & Review Queue**
        - ⚪ **M5: Immutable Audit & Dash**
        - ⚪ **M6: Webhook Ingestion**
        - ⚪ **M7: 100-Ticket Benchmark**
        - ⚪ **M8: Azure Container Deploy**
        """
    )
    st.markdown("---")
    st.caption("Environment: `Development` | Version: `1.0.0`")

# ==============================================================================
# MAIN VIEW: HERO HEADER
# ==============================================================================
col_hero, col_action = st.columns([3, 1])
with col_hero:
    st.markdown('<div class="hero-title">CloudDesk Operations Center</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Intelligent support ticket classification, confidence-gated routing, and human-in-the-loop review.</div>',
        unsafe_allow_html=True,
    )

with col_action:
    refresh_button = st.button("🔄 Probe System Health", use_container_width=True)

# Probe Backend Gateway
health_result = check_backend_health(configured_api)

# ==============================================================================
# SYSTEM STATUS CARDS (KPI METRIC GRID)
# ==============================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    if health_result["online"]:
        overall = health_result["data"].get("status", "healthy")
        badge = "badge-success" if overall == "healthy" else "badge-warning"
        st.markdown(
            f"""
            <div class="metric-card">
                <span class="badge {badge}">API Gateway</span>
                <h3 style="margin-top: 10px; margin-bottom: 2px; color: #10B981;">ONLINE</h3>
                <small style="color: #94A3B8;">HTTP {health_result['status_code']} • {health_result['latency_ms']} ms</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="metric-card">
                <span class="badge badge-danger">API Gateway</span>
                <h3 style="margin-top: 10px; margin-bottom: 2px; color: #EF4444;">OFFLINE</h3>
                <small style="color: #94A3B8;">Check uvicorn service</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col2:
    if health_result["online"]:
        db_info = health_result["data"].get("components", {}).get("database", {})
        db_status = db_info.get("status", "unknown")
        db_color = "#10B981" if db_status == "connected" else "#F59E0B"
        db_badge = "badge-success" if db_status == "connected" else "badge-warning"
        db_latency = db_info.get("latency_ms", "N/A")
        st.markdown(
            f"""
            <div class="metric-card">
                <span class="badge {db_badge}">PostgreSQL</span>
                <h3 style="margin-top: 10px; margin-bottom: 2px; color: {db_color};">{db_status.upper()}</h3>
                <small style="color: #94A3B8;">Latency: {db_latency} ms</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="metric-card">
                <span class="badge badge-warning">PostgreSQL</span>
                <h3 style="margin-top: 10px; margin-bottom: 2px; color: #94A3B8;">STANDBY</h3>
                <small style="color: #94A3B8;">Awaiting API Link</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col3:
    threshold = (
        health_result.get("data", {})
        .get("components", {})
        .get("configuration", {})
        .get("confidence_threshold", 0.85)
    )
    st.markdown(
        f"""
        <div class="metric-card">
            <span class="badge badge-info">Gate Threshold</span>
            <h3 style="margin-top: 10px; margin-bottom: 2px; color: #818CF8;">θ = {threshold}</h3>
            <small style="color: #94A3B8;">Auto-Route Cutoff</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    uptime = health_result.get("data", {}).get("uptime_seconds", 0.0)
    st.markdown(
        f"""
        <div class="metric-card">
            <span class="badge badge-info">Runtime</span>
            <h3 style="margin-top: 10px; margin-bottom: 2px; color: #C084FC;">{uptime}s</h3>
            <small style="color: #94A3B8;">Uptime Tracked</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# PHASE 1 ARCHITECTURE & CONTRACT INSPECTION TABS
# ==============================================================================
tab_overview, tab_diagnostics, tab_contracts = st.tabs(
    ["🏗️ Phase 1 Architecture", "🔍 Live Diagnostic Inspector", "📋 System Contracts & Taxonomy"]
)

with tab_overview:
    st.subheader("Phase 1: Foundation & Scaffold Architecture")
    st.write(
        """
        Phase 1 establishes the decoupled boundary between the **FastAPI REST Gateway** and the 
        **Streamlit Operations UI**, configuring typed settings management, asynchronous database connectivity,
        and health diagnostic contracts.
        """
    )

    st.code(
        """
        [Streamlit Dashboard (Port 8501)]
                      │
                      │  HTTP REST (requests)
                      ▼
        [FastAPI Gateway (Port 8000)]
                      │
           ┌──────────┴──────────┐
           ▼                     ▼
      [Pydantic v2]        [SQLAlchemy 2.0]
     (BaseSettings)       (AsyncSession / asyncpg)
           │                     │
           ▼                     ▼
     [.env Config]       [PostgreSQL DB (Port 5432)]
        """,
        language="text",
    )

    st.info(
        "💡 **Key Architectural Decision:** The Streamlit frontend is strictly decoupled from the database. "
        "It communicates exclusively via HTTP REST APIs, guaranteeing that business rules and schema constraints "
        "are enforced uniformly in FastAPI."
    )

with tab_diagnostics:
    st.subheader("Diagnostic Health Payload")
    if health_result["online"]:
        st.success(f"Successfully reached API Gateway at `{configured_api}/health`")
        st.json(health_result["data"])
    else:
        st.error(f"Could not connect to API Gateway at `{configured_api}/health`")
        st.code(health_result.get("error", "Connection error"), language="text")
        st.markdown(
            """
            **Troubleshooting Steps:**
            1. Make sure the FastAPI backend is running:
               ```powershell
               cd backend
               python -m uvicorn app.main:app --reload --port 8000
               ```
            2. Verify the URL matches in the sidebar (`http://localhost:8000/api/v1`).
            """
        )

with tab_contracts:
    st.subheader("Taxonomy & Classification Standards")
    col_cat, col_team = st.columns(2)

    with col_cat:
        st.markdown("**7 Functional Categories:**")
        st.markdown(
            """
            1. `Authentication` — Login issues, SSO, 2FA, password resets
            2. `Billing` — Invoices, refunds, subscription downgrades/upgrades
            3. `Bug` — Broken functionality, crashes, unexpected errors
            4. `Feature Request` — New product capabilities, improvements
            5. `Performance` — Latency, timeouts, slow page loading
            6. `Security` — Vulnerabilities, unauthorized access, compliance
            7. `General Inquiry` — Documentation questions, how-tos
            """
        )

    with col_team:
        st.markdown("**6 Escalation Teams & Routing Rules:**")
        st.markdown(
            """
            * `Technical Support` ➔ General bugs, inquiries, workflows
            * `Billing & Finance` ➔ Payment failures, invoices, refunds
            * `Engineering` ➔ Code defects, infrastructure regressions
            * `Security & Compliance` ➔ Data privacy, access breaches
            * `Product Management` ➔ Feature requests, feedback
            * `Customer Success` ➔ Account management, onboarding
            """
        )
