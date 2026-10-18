"""Page 1: Prototype Landing Page (Overview, Option Cards & Guided Walkthrough — No Cluttered Stats Bar)."""

from typing import Any
import streamlit as st

from app.ui.components.help_and_presets import render_help_and_presets_section


def render_landing_page(
    page_dashboard: Any,
    page_research: Any,
    page_guide_claude: Any,
    page_mcp: Any,
    page_guide_inspector: Any,
) -> None:
    """Renders the clean Landing Page with summary description, 2 main Option Cards, 3 MCP cards, and below-the-fold guide."""
    st.title("🏘️ Social Housing & Property Repairs Triage Sandbox")
    st.subheader(
        "Eliminating Contractor Mis-Dispatch, Wasted Callouts & Awaab's Law Compliance Risks with Two-Stage TypeSafe Jev + M3NHF SOR Gating"
    )

    st.markdown(
        """
        Welcome to the **Social Housing & Property Complaint Classifier Prototype**.
        In property management, resident repair channels (**Web Portals** and **WhatsApp**) are flooded with a mix of
        urgent emergencies, vague descriptions with sideways smartphone photos, work-in-progress (WIP) status chasers,
        complaints about botched completed repairs, and statutory **Awaab's Law** damp and mould hazards.

        This prototype demonstrates how a **Two-Stage Multimodal TypeSafe Jev Engine** paired with **M3NHF Schedule of Rates (SOR) codes**
        and a **Hard Circuit-Breaker Middleware (`TriageEscalationGuard`)** safely automates unambiguous repairs while intercepting
        statutory risks, non-repair updates, completed-job recalls, and inappropriate media before a contractor is ever dispatched.
        """
    )

    # Two Primary Option Cards Side-by-Side (Native st.page_link navigation)
    cta_col1, cta_col2 = st.columns(2, gap="large")
    with cta_col1:
        with st.container(border=True):
            st.markdown("### 🎛️ Option 1: Launch the Interactive Sandbox")
            st.write(
                "Select a social housing or commercial property, test the 9 one-click scenario presets, submit custom "
                "Web or WhatsApp complaints with defect photos, toggle between Simulated and Live Jev API, and tune "
                "confidence/margin thresholds with instant visual feedback."
            )
            st.page_link(
                page_dashboard,
                label="Open Live Sandbox Dashboard →",
                icon="🚀",
                use_container_width=True,
            )

    with cta_col2:
        with st.container(border=True):
            st.markdown("### 🧠 Option 2: Product Thinking, Insights & Decisions")
            st.write(
                "Explore the domain research from UK Housing Ombudsman & Commercial Tribunal datasets, why 35%–45% of "
                "messages are non-new-repair updates, why completed-job recalls still require SOR scoping, and why "
                "Two-Stage Jev + Margin Gating beats raw LLM chat."
            )
            st.page_link(
                page_research,
                label="Read Product Thinking & Decisions →",
                icon="📐",
                use_container_width=True,
            )

    st.markdown("### 🤖 Model Context Protocol (MCP) Agent Integrations (Showcasing Pillar 2)")
    g_col1, g_col2, g_col3 = st.columns(3)
    with g_col1:
        with st.container(border=True):
            st.markdown("#### 🔌 Claude Desktop & Cursor (Option 1)")
            st.write(
                "Connect Claude or Cursor over `/mcp/sse` and see the exact natural-language prompts that trigger each M3NHF tool and preset."
            )
            st.page_link(
                page_guide_claude,
                label="Open Claude & Cursor Setup + Prompt Guide →",
                icon="🔌",
                use_container_width=True,
            )
    with g_col2:
        with st.container(border=True):
            st.markdown("#### 🤖 Interactive MCP Agent Console (Option 2)")
            st.write(
                "Run live MCP tool handshakes, execute all 9 preset prompts over JSON-RPC, and inspect resources right inside your browser."
            )
            st.page_link(
                page_mcp,
                label="Open Interactive MCP Agent Console →",
                icon="🤖",
                use_container_width=True,
            )
    with g_col3:
        with st.container(border=True):
            st.markdown("#### 🔬 Official MCP Inspector (Option 3)")
            st.write(
                "Use the official zero-install `npx @modelcontextprotocol/inspector` visualizer to test tool schemas and SSE streams."
            )
            st.page_link(
                page_guide_inspector,
                label="Open Official MCP Inspector Guide →",
                icon="🔬",
                use_container_width=True,
            )

    # Below the Cards: Step-by-Step Help Content, 4-Stage Rationale & 9-Preset Guide
    render_help_and_presets_section(show_quick_launch=False)
