"""Sandbox Tab 2: Time-Machine Scenario Injection Deck & Batch Preset Evaluator."""

from typing import Dict
import pandas as pd
import streamlit as st

from app.domain.presets import SCENARIO_PRESETS
from app.ui.api_client import api_client
from app.ui.components.probability_charts import render_ticket_inspection_card


def render_time_machine_view(session_id: str, thresholds: Dict[str, float]) -> None:
    """Renders the 9 pre-configured Time-Machine scenario cards and batch sweep runner."""
    st.markdown("### ⏱️ Time-Machine Scenario Injection Deck")
    st.caption(
        "Inject any of the **9 calibrated domain scenarios** using your active sidebar thresholds, or run all 9 "
        "in a single batch sweep to verify every circuit breaker and intent re-router."
    )

    engine_mode = st.session_state.get("engine_mode", "SIMULATED")

    # Handle quick-launch redirect from Landing Page
    pending_preset = st.session_state.pop("pending_preset_to_run", None)
    if pending_preset:
        tkt = api_client.trigger_preset(
            preset_id=pending_preset,
            session_id=session_id,
            engine_mode=engine_mode,
            thresholds=thresholds,
        )
        if tkt:
            st.session_state["last_simulated_ticket"] = tkt

    col_batch, col_info = st.columns([0.35, 0.65])
    with col_batch:
        if st.button(
            "⚡ Run All 9 Scenario Presets (Batch Sweep)",
            type="primary",
            use_container_width=True,
            key="run_all_9_presets_btn",
        ):
            batch_results = []
            for p in SCENARIO_PRESETS:
                tkt = api_client.trigger_preset(
                    preset_id=p.preset_id,
                    session_id=session_id,
                    engine_mode=engine_mode,
                    thresholds=thresholds,
                )
                if tkt:
                    st.session_state["last_simulated_ticket"] = tkt
                    dec = tkt.get("decision", {})
                    batch_results.append(
                        {
                            "Preset": p.title,
                            "Channel": tkt.get("channel"),
                            "Intent": dec.get("message_intent"),
                            "Trade": dec.get("assigned_trade") or "N/A",
                            "M3NHF SOR": dec.get("assigned_sor") or "Skipped",
                            "Auto-Approve": dec.get("auto_approve"),
                            "Media Purged": tkt.get("media_discarded"),
                            "Destination": dec.get("destination"),
                            "Gating Flags": ", ".join(dec.get("reasons", [])) or "NONE",
                        }
                    )
            st.session_state["last_batch_sweep_df"] = batch_results
            st.rerun()

    with col_info:
        st.caption(
            "💡 **Tip:** Try lowering `Min M3NHF SOR Confidence` to `0.50` and `Min Top-1 vs Top-2 Margin` to `0.05` "
            "in the sidebar, then click **Preset 2 (Ambiguous SOR Margin Trap)** to see how relaxing policy gates "
            "switches it from `SURVEYOR_DESK_REVIEW` to `AUTO_DISPATCH_HMS`."
        )

    if st.session_state.get("last_batch_sweep_df"):
        with st.expander("📊 Latest 9-Preset Batch Sweep Summary Table", expanded=True):
            st.dataframe(
                pd.DataFrame(st.session_state["last_batch_sweep_df"]),
                use_container_width=True,
                hide_index=True,
            )

    # Render 9 Scenario Cards in a 3x3 Grid
    for row_idx in range(0, len(SCENARIO_PRESETS), 3):
        cols = st.columns(3, gap="medium")
        for col_idx, preset in enumerate(SCENARIO_PRESETS[row_idx : row_idx + 3]):
            with cols[col_idx]:
                with st.container(border=True):
                    st.markdown(f"**{preset.title}**")
                    st.caption(f"Channel: `{preset.channel.value}` | Target Badge: `{preset.badge}`")
                    st.markdown(f"> _{preset.complaint_text}_")
                    st.caption(f"**What it tests:** {preset.what_it_tests}")
                    if st.button(
                        f"Inject Preset #{row_idx + col_idx + 1}",
                        key=f"inject_{preset.preset_id}",
                        use_container_width=True,
                    ):
                        tkt = api_client.trigger_preset(
                            preset_id=preset.preset_id,
                            session_id=session_id,
                            engine_mode=engine_mode,
                            thresholds=thresholds,
                        )
                        if tkt:
                            st.session_state["last_simulated_ticket"] = tkt
                            st.rerun()

    if st.session_state.get("last_simulated_ticket"):
        st.divider()
        st.markdown("### 🔬 Selected Preset Telemetry & Gating Breakdown")
        render_ticket_inspection_card(
            st.session_state["last_simulated_ticket"],
            key_prefix="time_machine_result",
        )
