"""Page 3: Unified Interactive Sandbox Dashboard (Sidebar Control Deck + 4-Stage Workflow + Audit Stream)."""

import base64
import re
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

from app.config import settings
from app.domain.presets import GOLDEN_PROPERTIES, SCENARIO_PRESETS
from app.domain.sor_catalog import M3NHF_SOR_CATALOG, get_sor_item
from app.engine.image_normalizer import (
    SYNTHETIC_IMAGE_CATALOG,
    generate_synthetic_defect_image,
)
from app.ui.api_client import api_client
from app.ui.components.kpi_header import render_error_banner, render_kpi_header
from app.ui.components.probability_charts import render_ticket_inspection_card


PRESET_SHORT_LABELS: Dict[str, str] = {
    "preset_clean_plumbing": "1️⃣ Clean Plumbing Auto-Dispatch (194010)",
    "preset_ambiguous_margin": "2️⃣ Ambiguous SOR Margin Trap (54% vs 44%)",
    "preset_awaabs_law_damp": "3️⃣ Awaab's Law Black Mould (Legal Override)",
    "preset_emergency_water_electrics": "4️⃣ Emergency Water in Light Fitting (24h OOH)",
    "preset_whatsapp_photo_disambiguation": "5️⃣ WhatsApp Photo Disambiguation (Hinge 125011)",
    "preset_wip_scheduling_reroute": "6️⃣ WIP Update / Reschedule Re-Route (Skip SOR)",
    "preset_contractor_late_payment": "7️⃣ Contractor Late Payment Re-Route (Finance)",
    "preset_completed_repair_complaint": "8️⃣ Completed-Job Workmanship Recall (192005)",
    "preset_inappropriate_content_discard": "9️⃣ Inappropriate Photo Safety Purge",
}


def render_sandbox_dashboard_page() -> None:
    """Renders the unified Live Sandbox Dashboard with sidebar controls, 4-stage walkthrough, and audit stream."""
    session_id = st.session_state.get("sandbox_session_id", "default")
    properties_list = api_client.get_properties(session_id=session_id)
    props_map: Dict[str, Dict[str, Any]] = {p["property_id"]: p for p in properties_list}

    default_prop_id = f"s_{session_id}_prop_oak_01"
    active_prop_id = st.session_state.get("active_property_id", default_prop_id)
    if active_prop_id not in props_map and props_map:
        active_prop_id = (
            default_prop_id if default_prop_id in props_map else next(iter(props_map.keys()))
        )
        st.session_state["active_property_id"] = active_prop_id

    active_prop = props_map.get(active_prop_id, GOLDEN_PROPERTIES["prop_oak_01"].model_dump())
    base_prop_id = active_prop_id.replace(f"s_{session_id}_", "")

    # Current engine mode & gating thresholds
    current_engine_mode = st.session_state.get("engine_mode", "SIMULATED")
    thresholds: Dict[str, float] = st.session_state.get(
        "active_thresholds",
        {
            "min_trade_confidence": settings.min_trade_confidence,
            "min_sor_confidence": settings.min_sor_confidence,
            "min_probability_margin": settings.min_probability_margin,
            "damp_hazard_threshold": settings.damp_hazard_threshold,
            "inappropriate_content_threshold": settings.inappropriate_content_threshold,
        },
    )

    # =====================================================================
    # SIDEBAR: WORKSPACE SESSION, PROPERTY SELECTOR, 9 PRESETS, CUSTOM BUILDER & SLIDERS
    # =====================================================================
    with st.sidebar:
        st.title("🎛️ Sandbox Control Deck")

        # 0. Multi-User Workspace Session Card
        with st.container(border=True):
            st.markdown(f"**👤 Session Workspace:** `{session_id}`")
            st.caption("All simulations, overrides, and resets are isolated to your workspace.")
            with st.expander("Switch or Name Workspace", expanded=False):
                custom_session = st.text_input(
                    "Workspace Key",
                    value=session_id,
                    max_chars=16,
                    help="Alphanumeric, dash, or underscore (e.g. 'alice', 'demo1').",
                    key="custom_session_input",
                )
                if st.button("Switch Workspace", use_container_width=True, key="btn_switch_ws"):
                    clean_s = re.sub(r"[^a-zA-Z0-9_-]", "", custom_session).strip().lower()[:16]
                    if clean_s and clean_s != session_id:
                        st.query_params["session"] = clean_s
                        st.session_state["sandbox_session_id"] = clean_s
                        st.session_state["active_property_id"] = f"s_{clean_s}_prop_oak_01"
                        st.session_state.pop("active_inspected_ticket", None)
                        st.session_state["last_ui_feedback"] = (
                            f"Switched isolated workspace to `?session={clean_s}` (`s_{clean_s}_*`)."
                        )
                        st.toast(f"Switched workspace to {clean_s}!", icon="👤")
                        st.rerun()

        # 1. Select Active Property / Tenancy
        prop_options = list(props_map.keys())

        def _format_prop_label(pid: str) -> str:
            info = props_map.get(pid, {})
            return f"🏘️ {info.get('name', pid)}"

        selected_pid = st.selectbox(
            "🏘️ Active Property / Tenancy",
            options=prop_options,
            index=prop_options.index(active_prop_id) if active_prop_id in prop_options else 0,
            format_func=_format_prop_label,
        )
        if selected_pid != active_prop_id:
            st.session_state["active_property_id"] = selected_pid
            st.session_state.pop("active_inspected_ticket", None)
            st.session_state["last_ui_feedback"] = (
                f"Switched active property to `{props_map[selected_pid]['name']}`."
            )
            st.toast(f"Selected {props_map[selected_pid]['name']}", icon="🏘️")
            st.rerun()

        st.divider()

        # 2. One-Click Scenario Presets (Expanded by default so cold users know immediately what to click!)
        st.subheader("⚡ 1. Test a Guided Scenario")
        with st.expander("🎯 9 One-Click Housing Presets", expanded=True):
            st.caption("Click any preset to inject it into the 4-stage pipeline and inspect the outcome:")
            for idx, preset in enumerate(SCENARIO_PRESETS):
                btn_label = PRESET_SHORT_LABELS.get(preset.preset_id, preset.title)
                is_primary = idx in (0, 1, 7, 8)
                if st.button(
                    btn_label,
                    key=f"sidebar_preset_{preset.preset_id}",
                    use_container_width=True,
                    type="primary" if is_primary else "secondary",
                    help=preset.what_it_tests,
                ):
                    with st.spinner(f"Running {preset.title} through Jev ({current_engine_mode})..."):
                        tkt = api_client.trigger_preset(
                            preset_id=preset.preset_id,
                            session_id=session_id,
                            engine_mode=current_engine_mode,
                            thresholds=thresholds,
                        )
                    if tkt:
                        st.session_state["active_inspected_ticket"] = tkt
                        dest = tkt.get("decision", {}).get("destination", "")
                        st.session_state["last_ui_feedback"] = (
                            f"✅ **Injected Preset:** *{preset.title}* → Routed to **`{dest}`** "
                            f"(Ticket `{tkt.get('ticket_id')}`)."
                        )
                        st.toast(f"Injected {btn_label} → {dest}", icon="⚡")
                        st.rerun()

        # 3. Custom Complaint / WhatsApp Message Builder
        with st.expander("➕ 2. Create Custom Complaint / WhatsApp", expanded=False):
            recipe_choice = st.selectbox(
                "Quick Template Recipe",
                [
                    "Custom / Freeform",
                    "Recipe A: Completed-Repair Job Recall (Plumber Trap Still Leaking)",
                    "Recipe B: WIP Status Update & Rescheduling Request",
                    "Recipe C: Ambiguous Under-Sink Leak (Pipe vs Waste Trap)",
                    "Recipe D: Awaab's Law Black Mould on Bedroom Reveal",
                ],
                key="sb_recipe_choice",
            )
            default_channel = "WHATSAPP"
            default_job_ref = ""
            default_img_preset = "sink_leak"

            if "Recipe A" in recipe_choice:
                default_text = (
                    "Your operative came yesterday and closed JOB-77210 as completed, but the new push-fit "
                    "waste pipe under the kitchen sink is still leaking onto the cupboard floor!"
                )
                default_job_ref = "JOB-77210"
                default_img_preset = "sink_leak"
            elif "Recipe B" in recipe_choice:
                default_text = (
                    "Hi, chasing an update on my work-in-progress plastering job JOB-88412. "
                    "Can we reschedule the appointment slot to Thursday morning?"
                )
                default_job_ref = "JOB-88412"
                default_img_preset = "NONE"
            elif "Recipe C" in recipe_choice:
                default_channel = "DASHBOARD_UI"
                default_text = (
                    "There is water pooling inside the kitchen base cupboard underneath the sink. "
                    "Not sure if it is coming from the copper supply pipe joint or the plastic waste trap."
                )
                default_img_preset = "sink_leak"
            elif "Recipe D" in recipe_choice:
                default_text = (
                    "Heavy black mould spreading across the child's bedroom window reveal and cold external wall."
                )
                default_img_preset = "black_mould"
            else:
                default_channel = "DASHBOARD_UI"
                default_text = (
                    "Water is dripping from the push-fit waste trap under the kitchen sink onto the cupboard floor."
                )
                default_img_preset = "sink_leak"

            custom_channel = st.radio(
                "Intake Channel",
                options=["DASHBOARD_UI", "WHATSAPP"],
                index=0 if default_channel == "DASHBOARD_UI" else 1,
                format_func=lambda c: "🖥️ Web Portal" if c == "DASHBOARD_UI" else "💬 WhatsApp Webhook",
                horizontal=True,
                key="sb_custom_channel",
            )
            if custom_channel == "WHATSAPP":
                st.success(
                    "💬 **WhatsApp Webhook Simulator (`POST /api/v1/webhooks/whatsapp`)**  \n"
                    "Simulates an unstructured WhatsApp message + camera photo arriving from a tenant's mobile phone."
                )
                wa_phone = st.text_input(
                    "Sender Mobile Number (CRM Lookup → Property)",
                    value="+447700900123",
                    key="sb_wa_phone",
                )
                custom_text = st.text_area(
                    "WhatsApp Message / Photo Caption",
                    value=default_text,
                    height=100,
                )
                custom_job_ref = st.text_input(
                    "Mentioned Job Ref (Optional)",
                    value=default_job_ref,
                )
            else:
                wa_phone = "+447700900123"
                st.info(
                    "🖥️ **Tenant Web Portal Form (`POST /api/v1/complaints/triage`)**  \n"
                    "Simulates an authenticated portal form submission with structured tenancy & job fields."
                )
                custom_job_ref = st.text_input(
                    "Existing / Completed Job or Invoice Ref (Optional)",
                    value=default_job_ref,
                )
                custom_text = st.text_area(
                    "Structured Defect / Complaint Description",
                    value=default_text,
                    height=100,
                )

            synth_options = ["NONE"] + list(SYNTHETIC_IMAGE_CATALOG.keys())
            custom_img_preset = st.selectbox(
                "Attach Synthetic Defect Photo",
                options=synth_options,
                index=synth_options.index(default_img_preset) if default_img_preset in synth_options else 0,
                format_func=lambda k: "📝 No Photo (Text Only)" if k == "NONE" else SYNTHETIC_IMAGE_CATALOG[k],
            )
            if custom_img_preset != "NONE":
                st.image(
                    generate_synthetic_defect_image(custom_img_preset),
                    caption=SYNTHETIC_IMAGE_CATALOG[custom_img_preset],
                    use_container_width=True,
                )

            uploaded_file = st.file_uploader(
                "Or Upload Custom JPEG/PNG Photo",
                type=["jpg", "jpeg", "png"],
                key="sb_custom_upload",
            )

            btn_cta = (
                "📲 Send Simulated WhatsApp Webhook"
                if custom_channel == "WHATSAPP"
                else "🖥️ Submit Web Portal Form"
            )
            if st.button(btn_cta, type="primary", use_container_width=True):
                uploaded_b64: Optional[str] = None
                if uploaded_file is not None:
                    uploaded_b64 = base64.b64encode(uploaded_file.read()).decode("utf-8")

                chosen_synth = None if (custom_img_preset == "NONE" or uploaded_b64) else custom_img_preset

                with st.spinner(f"Evaluating via {current_engine_mode} Jev Engine..."):
                    if custom_channel == "WHATSAPP":
                        res_tkt = api_client.submit_whatsapp_webhook(
                            {
                                "from_phone": wa_phone,
                                "property_id": base_prop_id,
                                "message_body": custom_text,
                                "media_base64": uploaded_b64,
                                "synthetic_image_preset": chosen_synth,
                                "existing_job_ref": custom_job_ref.strip() or None,
                                "session_id": session_id,
                                "engine_mode": current_engine_mode,
                                "thresholds": thresholds,
                            }
                        )
                    else:
                        res_tkt = api_client.submit_complaint(
                            {
                                "complaint_text": custom_text,
                                "property_id": base_prop_id,
                                "channel": "DASHBOARD_UI",
                                "engine_mode": current_engine_mode,
                                "session_id": session_id,
                                "image_base64": uploaded_b64,
                                "synthetic_image_preset": chosen_synth,
                                "existing_job_ref": custom_job_ref.strip() or None,
                                "thresholds": thresholds,
                            }
                        )
                if res_tkt:
                    st.session_state["active_inspected_ticket"] = res_tkt
                    dest = res_tkt.get("decision", {}).get("destination", "")
                    st.session_state["last_ui_feedback"] = (
                        f"✅ **Evaluated Custom {custom_channel} Message** → Routed to **`{dest}`** "
                        f"(Ticket `{res_tkt.get('ticket_id')}`)."
                    )
                    st.toast(f"Evaluated custom message → {dest}", icon="🚀")
                    st.rerun()

        st.divider()

        # 4. Jev Mode Toggle & Policy Threshold Sliders (with explicit UI feedback!)
        st.subheader("🎚️ 3. Jev Engine & Policy Sliders")
        with st.form("policy_thresholds_form"):
            new_engine_mode = st.radio(
                "🧠 Jev Evaluation Mode",
                options=["SIMULATED", "LIVE"],
                index=0 if current_engine_mode == "SIMULATED" else 1,
                format_func=lambda m: (
                    "🧪 Simulated Jev (Offline Calibrated)"
                    if m == "SIMULATED"
                    else "🟢 Live TypeSafe AI Jev API (TYPESAFE_API_KEY)"
                ),
                help="Switch between deterministic offline probabilities and live calls to api.typesafe.ai/v1/decide.",
            )
            new_trade_conf = st.slider(
                "Min Trade Confidence",
                0.40,
                0.95,
                float(thresholds["min_trade_confidence"]),
                0.05,
                help="Stage 1 trade confidence below this routes to Surveyor Review.",
            )
            new_sor_conf = st.slider(
                "Min M3NHF SOR Confidence",
                0.40,
                0.95,
                float(thresholds["min_sor_confidence"]),
                0.05,
                help="Stage 2 SOR confidence below this routes to Surveyor Review.",
            )
            new_margin = st.slider(
                "Min Top-1 vs Top-2 SOR Margin",
                0.05,
                0.50,
                float(thresholds["min_probability_margin"]),
                0.05,
                help="Minimum gap required between the #1 and #2 candidate SOR codes.",
            )
            new_damp = st.slider(
                "Awaab's Law Damp Hazard Cutoff",
                0.15,
                0.85,
                float(thresholds["damp_hazard_threshold"]),
                0.05,
                help="Damp/mould probability >= this value triggers statutory escalation to DISREPAIR_LEGAL_TEAM.",
            )

            if st.form_submit_button("Save Engine Mode & Thresholds", use_container_width=True):
                old_mode = current_engine_mode
                st.session_state["engine_mode"] = new_engine_mode
                st.session_state["active_thresholds"] = {
                    "min_trade_confidence": new_trade_conf,
                    "min_sor_confidence": new_sor_conf,
                    "min_probability_margin": new_margin,
                    "damp_hazard_threshold": new_damp,
                    "inappropriate_content_threshold": thresholds.get(
                        "inappropriate_content_threshold", 0.50
                    ),
                }
                mode_note = (
                    f"Switched Engine Mode `{old_mode}` → **`{new_engine_mode}`** | "
                    if old_mode != new_engine_mode
                    else f"Active Engine Mode: **`{new_engine_mode}`** | "
                )
                if new_engine_mode == "LIVE" and not settings.typesafe_api_key:
                    mode_note += (
                        "*(Note: `TYPESAFE_API_KEY` not set in environment; engine will safely use calibrated fallback)* | "
                    )
                st.session_state["last_ui_feedback"] = (
                    f"🎚️ **Policy Updated:** {mode_note}"
                    f"Trade $\\ge {new_trade_conf:.2f}$, SOR $\\ge {new_sor_conf:.2f}$, "
                    f"Margin $\\ge {new_margin:.2f}$, Awaab's Damp $\\ge {new_damp:.2f}$."
                )
                st.toast(f"Saved Engine Mode ({new_engine_mode}) & Thresholds!", icon="✅")
                st.rerun()

        st.divider()

        # 5. Workspace Reset & Protected System Admin Wipe
        if st.button("🔄 Reset My Workspace to Baseline", use_container_width=True):
            res = api_client.reset_workspace(session_id=session_id, reset_all=False)
            if res is not None:
                st.session_state.pop("active_inspected_ticket", None)
                st.session_state["last_ui_feedback"] = (
                    f"🔄 Reset your isolated workspace (`s_{session_id}_*`) back to the clean 3-ticket baseline."
                )
                st.toast("Workspace reset to baseline!", icon="🔄")
                st.rerun()

        with st.expander("⚙️ System Admin Reset (Protected)", expanded=False):
            st.caption("Requires `SANDBOX_ADMIN_KEY` (default: `sor-admin-secret-2026`).")
            sys_admin_key = st.text_input(
                "System Admin Key",
                type="password",
                placeholder="Enter admin key...",
                key="sys_admin_key_input",
            )
            if st.button("⚠️ Full System Wipe & Reset All", use_container_width=True):
                if not sys_admin_key.strip():
                    st.error("Admin secret key is required for a full system wipe.")
                else:
                    res = api_client.reset_workspace(
                        session_id=session_id,
                        reset_all=True,
                        admin_key=sys_admin_key.strip(),
                    )
                    if res is not None:
                        st.session_state.pop("active_inspected_ticket", None)
                        st.session_state["last_ui_feedback"] = (
                            "🧹 **Full System Wipe Completed:** All sessions and Golden Baseline reseeded."
                        )
                        st.toast("Full system wipe completed!", icon="🧹")
                        st.rerun()

    # =====================================================================
    # MAIN STAGE: FEEDBACK BANNER, PROPERTY HEADER & TELEMETRY KPI BAR
    # =====================================================================
    render_error_banner()

    if st.session_state.get("last_ui_feedback"):
        fb_col, close_col = st.columns([0.92, 0.08])
        with fb_col:
            st.info(st.session_state["last_ui_feedback"])
        with close_col:
            if st.button("✖️", key="dismiss_ui_fb", help="Dismiss notification"):
                st.session_state["last_ui_feedback"] = None
                st.rerun()

    active_mode_badge = (
        "🟢 LIVE TYPESAFE AI JEV API"
        if current_engine_mode == "LIVE"
        else "🧪 SIMULATED JEV ENGINE (CALIBRATED)"
    )

    head_col1, head_col2 = st.columns([0.72, 0.28])
    with head_col1:
        st.title(f"🏘️ {active_prop.get('name', 'Property Workspace')}")
        st.markdown(
            f"**Property ID:** `{active_prop_id}` | **Landlord:** `{active_prop.get('landlord_name', '')}` | "
            f"**Tenancy:** `{active_prop.get('tenant_Summary', '')}` | **Engine:** `{active_mode_badge}`"
        )
    with head_col2:
        st.metric(
            label="Active Gating Policy",
            value=f"Margin >= {thresholds['min_probability_margin']:.2f}",
            delta=f"SOR >= {thresholds['min_sor_confidence']:.0%} | Damp >= {thresholds['damp_hazard_threshold']:.0%}",
            delta_color="off",
        )

    render_kpi_header(session_id=session_id)
    st.divider()

    # Fetch tickets for the session
    all_tickets = api_client.get_tickets(session_id=session_id)
    prop_tickets_top = [
        t for t in all_tickets if t.get("property_id") in (active_prop_id, base_prop_id)
    ]
    active_ticket = st.session_state.get("active_inspected_ticket") or (
        prop_tickets_top[0] if prop_tickets_top else (all_tickets[0] if all_tickets else None)
    )

    # =====================================================================
    # SECTION 1: 4-STAGE VISUAL PIPELINE WALKTHROUGH (LATEST TICKET)
    # =====================================================================
    if active_ticket:
        tkt_id_str = str(active_ticket.get("ticket_id", ""))
        if tkt_id_str.startswith("TKT-BASE"):
            st.success(
                f"🟢 **Clean Baseline State (`{tkt_id_str}`)**: Each property starts with a nominal, low-risk routine repair "
                "that passes all 4 stages cleanly (**0 Awaab's Law hazards**, **0 Emergencies**, **100% Auto-Dispatched**).  \n"
                "👉 Use **⚡ 1. Test a Guided Scenario** in the left sidebar (for example, click **`3️⃣ Awaab's Law Black Mould`** "
                "or **`2️⃣ Ambiguous SOR Margin Trap`**) to inject a high-risk or ambiguous complaint and watch the circuit-breaker intercept it."
            )
        st.subheader(
            f"🔬 Active Complaint Walkthrough — Ticket `{tkt_id_str}`"
        )
        render_ticket_inspection_card(active_ticket, key_prefix="main_stage_walkthrough")

    # =====================================================================
    # SECTION 2: ACTIONABLE SURVEYOR REVIEW & RECALL QUEUE BANNER
    # =====================================================================
    pending_review_tickets = [
        t
        for t in all_tickets
        if t.get("status") in ("PENDING_SURVEYOR_REVIEW", "PENDING_RECALL_INSPECTION")
    ]
    if pending_review_tickets:
        st.divider()
        st.warning(
            f"🔔 **{len(pending_review_tickets)} Ticket(s) Held in Human Surveyor / Recall Queue!** "
            "These items were intercepted by `TriageEscalationGuard` (due to an ambiguous SOR margin, low confidence, "
            "or a completed-repair workmanship recall). Confirm or override the M3NHF SOR code below to dispatch:"
        )

        sor_choices = [
            f"{item.sor_code} ({trade.value}) — {item.short_description} (£{item.base_rate_gbp:.2f})"
            for trade, items in M3NHF_SOR_CATALOG.items()
            for item in items
        ]
        sor_code_map = {label: label.split(" ")[0] for label in sor_choices}

        for p_tkt in pending_review_tickets[:3]:
            tid = p_tkt["ticket_id"]
            dec = p_tkt.get("decision", {})
            cur_sor = dec.get("assigned_sor") or "192005"
            default_idx = next(
                (i for i, lbl in enumerate(sor_choices) if lbl.startswith(cur_sor)),
                0,
            )

            with st.container(border=True):
                q_c1, q_c2, q_c3 = st.columns([0.48, 0.34, 0.18])
                with q_c1:
                    recall_tag = "🔍 **[COMPLETED-JOB RECALL]** " if dec.get("is_completed_job_recall") else "⚠️ **[SURVEYOR REVIEW]** "
                    st.markdown(
                        f"{recall_tag}**`{tid}`** ({p_tkt.get('channel')})  \n"
                        f"_{p_tkt.get('complaint_text')}_  \n"
                        f"Flags: `{', '.join(dec.get('reasons', []))}` | Model Pick: **`{cur_sor}`** (`p={dec.get('metadata', {}).get('sor_prob', 0):.0%}`)"
                    )
                with q_c2:
                    chosen_label = st.selectbox(
                        "Confirm or Override M3NHF SOR Code",
                        options=sor_choices,
                        index=default_idx,
                        key=f"queue_sor_select_{tid}",
                    )
                with q_c3:
                    st.write("")
                    if st.button(
                        "⚡ Approve & Dispatch",
                        key=f"queue_approve_btn_{tid}",
                        type="primary",
                        use_container_width=True,
                    ):
                        chosen_code = sor_code_map[chosen_label]
                        updated = api_client.approve_or_override_ticket(
                            ticket_id=tid,
                            session_id=session_id,
                            override_sor=chosen_code,
                            surveyor_notes=f"Surveyor confirmed/overrode M3NHF SOR {chosen_code} from Sandbox Control Deck.",
                        )
                        if updated:
                            st.session_state["active_inspected_ticket"] = updated
                            st.session_state["last_ui_feedback"] = (
                                f"✅ **Surveyor Approved Ticket `{tid}`** with M3NHF SOR **`{chosen_code}`** → Dispatched to HMS!"
                            )
                            st.toast(f"Approved {tid} with SOR {chosen_code}!", icon="✅")
                            st.rerun()

    st.divider()

    # =====================================================================
    # SECTION 3: SPLIT WORKSPACE — PROPERTY DOSSIER & M3NHF CATALOG (LEFT) VS AUDIT STREAM (RIGHT)
    # =====================================================================
    left_pane, right_pane = st.columns([1.05, 1], gap="large")

    with left_pane:
        st.subheader("📋 Property Context & M3NHF SOR Catalog")
        tab_prop, tab_catalog = st.tabs(
            [
                "🏠 Active Property Jobs & Context",
                "📚 M3NHF Schedule of Rates Catalog",
            ]
        )
        with tab_prop:
            st.markdown(f"**Address:** {active_prop.get('address', '')}")
            st.markdown("##### 🚧 Open Work-in-Progress (WIP) Jobs on Property")
            st.caption(
                "When a resident messages about one of these open jobs, Stage 1 detects `WIP_REPAIR_UPDATE` "
                "or `CONTRACTOR_SCHEDULING` and diverts to Customer Service instead of raising a duplicate order."
            )
            for wip in active_prop.get("active_wip_jobs", []):
                st.info(f"🔧 {wip}")

            st.markdown("##### ✅ Recently Completed Repair Jobs on Property")
            st.caption(
                "When a resident complains that one of these completed jobs failed or was botched, Stage 1 flags "
                "`COMPLETED_REPAIR_COMPLAINT`, Stage 2 scopes the remedial M3NHF SOR code, and Stage 4 routes to Recall Review."
            )
            for comp in active_prop.get("completed_jobs", []):
                st.warning(f"📋 {comp}")

        with tab_catalog:
            st.caption(
                "Stage 2 bounds TypeSafe Jev strictly to the M3NHF codes matching the Stage 1 trade:"
            )

            # Determine selected SOR code from the active inspected ticket
            active_sor_code = None
            if active_ticket:
                active_dec = active_ticket.get("decision", {})
                active_sor_code = active_dec.get("assigned_sor")
                if not active_sor_code:
                    s2 = active_ticket.get("stage2_output")
                    if s2 and "answers" in s2 and "selected_sor" in s2["answers"]:
                        active_sor_code = s2["answers"]["selected_sor"].get("value")

            if active_sor_code:
                active_item = get_sor_item(active_sor_code)
                if active_item:
                    st.success(
                        f"👉 **Currently Selected for Active Ticket (`{active_ticket.get('ticket_id')}`):**  \n"
                        f"**Code `{active_item.sor_code}`** ({active_item.trade.value}) — {active_item.short_description}  \n"
                        f"_{active_item.full_specification}_  \n"
                        f"**Rate:** £{active_item.base_rate_gbp:.2f} ({active_item.unit_of_measure}) | **SLA:** Level {active_item.default_sla_priority}"
                    )
                else:
                    active_desc = (
                        active_dec.get("assigned_sor_description")
                        or "Dynamic / Specialist scope resolved via Live Jev or Surveyor Override"
                    )
                    active_trade = active_dec.get("assigned_trade") or "OTHER"
                    st.info(
                        f"👉 **Currently Selected for Active Ticket (`{active_ticket.get('ticket_id')}`):**  \n"
                        f"**Code `{active_sor_code}`** ({active_trade}) — {active_desc}  \n"
                        f"*(Dynamic / Out-of-Sample code added to table below)*"
                    )

            cat_rows = []
            for trade, items in M3NHF_SOR_CATALOG.items():
                for item in items:
                    is_active = (active_sor_code == item.sor_code)
                    cat_rows.append(
                        {
                            "Status": "👉 SELECTED" if is_active else "",
                            "M3NHF Code": item.sor_code,
                            "Trade": trade.value,
                            "Description": item.short_description,
                            "Rate": f"£{item.base_rate_gbp:.2f}",
                            "SLA": f"P{item.default_sla_priority}",
                            "Unit": item.unit_of_measure,
                        }
                    )

            # If active SOR code is not in the default catalog, dynamically append it so it's always visible
            if active_sor_code and active_sor_code not in [r["M3NHF Code"] for r in cat_rows]:
                cat_rows.append(
                    {
                        "Status": "👉 SELECTED (Dynamic)",
                        "M3NHF Code": active_sor_code,
                        "Trade": active_dec.get("assigned_trade") or "OTHER",
                        "Description": (
                            active_dec.get("assigned_sor_description")
                            or "Dynamic scope resolved via Live Jev or Surveyor Override"
                        ),
                        "Rate": "Custom / Surveyor Sourced",
                        "SLA": f"P{active_dec.get('metadata', {}).get('priority_level', '1')}",
                        "Unit": "IT",
                    }
                )

            # Float the selected SOR to the very top row so the user immediately sees it
            if active_sor_code:
                cat_rows.sort(key=lambda r: 0 if r["M3NHF Code"] == active_sor_code else 1)

            st.dataframe(pd.DataFrame(cat_rows), use_container_width=True, hide_index=True)

    with right_pane:
        st.subheader(f"🔬 Jev Gatekeeper Audit Stream ({len(all_tickets)} Tickets)")
        st.caption(
            "Every incoming message is logged with its Stage 1 intent, Stage 2 M3NHF SOR distribution, and circuit-breaker decision."
        )

        for tkt in all_tickets:
            tid = tkt["ticket_id"]
            dec = tkt.get("decision", {})
            meta = dec.get("metadata", {})
            dest = dec.get("destination", "")
            icon = {
                "AUTO_DISPATCH_HMS": "✅",
                "DISREPAIR_LEGAL_TEAM": "🚨",
                "OUT_OF_HOURS_DUTY_OFFICER": "⚡",
                "DISCARDED_INAPPROPRIATE_CONTENT": "🛑",
                "QUALITY_RECALL_SURVEYOR_REVIEW": "🔍",
                "CUSTOMER_SERVICE_WIP_DESK": "↪️",
                "CONTRACTOR_FINANCE_DESK": "💳",
                "SURVEYOR_DESK_REVIEW": "⚠️",
            }.get(dest, "ℹ️")

            sor_badge = dec.get("assigned_sor") or "No SOR (Skipped)"
            with st.expander(
                f"{icon} [{tid}] {dest} | Trade: {dec.get('assigned_trade') or 'N/A'} → SOR: {sor_badge}",
                expanded=(active_ticket and active_ticket.get("ticket_id") == tid),
            ):
                st.markdown(f"**Message ({tkt.get('channel')}):** {tkt.get('complaint_text')}")
                m1, m2, m3 = st.columns(3)
                m1.metric("Intent", dec.get("message_intent", "")[:14], f"p={meta.get('intent_prob', 0):.0%}")
                m2.metric("Trade / SOR", f"{dec.get('assigned_trade') or '-'} / {sor_badge}", f"p={meta.get('sor_prob', 0):.0%}")
                m3.metric("Damp / SLA", f"{meta.get('damp_prob', 0):.0%} Damp", f"Priority {meta.get('priority_level', '1')}")

                if st.button(
                    f"🔍 Load {tid} into 4-Stage Walkthrough Above",
                    key=f"load_walkthrough_{tid}",
                    use_container_width=True,
                ):
                    st.session_state["active_inspected_ticket"] = tkt
                    st.toast(f"Loaded {tid} into the 4-Stage Walkthrough!", icon="🔬")
                    st.rerun()
