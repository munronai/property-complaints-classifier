"""Pillar 3 Streamlit Application Entrypoint: Landing Page, Two Option Cards, Product Insights & Sandbox Control Deck."""

from pathlib import Path
import sys
import uuid

# Ensure project root is on sys.path when launched via `streamlit run app/ui/dashboard_app.py`
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st  # noqa: E402

from app.ui.components.kpi_header import render_kpi_header  # noqa: E402
from app.ui.components.threshold_sidebar import render_sidebar  # noqa: E402
from app.ui.views.landing_page import render_landing_page  # noqa: E402
from app.ui.views.live_intake import render_live_intake_view  # noqa: E402
from app.ui.views.mcp_console import render_mcp_console_view  # noqa: E402
from app.ui.views.product_insights import render_product_insights_view  # noqa: E402
from app.ui.views.surveyor_desk import render_surveyor_desk_view  # noqa: E402
from app.ui.views.time_machine import render_time_machine_view  # noqa: E402


def sync_session_id_query_param() -> str:
    """Reads and writes ?session=<id> into URL query parameters for bookmarkable multi-user isolation."""
    query_session = st.query_params.get("session")
    if query_session:
        st.session_state["sandbox_session_id"] = str(query_session)
    elif "sandbox_session_id" not in st.session_state:
        st.session_state["sandbox_session_id"] = uuid.uuid4().hex[:6]

    active_sid = st.session_state["sandbox_session_id"]
    if st.query_params.get("session") != active_sid:
        st.query_params["session"] = active_sid
    return active_sid


def render_sandbox_workbench(session_id: str, thresholds: dict[str, float]) -> None:
    """Renders the 4-Tab Interactive Sandbox & Visual Control Deck (Option Card 1)."""
    top_c1, top_c2 = st.columns([0.78, 0.22])
    with top_c1:
        st.markdown("# 🧪 Interactive Sandbox & Visual Control Deck")
        st.caption(
            f"Multi-Channel Complaint Triage, TypeSafe Jev + M3NHF SOR Classification & Gating Workbench (`s_{session_id}_*`)"
        )
    with top_c2:
        st.write("")
        if st.button("← Back to Landing Page", key="sandbox_back_landing", use_container_width=True):
            st.session_state["active_page"] = "LANDING"
            st.rerun()
        if st.button("📘 Product Insights →", key="sandbox_go_insights", use_container_width=True):
            st.session_state["active_page"] = "INSIGHTS"
            st.rerun()

    render_kpi_header(session_id=session_id)

    # If redirected from Landing Page Quick-Launch, show Time-Machine first
    default_tab_order = [
        "📨 1. Live Multi-Channel Intake (Web & WhatsApp)",
        "⏱️ 2. Time-Machine Scenario Deck (9 Presets)",
        "👷 3. Surveyor Review Queue & M3NHF Catalog",
        "🤖 4. Embedded MCP Agent Console",
    ]
    if st.session_state.pop("active_sandbox_tab", None) == "TIME_MACHINE":
        st.info("👇 Opened **Time-Machine Scenario Deck** from Landing Page quick-launch.")

    tab_intake, tab_presets, tab_surveyor, tab_mcp = st.tabs(default_tab_order)

    with tab_intake:
        render_live_intake_view(session_id=session_id, thresholds=thresholds)

    with tab_presets:
        render_time_machine_view(session_id=session_id, thresholds=thresholds)

    with tab_surveyor:
        render_surveyor_desk_view(session_id=session_id)

    with tab_mcp:
        render_mcp_console_view(session_id=session_id)


def main() -> None:
    """Main Streamlit entrypoint."""
    st.set_page_config(
        page_title="Social Housing & Property Complaint Classifier Sandbox",
        page_icon="🏘️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "LANDING"

    session_id = sync_session_id_query_param()
    thresholds = render_sidebar(session_id=session_id)

    active_page = st.session_state.get("active_page", "LANDING")
    if active_page == "SANDBOX":
        render_sandbox_workbench(session_id=session_id, thresholds=thresholds)
    elif active_page == "INSIGHTS":
        render_product_insights_view(session_id=session_id)
    else:
        render_landing_page(session_id=session_id)


if __name__ == "__main__":
    main()
