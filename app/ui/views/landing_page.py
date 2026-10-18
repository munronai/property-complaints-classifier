"""Prototype Landing Page with Summary Description, Two Option Cards, and Below-the-Cards Help & Preset Guide."""

import streamlit as st

from app.ui.components.help_and_presets import render_help_and_presets_section
from app.ui.components.kpi_header import render_kpi_header


def render_landing_page(session_id: str) -> None:
    """Renders the Landing Page with executive summary, 2 primary Option Cards, and help/preset reference below."""
    st.markdown(
        """
        # 🏘️ Social Housing & Property Complaint Classifier Prototype
        ### AI-Native Multimodal Intake, M3NHF SOR Classification & Statutory Circuit-Breaker Sandbox
        """
    )

    st.info(
        "**Prototype Summary:** This platform demonstrates how social housing providers and commercial property "
        "managers can safely automate multi-channel repair complaint triage (**Web Portal** & **WhatsApp**) "
        "using **TypeSafe Jev** and **M3NHF Schedule of Rates (SOR) codes**. To eliminate contractor mis-dispatch "
        "and statutory compliance failures, the pipeline combines a **Two-Stage Multimodal Assessment Engine** "
        "with a **Hard Circuit-Breaker Middleware (`TriageEscalationGuard`)** that intercepts **Awaab's Law** damp "
        "hazards, **24-hour emergencies**, **ambiguous SOR probability margins ($<0.15$)**, **WIP/scheduling/finance "
        "inquiries**, **completed-repair workmanship recalls**, and **inappropriate photo submissions**."
    )

    render_kpi_header(session_id=session_id)
    st.write("")

    # Two Primary Option Cards Side-by-Side
    card_col1, card_col2 = st.columns(2, gap="large")

    with card_col1:
        with st.container(border=True):
            st.markdown("## 🧪 Option 1: Interactive Sandbox & Control Deck")
            st.markdown(
                """
                **Hands-on testing workbench for evaluating the end-to-end classification & gating pipeline:**
                - **Live Multi-Channel Intake**: Submit resident or contractor messages via **Dashboard UI** or **WhatsApp Business Webhook Simulator** with uploaded or synthetic defect photos.
                - **9 Time-Machine Scenario Presets**: One-click injection of calibrated edge cases (Clean Plumbing Dispatch, Ambiguous Margin Trap, Awaab's Law Black Mould, Priority 3 Ceiling Rose Leak, Completed-Job Recall, WIP Update Re-Route, Contractor Late Payment, and Inappropriate Photo Purge).
                - **Real-Time Policy Tuning**: Adjust confidence, margin, and damp sliders in the sidebar to see live routing changes.
                - **Surveyor Review Queue & Embedded MCP Console**: Override M3NHF SOR codes or invoke FastMCP agent tools in-browser.
                """
            )
            if st.button(
                "Launch Sandbox & Control Deck →",
                key="btn_card_sandbox",
                type="primary",
                use_container_width=True,
            ):
                st.session_state["active_page"] = "SANDBOX"
                st.rerun()

    with card_col2:
        with st.container(border=True):
            st.markdown("## 📘 Option 2: Product Thinking, Insights & Decisions")
            st.markdown(
                r"""
                **Deep dive into the domain research, product rationale, and architectural trade-offs behind this system:**
                - **The Real-World Intake Problem**: Why 35%–45% of incoming housing messages are *not* new repairs (UK Housing Ombudsman & Commercial Property statistical breakdowns).
                - **Completed-Repair Recalls vs. WIP Updates**: Why WIP/scheduling/finance chasers must short-circuit Stage 2, whereas complaints about *completed* repair jobs must undergo full Jev + M3NHF SOR assessment to hold contractors accountable.
                - **Two-Stage TypeSafe Jev vs. Raw LLM Chat**: How trade-bounded candidate sets and Top-1 vs. Top-2 margin gating ($\ge 0.15$) prevent hallucinated SOR codes.
                - **Safety & Statutory Guardrails**: Awaab's Law circuit breakers and Stage 1 inappropriate photo purging.
                """
            )
            if st.button(
                "Explore Product Thinking & Insights →",
                key="btn_card_insights",
                type="secondary",
                use_container_width=True,
            ):
                st.session_state["active_page"] = "INSIGHTS"
                st.rerun()

    # Below the Two Option Cards: Help Content & Preset Guide
    render_help_and_presets_section(show_quick_launch=True)
