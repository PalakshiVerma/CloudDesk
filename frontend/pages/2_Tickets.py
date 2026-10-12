"""CloudDesk — Ticket Management & Explorer.

Provides interactive ticket creation, search/filtering, and detailed inspection.
"""

import os
from datetime import datetime
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Ticket Explorer — CloudDesk",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0B0F17;
        color: #F8FAFC;
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 16px;
        backdrop-filter: blur(10px);
        margin-bottom: 12px;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-pending { background-color: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-routed { background-color: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-review { background-color: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-closed { background-color: rgba(148, 163, 184, 0.15); color: #94A3B8; border: 1px solid rgba(148, 163, 184, 0.3); }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(120deg, #F8FAFC 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# API Configuration
API_BASE = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/api/v1").rstrip("/")


# Helper API fetchers
@st.cache_data(ttl=10)
def fetch_teams():
    """Fetch active teams from backend."""
    try:
        res = requests.get(f"{API_BASE}/tickets/teams", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []


def fetch_stats():
    """Fetch aggregate ticket stats."""
    try:
        res = requests.get(f"{API_BASE}/tickets/stats", timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {"total": 0, "pending_triage": 0, "auto_routed": 0, "needs_review": 0, "closed": 0}


def fetch_tickets(status_filter=None, priority_filter=None, category_filter=None, search_filter=None):
    """Fetch tickets list with filters."""
    params = {"page": 1, "page_size": 50}
    if status_filter and status_filter != "All":
        params["status"] = status_filter
    if priority_filter and priority_filter != "All":
        params["priority"] = priority_filter
    if category_filter and category_filter != "All":
        params["category"] = category_filter
    if search_filter:
        params["search"] = search_filter

    try:
        res = requests.get(f"{API_BASE}/tickets", params=params, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception as exc:
        st.error(f"Error connecting to backend: {exc}")
    return {"items": [], "total": 0, "page": 1, "page_size": 50, "total_pages": 1}


# ==============================================================================
# HEADER
# ==============================================================================
col_title, col_btn = st.columns([3, 1])
with col_title:
    st.markdown('<div class="hero-title">🎫 Support Ticket Management</div>', unsafe_allow_html=True)
    st.caption("Live ticket ingestion, priority filtering, and lifecycle state management powered by Neon PostgreSQL.")

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    refresh_btn = st.button("🔄 Refresh Data", use_container_width=True)

teams_data = fetch_teams()
stats_data = fetch_stats()

# ==============================================================================
# KPI METRIC CARDS
# ==============================================================================
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.markdown(
        f"""
        <div class="metric-card">
            <span style="color: #94A3B8; font-size: 0.8rem; font-weight: 600;">TOTAL TICKETS</span>
            <h2 style="margin: 4px 0 0 0; color: #F8FAFC;">{stats_data.get('total', 0)}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        f"""
        <div class="metric-card">
            <span style="color: #F59E0B; font-size: 0.8rem; font-weight: 600;">PENDING TRIAGE</span>
            <h2 style="margin: 4px 0 0 0; color: #F59E0B;">{stats_data.get('pending_triage', 0)}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(
        f"""
        <div class="metric-card">
            <span style="color: #10B981; font-size: 0.8rem; font-weight: 600;">AUTO-ROUTED</span>
            <h2 style="margin: 4px 0 0 0; color: #10B981;">{stats_data.get('auto_routed', 0)}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m4:
    st.markdown(
        f"""
        <div class="metric-card">
            <span style="color: #EF4444; font-size: 0.8rem; font-weight: 600;">NEEDS REVIEW</span>
            <h2 style="margin: 4px 0 0 0; color: #EF4444;">{stats_data.get('needs_review', 0)}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m5:
    st.markdown(
        f"""
        <div class="metric-card">
            <span style="color: #818CF8; font-size: 0.8rem; font-weight: 600;">ACTIVE TEAMS</span>
            <h2 style="margin: 4px 0 0 0; color: #818CF8;">{len(teams_data)}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ==============================================================================
# CREATE TICKET EXPANDER FORM
# ==============================================================================
with st.expander("➕ **Submit a New Support Ticket**", expanded=False):
    with st.form("create_ticket_form", clear_on_submit=True):
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            customer_email = st.text_input("Customer Email *", placeholder="customer@company.com")
            category_choice = st.selectbox(
                "Category (Optional)",
                ["None", "Account", "Billing", "Payment", "Technical", "Security", "Integration", "General"],
            )
        with fcol2:
            priority_choice = st.selectbox(
                "Priority (Optional)",
                ["None", "low", "medium", "high", "critical"],
            )
            team_options = {"None": None}
            for t in teams_data:
                team_options[t["name"]] = t["id"]
            team_choice = st.selectbox("Assign Team (Optional)", list(team_options.keys()))

        subject = st.text_input("Subject *", placeholder="Brief description of the problem")
        description = st.text_area("Ticket Description *", placeholder="Detailed explanation, error codes, steps to reproduce...")

        submitted = st.form_submit_button("🚀 Submit Support Ticket", use_container_width=True)
        if submitted:
            if not customer_email or not subject or not description:
                st.error("Please fill in Customer Email, Subject, and Description.")
            elif "@" not in customer_email:
                st.error("Please provide a valid email address.")
            elif len(description) < 10:
                st.error("Description must be at least 10 characters.")
            else:
                payload = {
                    "customer_email": customer_email.strip(),
                    "subject": subject.strip(),
                    "description": description.strip(),
                    "category": None if category_choice == "None" else category_choice,
                    "priority": None if priority_choice == "None" else priority_choice,
                    "assigned_team_id": team_options.get(team_choice),
                }
                try:
                    res = requests.post(f"{API_BASE}/tickets", json=payload, timeout=8)
                    if res.status_code == 201:
                        data = res.json()
                        st.success(f"✅ Ticket created successfully! ID: `{data['id']}`")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"Failed to create ticket: {res.text}")
                except Exception as exc:
                    st.error(f"Error sending request: {exc}")

# ==============================================================================
# FILTER TOOLBAR
# ==============================================================================
st.subheader("🔍 Filter & Search")
scol1, scol2, scol3, scol4 = st.columns([2, 1, 1, 1])

with scol1:
    search_query = st.text_input("Search tickets", placeholder="Search by subject, description, or email...", label_visibility="collapsed")
with scol2:
    status_filter = st.selectbox("Status", ["All", "pending_triage", "auto_routed", "needs_review", "reviewed", "closed"], label_visibility="collapsed")
with scol3:
    priority_filter = st.selectbox("Priority", ["All", "low", "medium", "high", "critical"], label_visibility="collapsed")
with scol4:
    category_filter = st.selectbox("Category", ["All", "Account", "Billing", "Payment", "Technical", "Security", "Integration", "General"], label_visibility="collapsed")

# Fetch data
tickets_response = fetch_tickets(
    status_filter=status_filter,
    priority_filter=priority_filter,
    category_filter=category_filter,
    search_filter=search_query,
)

tickets_list = tickets_response.get("items", [])
total_count = tickets_response.get("total", 0)

st.caption(f"Showing **{len(tickets_list)}** of **{total_count}** tickets.")

if not tickets_list:
    st.info("No tickets found matching your filter criteria. Use the **➕ Submit a New Support Ticket** form above to create the first one!")
else:
    for ticket in tickets_list:
        tid = ticket["id"]
        status_val = ticket.get("status", "pending_triage")
        priority_val = ticket.get("priority") or "unassigned"
        category_val = ticket.get("category") or "General"
        team_name = ticket.get("assigned_team", {}).get("name") if ticket.get("assigned_team") else "Unassigned"
        created_str = ticket.get("created_at", "")[:19].replace("T", " ")

        # Color badges
        badge_cls = "badge-pending"
        if status_val == "auto_routed":
            badge_cls = "badge-routed"
        elif status_val == "needs_review":
            badge_cls = "badge-review"
        elif status_val == "closed":
            badge_cls = "badge-closed"

        with st.expander(f"**[{priority_val.upper()}]** {ticket['subject']} — `{ticket['customer_email']}`"):
            dcol1, dcol2 = st.columns([3, 1])
            with dcol1:
                st.markdown(f"**Description:**")
                st.write(ticket["description"])
                st.caption(f"**Created:** {created_str} UTC | **ID:** `{tid}`")
            with dcol2:
                st.markdown(f"**Status:** <span class='badge {badge_cls}'>{status_val}</span>", unsafe_allow_html=True)
                st.markdown(f"**Category:** `{category_val}`")
                st.markdown(f"**Assigned Team:** `{team_name}`")

                # Action to update ticket status
                new_status = st.selectbox(
                    "Update Status",
                    ["pending_triage", "auto_routed", "needs_review", "reviewed", "closed"],
                    index=["pending_triage", "auto_routed", "needs_review", "reviewed", "closed"].index(status_val) if status_val in ["pending_triage", "auto_routed", "needs_review", "reviewed", "closed"] else 0,
                    key=f"status_{tid}",
                )
                if new_status != status_val:
                    if st.button("Save Status", key=f"btn_{tid}"):
                        try:
                            patch_res = requests.patch(
                                f"{API_BASE}/tickets/{tid}",
                                json={"status": new_status},
                                timeout=5,
                            )
                            if patch_res.status_code == 200:
                                st.success("Status updated!")
                                st.rerun()
                            else:
                                st.error(f"Failed: {patch_res.text}")
                        except Exception as e:
                            st.error(str(e))
