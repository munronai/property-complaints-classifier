"""Sandbox Tab 1: Live Multi-Channel Complaint Intake (Dashboard Web Portal & WhatsApp Business Simulator)."""

import base64
from typing import Any, Dict, Optional
import streamlit as st

from app.domain.presets import GOLDEN_PROPERTIES
from app.engine.image_normalizer import (
    SYNTHETIC_IMAGE_CATALOG,
    generate_synthetic_defect_image,
)
from app.ui.api_client import api_client
from app.ui.components.probability_charts import render_ticket_inspection_card


def render_live_intake_view(session_id: str, thresholds: Dict[str, float]) -> None:
    """Renders the interactive Dashboard UI and WhatsApp Business Webhook complaint composer."""
    st.markdown("### 📨 Multi-Channel Multimodal Complaint Intake")
    st.caption(
        "Test how the TypeSafe Jev engine and `TriageEscalationGuard` evaluate custom resident or contractor "
        "messages arriving via **Resident Web Portal** or **WhatsApp Business Webhook**."
    )

    col_form, col_preview = st.columns([0.58, 0.42], gap="large")

    with col_form:
        intake_channel = st.radio(
            "Select Source Intake Channel",
            options=["DASHBOARD_UI", "WHATSAPP"],
            format_func=lambda c: (
                "🖥️ Resident Web Portal (Dashboard UI)"
                if c == "DASHBOARD_UI"
                else "💬 WhatsApp Business Webhook (+44 7700 900123)"
            ),
            horizontal=True,
            key="live_intake_channel_radio",
        )

        prop_options = {
            pid: f"{p.name} ({p.portfolio_type.value})"
            for pid, p in GOLDEN_PROPERTIES.items()
        }
        selected_prop_id = st.selectbox(
            "Select Target Property / Tenancy",
            options=list(prop_options.keys()),
            format_func=lambda pid: prop_options[pid],
            key="live_intake_prop_select",
        )

        selected_prop = GOLDEN_PROPERTIES[selected_prop_id]
        st.caption(
            f"**Active WIP Jobs:** {', '.join(selected_prop.active_wip_jobs)}  \n"
            f"**Recently Completed Jobs:** {', '.join(selected_prop.completed_jobs)}"
        )

        default_text = (
            "Water is dripping from the push-fit waste trap under the kitchen sink onto the cupboard floor."
            if intake_channel == "DASHBOARD_UI"
            else "Your plumber came yesterday and closed JOB-77210 as completed, but the new push-fit waste pipe under the kitchen sink is still leaking! See pic."
        )
        complaint_text = st.text_area(
            "Resident or Contractor Message Text",
            value=default_text,
            height=115,
            key="live_intake_text_area",
        )

        existing_job_ref = st.text_input(
            "Optional Existing / Completed Job or Invoice Reference",
            value="JOB-77210" if intake_channel == "WHATSAPP" else "",
            placeholder="e.g., JOB-88412, JOB-77210, or INV-2026-091",
            key="live_intake_job_ref_input",
        )

        image_mode = st.radio(
            "Multimodal Photo Evidence",
            options=["SYNTHETIC_PRESET", "UPLOAD_FILE", "NONE"],
            format_func=lambda m: {
                "SYNTHETIC_PRESET": "🎨 Built-in Synthetic Defect Photo",
                "UPLOAD_FILE": "📷 Upload Custom Photo (JPEG/PNG)",
                "NONE": "📝 Text-Only (No Photo)",
            }[m],
            horizontal=True,
            key="live_intake_image_mode",
        )

        chosen_synthetic_preset: Optional[str] = None
        uploaded_b64: Optional[str] = None

        if image_mode == "SYNTHETIC_PRESET":
            preset_keys = list(SYNTHETIC_IMAGE_CATALOG.keys())
            chosen_synthetic_preset = st.selectbox(
                "Choose Synthetic Photo Attachment",
                options=preset_keys,
                index=1,  # sink_leak
                format_func=lambda k: SYNTHETIC_IMAGE_CATALOG[k],
                key="live_intake_synth_select",
            )
        elif image_mode == "UPLOAD_FILE":
            uploaded_file = st.file_uploader(
                "Upload Defect Photo (Automatically EXIF-transposed & scaled <=1568px)",
                type=["jpg", "jpeg", "png"],
                key="live_intake_file_uploader",
            )
            if uploaded_file is not None:
                uploaded_b64 = base64.b64encode(uploaded_file.read()).decode("utf-8")

        submit_btn = st.button(
            "Evaluate Complaint via TypeSafe Jev + M3NHF Gating →",
            type="primary",
            use_container_width=True,
            key="live_intake_submit_btn",
        )

    with col_preview:
        if intake_channel == "WHATSAPP":
            st.markdown("#### 📱 WhatsApp Business Webhook Preview")
            with st.container(border=True):
                st.markdown(
                    f"**From:** `+44 7700 900123` ({selected_prop.name})  \n"
                    f"**Webhook Endpoint:** `POST /api/v1/webhooks/whatsapp`"
                )
                st.success(f"💬 {complaint_text}")
                if chosen_synthetic_preset:
                    sample_bytes = generate_synthetic_defect_image(chosen_synthetic_preset)
                    st.image(
                        sample_bytes,
                        caption=f"WhatsApp Media Attachment: {SYNTHETIC_IMAGE_CATALOG[chosen_synthetic_preset]}",
                        use_container_width=True,
                    )
                elif uploaded_b64:
                    st.image(
                        base64.b64decode(uploaded_b64),
                        caption="Uploaded WhatsApp Media Attachment",
                        use_container_width=True,
                    )
        else:
            st.markdown("#### 🖥️ Web Portal Payload Preview")
            with st.container(border=True):
                st.markdown(
                    f"**Property:** `{selected_prop_id}` ({selected_prop.name})  \n"
                    f"**REST Endpoint:** `POST /api/v1/complaints/triage`"
                )
                if chosen_synthetic_preset:
                    sample_bytes = generate_synthetic_defect_image(chosen_synthetic_preset)
                    st.image(
                        sample_bytes,
                        caption=f"Attached Photo: {SYNTHETIC_IMAGE_CATALOG[chosen_synthetic_preset]}",
                        use_container_width=True,
                    )
                elif uploaded_b64:
                    st.image(
                        base64.b64decode(uploaded_b64),
                        caption="Uploaded Resident Photo",
                        use_container_width=True,
                    )
                else:
                    st.info("No photo attached — Stage 1 & Stage 2 will evaluate text tokens only.")

    if submit_btn:
        engine_mode = st.session_state.get("engine_mode", "SIMULATED")
        if intake_channel == "WHATSAPP":
            wa_payload: Dict[str, Any] = {
                "from_phone": "+447700900123",
                "property_id": selected_prop_id,
                "message_body": complaint_text,
                "media_base64": uploaded_b64,
                "synthetic_image_preset": chosen_synthetic_preset,
                "existing_job_ref": existing_job_ref.strip() or None,
                "session_id": session_id,
                "engine_mode": engine_mode,
                "thresholds": thresholds,
            }
            result_ticket = api_client.submit_whatsapp_webhook(wa_payload)
        else:
            rest_payload: Dict[str, Any] = {
                "complaint_text": complaint_text,
                "property_id": selected_prop_id,
                "channel": "DASHBOARD_UI",
                "engine_mode": engine_mode,
                "session_id": session_id,
                "image_base64": uploaded_b64,
                "synthetic_image_preset": chosen_synthetic_preset,
                "existing_job_ref": existing_job_ref.strip() or None,
                "thresholds": thresholds,
            }
            result_ticket = api_client.submit_complaint(rest_payload)

        if result_ticket:
            st.session_state["last_evaluated_ticket"] = result_ticket

    if st.session_state.get("last_evaluated_ticket"):
        st.divider()
        st.markdown("### 🔬 Latest Pipeline Assessment & Circuit-Breaker Result")
        render_ticket_inspection_card(
            st.session_state["last_evaluated_ticket"],
            key_prefix="live_intake_result",
        )
