"""Below-the-cards Help Guide and Time-Machine Preset Reference Table."""

import pandas as pd
import streamlit as st

from app.domain.presets import SCENARIO_PRESETS


def render_help_and_presets_section(show_quick_launch: bool = True) -> None:
    """Renders the step-by-step usage guide and detailed preset reference table below the two landing Option Cards."""
    st.markdown("---")
    st.markdown("## 📖 How to Use This System & What the Presets Are For")
    st.markdown(
        "This section explains how to test the complaint classification pipeline and what each of the "
        "**9 Time-Machine Scenario Presets** is designed to validate."
    )

    col_guide_1, col_guide_2 = st.columns(2)

    with col_guide_1:
        st.markdown(
            """
            ### 🛠️ Step-by-Step Testing Guide
            1. **Test Custom Resident & WhatsApp Inputs (`Live Intake` Tab)**:
               - Type any complaint description or pick a sample message.
               - Attach your own photo or choose one of the **6 built-in synthetic defect photos** (e.g., *Black Mould on Window Reveal*, *Under-Sink Pipe/Trap Leak*, *Broken Kitchen Hinge*, or *Inappropriate Photo Fixture*).
               - Switch between **Resident Web Dashboard** and **WhatsApp Business Webhook** to test multi-channel ingestion.
            2. **Tune Circuit-Breaker Sliders in the Left Sidebar**:
               - Dynamically adjust `Min Trade Confidence`, `Min M3NHF SOR Confidence`, `Min Top-1 vs Top-2 Margin`, and `Awaab's Law Damp Cutoff` to observe how policy changes shift tickets between **Auto-Dispatch (`AUTO_DISPATCH_HMS`)** and **Human Review (`SURVEYOR_DESK_REVIEW`)**.
            """
        )

    with col_guide_2:
        st.markdown(
            """
            ### 🔍 Inspecting Outcomes, Recalls & Agent Access
            3. **Verify Intent Re-Routing & Completed-Job Recalls**:
               - Test messages chasing a **work-in-progress (WIP) repair**, **rescheduling a contractor**, or **chasing late invoice payment**—watch Stage 1 divert them before Stage 2 SOR matching so zero duplicate works orders are raised.
               - Test **complaints about completed repair jobs**—watch the system run **both** Stage 1 and Stage 2 to scope the remedial M3NHF SOR code while routing to `QUALITY_RECALL_SURVEYOR_REVIEW` so the landlord recalls the original contractor instead of paying twice.
            4. **Surveyor Review Queue & Embedded MCP Console**:
               - Use the **Surveyor Desk** tab to override/approve M3NHF SOR codes on escalated tickets, or open the **Embedded MCP Console** to test JSON-RPC tool calls (`submit_complaint_triage`, `simulate_complaint_event`, `approve_or_override_work_order`).
            """
        )

    st.markdown("### ⏱️ What the 9 Time-Machine Scenario Presets Are For")
    st.caption(
        "Each preset is calibrated to demonstrate a specific real-world operational scenario, statutory circuit breaker, "
        "or edge case identified in social housing repairs triage:"
    )

    preset_rows = []
    for p in SCENARIO_PRESETS:
        preset_rows.append(
            {
                "Preset": p.title,
                "Channel": p.channel.value,
                "What It Tests (Product & Gating Rationale)": p.what_it_tests,
                "Expected Gating Flags": ", ".join(r.value for r in p.expected_reasons) or "NONE (Clean Pass)",
                "Expected Routing Destination": p.expected_destination.value,
            }
        )

    st.dataframe(
        pd.DataFrame(preset_rows),
        use_container_width=True,
        hide_index=True,
    )

    if show_quick_launch:
        with st.expander("🚀 Quick-Launch a Scenario Preset Directly Into the Sandbox"):
            q_col1, q_col2 = st.columns([0.75, 0.25])
            preset_map = {p.preset_id: p.title for p in SCENARIO_PRESETS}
            with q_col1:
                chosen_preset_id = st.selectbox(
                    "Choose a preset to inspect in the Sandbox Control Deck",
                    options=list(preset_map.keys()),
                    format_func=lambda pid: preset_map[pid],
                    key="landing_quick_launch_select",
                )
            with q_col2:
                st.write("")
                if st.button("Run Preset in Sandbox →", use_container_width=True, type="primary"):
                    st.session_state["pending_preset_to_run"] = chosen_preset_id
                    st.session_state["active_page"] = "SANDBOX"
                    st.session_state["active_sandbox_tab"] = "TIME_MACHINE"
                    st.rerun()
