"""Visual inspection component for Stage 1 & Stage 2 TypeSafe Jev probabilities, margins, and routing decisions."""

import base64
from typing import Any, Dict
import pandas as pd
import streamlit as st


DESTINATION_STYLES: Dict[str, tuple[str, str]] = {
    "AUTO_DISPATCH_HMS": ("✅ AUTO-APPROVED -> Direct Works Order (AUTO_DISPATCH_HMS)", "success"),
    "DISREPAIR_LEGAL_TEAM": ("🚨 STATUTORY ESCALATION -> Awaab's Law Legal / Disrepair Team (DISREPAIR_LEGAL_TEAM)", "error"),
    "OUT_OF_HOURS_DUTY_OFFICER": ("⚡ 24-HOUR EMERGENCY -> Out-of-Hours Duty Officer (OUT_OF_HOURS_DUTY_OFFICER)", "error"),
    "DISCARDED_INAPPROPRIATE_CONTENT": ("🛑 SAFETY GATE -> Inappropriate Media Flagged & Purged (DISCARDED_INAPPROPRIATE_CONTENT)", "error"),
    "QUALITY_RECALL_SURVEYOR_REVIEW": ("🔍 COMPLETED-JOB RECALL -> Remedial SOR Scoped for Contractor Recall (QUALITY_RECALL_SURVEYOR_REVIEW)", "warning"),
    "CUSTOMER_SERVICE_WIP_DESK": ("↪️ INTENT RE-ROUTE -> Customer Service WIP & Scheduling Desk (CUSTOMER_SERVICE_WIP_DESK)", "info"),
    "CONTRACTOR_FINANCE_DESK": ("💳 FINANCE RE-ROUTE -> Accounts Payable / Contractor Finance Desk (CONTRACTOR_FINANCE_DESK)", "info"),
    "SURVEYOR_DESK_REVIEW": ("⚠️ HUMAN TRIAGE QUEUE -> Repairs Surveyor Desk Review (SURVEYOR_DESK_REVIEW)", "warning"),
}


def render_ticket_inspection_card(ticket: Dict[str, Any], key_prefix: str = "insp") -> None:
    """Renders a complete visual breakdown of Pass 1, Pass 2 M3NHF probabilities, margin check, and routing outcome."""
    decision = ticket.get("decision", {})
    meta = decision.get("metadata", {})
    dest = decision.get("destination", "SURVEYOR_DESK_REVIEW")
    reasons = decision.get("reasons", [])

    banner_text, banner_kind = DESTINATION_STYLES.get(dest, (f"Routed to {dest}", "info"))
    if banner_kind == "success":
        st.success(f"**{banner_text}**  \nTicket ID: `{ticket.get('ticket_id')}` | Channel: `{ticket.get('channel')}` | Property: `{ticket.get('property_id')}`")
    elif banner_kind == "error":
        st.error(f"**{banner_text}**  \nTicket ID: `{ticket.get('ticket_id')}` | Channel: `{ticket.get('channel')}` | Property: `{ticket.get('property_id')}`")
    elif banner_kind == "warning":
        st.warning(f"**{banner_text}**  \nTicket ID: `{ticket.get('ticket_id')}` | Channel: `{ticket.get('channel')}` | Property: `{ticket.get('property_id')}`")
    else:
        st.info(f"**{banner_text}**  \nTicket ID: `{ticket.get('ticket_id')}` | Channel: `{ticket.get('channel')}` | Property: `{ticket.get('property_id')}`")

    if reasons:
        badges = " ".join([f"`{r}`" for r in reasons])
        st.markdown(f"**Triggered Gating / Re-Routing Flags:** {badges}")
    else:
        st.markdown("**Triggered Gating / Re-Routing Flags:** `NONE (All Confidence, Margin & Statutory Checks Passed)`")

    # Summary Metrics Row
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(
        "Stage 1 Intent",
        decision.get("message_intent", "NEW_REPAIR_DEFECT"),
        f"p={meta.get('intent_prob', 0.0):.2f}",
    )
    c2.metric(
        "Primary Trade",
        decision.get("assigned_trade") or "N/A",
        f"p={meta.get('trade_prob', 0.0):.2f}",
    )
    c3.metric(
        "M3NHF SOR Code",
        decision.get("assigned_sor") or "None (Skipped)",
        f"p={meta.get('sor_prob', 0.0):.2f}" if decision.get("assigned_sor") else "Short-Circuited",
    )
    sor_margin = meta.get("sor_margin")
    c4.metric(
        "Top-1 vs Top-2 Margin",
        f"{sor_margin:.2f}" if sor_margin is not None else "N/A",
        help="Difference between Top-1 and Top-2 M3NHF SOR candidate probabilities",
    )
    c5.metric(
        "Awaab's Law Damp Prob",
        f"{meta.get('damp_prob', 0.0):.0%}",
        f"SLA Priority {meta.get('priority_level', '1')}",
    )

    if decision.get("assigned_sor_description"):
        st.markdown(
            f"**Selected M3NHF SOR Specification (`{decision.get('assigned_sor')}`):** "
            f"{decision.get('assigned_sor_description')}"
        )

    col_left, col_right = st.columns([0.55, 0.45])

    with col_left:
        st.markdown("#### Pass 2: Trade-Bounded M3NHF Candidate Distribution")
        s2 = ticket.get("stage2_output")
        if s2 and "answers" in s2 and "selected_sor" in s2["answers"]:
            dist = s2["answers"]["selected_sor"].get("distribution", {})
            if dist:
                df_dist = pd.DataFrame(
                    [
                        {"M3NHF SOR Code": code, "Probability": float(prob)}
                        for code, prob in sorted(dist.items(), key=lambda x: x[1], reverse=True)
                    ]
                )
                st.bar_chart(df_dist.set_index("M3NHF SOR Code"), height=220)
                st.dataframe(df_dist, use_container_width=True, hide_index=True)
        else:
            skip_note = ticket.get("stage2_skipped_reason") or "Stage 2 M3NHF SOR matching was not executed."
            st.info(f"**Stage 2 Short-Circuited:** {skip_note}")

    with col_right:
        st.markdown("#### Multimodal Evidence & Image Normalization")
        if ticket.get("media_discarded"):
            st.error(
                "**🛑 RAW MEDIA BYTES PURGED BY CONTENT SAFETY GATE**  \n"
                "Stage 1 detected inappropriate/offensive visual content (`inappropriate_prob = "
                f"{meta.get('inappropriate_prob', 0.0):.2f}`). Raw base64 bytes were scrubbed from memory and "
                "blocked from entering persistent storage or surveyor queues."
            )
            if ticket.get("image_telemetry"):
                st.json(ticket["image_telemetry"])
        elif ticket.get("normalized_image_base64"):
            try:
                img_bytes = base64.b64decode(ticket["normalized_image_base64"])
                st.image(
                    img_bytes,
                    caption=(
                        f"Normalized Jev Asset ({ticket.get('image_telemetry', {}).get('normalized_width')}x"
                        f"{ticket.get('image_telemetry', {}).get('normalized_height')}px, RGB, EXIF Upright)"
                    ),
                    use_container_width=True,
                )
            except Exception:
                st.caption("Normalized image preview unavailable.")
            if ticket.get("image_telemetry"):
                with st.expander("View Pillow Normalization & Jev Asset Telemetry"):
                    st.json(ticket["image_telemetry"])
        else:
            st.caption("Text-only submission (no image attached).")

        with st.expander("View Raw Stage 1 & Stage 2 TypeSafe Jev JSON Payloads"):
            st.markdown("**Stage 1 Output (`triage_complaint`):**")
            st.json(ticket.get("stage1_output", {}))
            if ticket.get("stage2_output"):
                st.markdown("**Stage 2 Output (`resolve_sor_code`):**")
                st.json(ticket.get("stage2_output", {}))
