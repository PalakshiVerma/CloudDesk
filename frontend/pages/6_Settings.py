"""System Settings & Routing Thresholds."""
import streamlit as st

st.set_page_config(page_title="Settings — CloudDesk", page_icon="⚙️", layout="wide")
st.title("⚙️ System Configuration")
st.caption("Inspect and manage active decision thresholds and external service connections.")

st.subheader("🎯 Triage Parameters")
threshold = st.slider(
    "Confidence Threshold (θ)",
    min_value=0.50,
    max_value=0.99,
    value=0.85,
    step=0.01,
    help="Tickets with AI confidence ≥ θ are auto-routed. Tickets below θ divert to the Human Review Queue.",
)
st.write(f"Current operational threshold: **{threshold}**")

st.markdown("---")
st.subheader("🔗 Service Endpoints")
st.text_input("FastAPI Gateway", value="http://localhost:8000/api/v1", disabled=True)
st.text_input("Qdrant Vector Engine", value="http://localhost:6333", disabled=True)
st.text_input("PostgreSQL Relational DB", value="localhost:5432 (clouddesk_db)", disabled=True)
