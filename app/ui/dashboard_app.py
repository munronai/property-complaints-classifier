"""Pillar 3 Streamlit Application Entrypoint: Multi-Page Navigation via st.Page & st.navigation."""

import os
from pathlib import Path
import re
import sys
import uuid

# Ensure project root is on sys.path when launched via `streamlit run app/ui/dashboard_app.py`
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st  # noqa: E402

from app.ui.views.landing_page import render_landing_page  # noqa: E402
from app.ui.views.mcp_console import render_mcp_console_view  # noqa: E402
from app.ui.views.mcp_guides import (  # noqa: E402
    render_claude_cursor_guide,
    render_mcp_inspector_guide,
)
from app.ui.views.product_insights import render_product_insights_view  # noqa: E402
from app.ui.views.sandbox_dashboard import render_sandbox_dashboard_page  # noqa: E402


def sync_session_id_query_param() -> str:
    """Reads and writes ?session=<id> into URL query parameters for bookmarkable multi-user isolation."""
    query_session = st.query_params.get("session")
    if query_session:
        cleaned = re.sub(r"[^a-zA-Z0-9_-]", "", str(query_session)).strip().lower()[:16]
        session_id = cleaned or uuid.uuid4().hex[:6]
    else:
        session_id = st.session_state.get("sandbox_session_id") or uuid.uuid4().hex[:6]

    st.session_state["sandbox_session_id"] = session_id
    if st.query_params.get("session") != session_id:
        st.query_params["session"] = session_id
    return session_id


def main() -> None:
    """Main Streamlit entrypoint with native st.Page & st.navigation."""
    st.set_page_config(
        page_title="Complaint Classifier & M3NHF SOR Sandbox",
        page_icon="🏘️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    session_id = sync_session_id_query_param()
    docs_url = os.environ.get("SANDBOX_DOCS_URL", "http://127.0.0.1:8000/docs")

    # Define pages with closures so each view receives page references for native st.page_link buttons
    page_refs: dict = {}

    def _home() -> None:
        render_landing_page(
            page_dashboard=page_refs["dashboard"],
            page_research=page_refs["research"],
            page_guide_claude=page_refs["guide_claude"],
            page_mcp=page_refs["mcp"],
            page_guide_inspector=page_refs["guide_inspector"],
        )

    def _dashboard() -> None:
        render_sandbox_dashboard_page()

    def _research() -> None:
        render_product_insights_view(
            session_id=session_id,
            page_home=page_refs["home"],
            page_dashboard=page_refs["dashboard"],
        )

    def _guide_claude() -> None:
        render_claude_cursor_guide(
            session_id=session_id,
            page_dashboard=page_refs["dashboard"],
            page_mcp=page_refs["mcp"],
        )

    def _mcp() -> None:
        render_mcp_console_view(
            session_id=session_id,
            page_dashboard=page_refs["dashboard"],
            page_guide_claude=page_refs["guide_claude"],
            page_guide_inspector=page_refs["guide_inspector"],
        )

    def _guide_inspector() -> None:
        render_mcp_inspector_guide(
            session_id=session_id,
            page_mcp=page_refs["mcp"],
        )

    page_refs["home"] = st.Page(
        _home,
        title="Overview & Guided Walkthrough",
        icon="🧭",
        default=True,
        url_path="overview",
    )
    page_refs["dashboard"] = st.Page(
        _dashboard,
        title="Live Sandbox Dashboard",
        icon="🎛️",
        url_path="sandbox",
    )
    page_refs["research"] = st.Page(
        _research,
        title="Research & Product Decisions",
        icon="📘",
        url_path="research",
    )
    page_refs["guide_claude"] = st.Page(
        _guide_claude,
        title="Guide: Claude & Cursor (Option 1)",
        icon="🖥️",
        url_path="mcp-claude-cursor",
    )
    page_refs["mcp"] = st.Page(
        _mcp,
        title="Console: MCP Agent (Option 2)",
        icon="🤖",
        url_path="mcp-console",
    )
    page_refs["guide_inspector"] = st.Page(
        _guide_inspector,
        title="Guide: MCP Inspector (Option 3)",
        icon="🔍",
        url_path="mcp-inspector",
    )

    pg = st.navigation(
        {
            "Sandbox Core": [
                page_refs["home"],
                page_refs["dashboard"],
                page_refs["research"],
            ],
            "MCP Integration Guides": [
                page_refs["guide_claude"],
                page_refs["mcp"],
                page_refs["guide_inspector"],
            ],
        }
    )

    with st.sidebar:
        st.caption(f"🔒 **Isolated Session:** `{session_id}` (`?session={session_id}`)")
        st.markdown(f"📖 **[OpenAPI `/docs` ↗]({docs_url})**")

    pg.run()


if __name__ == "__main__":
    main()
