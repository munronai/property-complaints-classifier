"""Real-time Telemetry KPI Header and Non-Blocking Error Banner component."""

from typing import Any, Dict
import streamlit as st

from app.ui.api_client import api_client


def render_error_banner() -> None:
    """Renders a dismissible alert banner if st.session_state['last_api_error'] is set."""
    err = st.session_state.get("last_api_error")
    if err:
        col_msg, col_btn = st.columns([0.88, 0.12])
        with col_msg:
            st.error(f"**Non-Blocking Resilience Alert:** {err}")
        with col_btn:
            if st.button("Dismiss", key="dismiss_api_err_btn", use_container_width=True):
                api_client.clear_error()
                st.rerun()


def render_kpi_header(session_id: str) -> Dict[str, Any]:
    """Fetches and renders the real-time workspace telemetry KPI bar."""
    render_error_banner()
    telemetry = api_client.get_telemetry(session_id=session_id)

    total = telemetry.get("total_tickets", 0)
    auto_rate = telemetry.get("auto_dispatch_rate", 0.0) * 100.0
    awaabs = telemetry.get("awaabs_law_intercepts", 0)
    emerg = telemetry.get("emergency_escalations", 0)
    reroutes = telemetry.get("wip_and_finance_reroutes", 0)
    recalls = telemetry.get("completed_job_recalls", 0)
    discards = telemetry.get("inappropriate_discards", 0)
    mean_sor_conf = telemetry.get("mean_sor_confidence", 0.0) * 100.0

    cols = st.columns(7)
    cols[0].metric(
        "Triaged Tickets",
        f"{total}",
        help=f"Active workspace: s_{session_id}_*",
    )
    cols[1].metric(
        "Auto-Dispatch Rate",
        f"{auto_rate:.0f}%",
        help="Percentage of tickets passing all confidence, margin, and statutory gates for direct HMS dispatch",
    )
    cols[2].metric(
        "Awaab's Law / Emergency",
        f"{awaabs + emerg}",
        delta=f"{awaabs} Damp | {emerg} SLA-3",
        delta_color="inverse",
        help="Statutory damp & mould hazards + 24-hour Priority 3 emergency intercepts",
    )
    cols[3].metric(
        "WIP & Finance Re-Routes",
        f"{reroutes}",
        help="Work-in-progress status updates, contractor scheduling, and late-payment queries diverted before Stage 2",
    )
    cols[4].metric(
        "Completed-Job Recalls",
        f"{recalls}",
        help="Complaints about completed repair jobs assessed with M3NHF SOR codes and routed for contractor recall",
    )
    cols[5].metric(
        "Safety Media Purges",
        f"{discards}",
        help="Inappropriate/rude photo submissions flagged in Stage 1 with raw media bytes discarded",
    )
    cols[6].metric(
        "Mean SOR Confidence",
        f"{mean_sor_conf:.1f}%",
        help="Mean Stage 2 TypeSafe Jev probability across evaluated M3NHF SOR selections",
    )

    return telemetry
