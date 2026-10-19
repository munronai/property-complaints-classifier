"""Sidebar Navigation Switcher, Gating Threshold Sliders, and Session/Admin Workspace Controls."""

from typing import Dict
import streamlit as st

from app.config import settings
from app.ui.api_client import api_client


def render_sidebar(session_id: str) -> Dict[str, float]:
    """Renders top-level view switcher, live policy threshold sliders, and session reset controls."""
    with st.sidebar:
        st.markdown("### 🧭 Prototype Navigation")
        current_view = st.session_state.get("active_page", "LANDING")

        nav_options = {
            "LANDING": "🏠 Landing Page & Help Guide",
            "SANDBOX": "🧪 Interactive Sandbox & Control Deck",
            "INSIGHTS": "📘 Product Thinking & Decisions",
        }
        selected_page = st.radio(
            "Select View",
            options=list(nav_options.keys()),
            format_func=lambda k: nav_options[k],
            index=list(nav_options.keys()).index(current_view),
            key="sidebar_page_radio",
        )
        if selected_page != current_view:
            st.session_state["active_page"] = selected_page
            st.rerun()

        st.divider()
        st.markdown("### 🔐 Session Isolation")
        st.caption(
            f"**Workspace ID:** `?session={session_id}`  \n"
            f"**Scoped Prefix:** `s_{session_id}_*`"
        )

        engine_mode = st.selectbox(
            "TypeSafe Jev Engine Mode",
            options=["SIMULATED", "LIVE"],
            index=0,
            help=(
                "SIMULATED: Deterministic sub-millisecond calibrated mathematical model. "
                "LIVE: Real-time HTTP calls to https://api.typesafe.ai/v1/systemone."
            ),
            key="engine_mode_select",
        )
        st.session_state["engine_mode"] = engine_mode

        st.divider()
        st.markdown("### ⚙️ Circuit-Breaker Thresholds")
        st.caption(
            "Adjust thresholds to test how `TriageEscalationGuard` alters routing outcomes:"
        )

        min_trade_conf = st.slider(
            "Min Trade Confidence",
            min_value=0.40,
            max_value=0.95,
            value=float(
                st.session_state.get(
                    "min_trade_confidence", settings.min_trade_confidence
                )
            ),
            step=0.05,
            help="Stage 1 primary trade probability below this threshold routes to SURVEYOR_DESK_REVIEW.",
        )
        min_sor_conf = st.slider(
            "Min M3NHF SOR Confidence",
            min_value=0.40,
            max_value=0.95,
            value=float(
                st.session_state.get("min_sor_confidence", settings.min_sor_confidence)
            ),
            step=0.05,
            help="Stage 2 selected SOR probability below this threshold routes to SURVEYOR_DESK_REVIEW.",
        )
        min_margin = st.slider(
            "Min Top-1 vs Top-2 SOR Margin",
            min_value=0.05,
            max_value=0.50,
            value=float(
                st.session_state.get(
                    "min_probability_margin", settings.min_probability_margin
                )
            ),
            step=0.05,
            help="Minimum required gap between #1 and #2 candidate SOR codes (catches ambiguous defects).",
        )
        damp_threshold = st.slider(
            "Awaab's Law Damp Hazard Cutoff",
            min_value=0.15,
            max_value=0.85,
            value=float(
                st.session_state.get(
                    "damp_hazard_threshold", settings.damp_hazard_threshold
                )
            ),
            step=0.05,
            help="Damp/mould probability at or above this threshold forces routing to DISREPAIR_LEGAL_TEAM.",
        )
        inappropriate_threshold = st.slider(
            "Content Safety Discard Cutoff",
            min_value=0.25,
            max_value=0.90,
            value=float(
                st.session_state.get(
                    "inappropriate_content_threshold",
                    settings.inappropriate_content_threshold,
                )
            ),
            step=0.05,
            help="Stage 1 inappropriate content probability >= this value halts triage and purges media bytes.",
        )

        thresholds_dict = {
            "min_trade_confidence": min_trade_conf,
            "min_sor_confidence": min_sor_conf,
            "min_probability_margin": min_margin,
            "damp_hazard_threshold": damp_threshold,
            "inappropriate_content_threshold": inappropriate_threshold,
        }
        st.session_state["active_thresholds"] = thresholds_dict

        st.divider()
        st.markdown("### 🔄 Workspace Reset & Admin Gate")
        if st.button(
            "Reset My Workspace (s_" + session_id + "_*)", use_container_width=True
        ):
            res = api_client.reset_workspace(session_id=session_id, reset_all=False)
            if res:
                st.success(f"Workspace `s_{session_id}_*` reseeded to Golden Baseline.")
                st.rerun()

        with st.expander("🔒 Protected Global Wipe (Admin Only)"):
            admin_key_input = st.text_input(
                "Enter SANDBOX_ADMIN_KEY",
                type="password",
                help="Default sandbox key: sor-admin-secret-2026",
                key="admin_key_password_input",
            )
            if st.button(
                "Wipe All Sessions & Reseed Baseline", use_container_width=True
            ):
                res = api_client.reset_workspace(
                    session_id=session_id,
                    reset_all=True,
                    admin_key=admin_key_input,
                )
                if res:
                    st.success(
                        "Global wipe complete! All sessions and Golden Baseline reseeded."
                    )
                    st.rerun()

    return thresholds_dict
