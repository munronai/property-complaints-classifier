"""4-Stage Visual Workflow Inspector showing What Happened and Why Each Stage Exists."""

import base64
from typing import Any, Dict
import pandas as pd
import streamlit as st

from app.domain.sor_catalog import get_sor_item


DESTINATION_STYLES: Dict[str, tuple[str, str, str]] = {
    "AUTO_DISPATCH_HMS": (
        "✅ AUTO-APPROVED → Direct Contractor Works Order (AUTO_DISPATCH_HMS)",
        "success",
        "All safety, intent, statutory, confidence, and probability margin gates passed. Dispatched directly to Housing Management System without human intervention.",
    ),
    "DISREPAIR_LEGAL_TEAM": (
        "🚨 STATUTORY ESCALATION → Awaab's Law Disrepair & Damp Team (DISREPAIR_LEGAL_TEAM)",
        "error",
        "Circuit breaker triggered: Awaab's Law damp/mould probability met or exceeded policy cutoff. Statutory inspection timeline initiated immediately.",
    ),
    "OUT_OF_HOURS_DUTY_OFFICER": (
        "⚡ 24-HOUR EMERGENCY → Out-of-Hours Duty Officer (OUT_OF_HOURS_DUTY_OFFICER)",
        "error",
        "Circuit breaker triggered: Repair Priority Level 3 (immediate safety/amenity hazard). Diverted to 24-hour emergency attendance.",
    ),
    "DISCARDED_INAPPROPRIATE_CONTENT": (
        "🛑 CONTENT SAFETY GATE → Inappropriate Photo Flagged & Bytes Purged (DISCARDED_INAPPROPRIATE_CONTENT)",
        "error",
        "Circuit breaker triggered: Stage 1 detected rude/explicit/abusive content. Raw image bytes were immediately scrubbed from memory and storage.",
    ),
    "QUALITY_RECALL_SURVEYOR_REVIEW": (
        "🔍 COMPLETED-JOB RECALL → Remedial SOR Scoped for Contractor Recall (QUALITY_RECALL_SURVEYOR_REVIEW)",
        "warning",
        "Complaint about a recently completed repair job: Stage 2 still scoped the remedial M3NHF SOR code, but routed to Surveyor Recall Review so the landlord does not pay the contractor twice.",
    ),
    "CUSTOMER_SERVICE_WIP_DESK": (
        "↪️ INTENT RE-ROUTE → Customer Service WIP & Scheduling Desk (CUSTOMER_SERVICE_WIP_DESK)",
        "info",
        "Message is requesting a status update or rescheduling an existing work-in-progress repair. Stage 2 SOR matching was skipped so zero duplicate works orders are raised.",
    ),
    "CONTRACTOR_FINANCE_DESK": (
        "💳 FINANCE RE-ROUTE → Accounts Payable / Contractor Finance Desk (CONTRACTOR_FINANCE_DESK)",
        "info",
        "Message is a subcontractor late-payment / invoice inquiry. Stage 2 SOR matching was skipped and routed to Finance.",
    ),
    "SURVEYOR_DESK_REVIEW": (
        "⚠️ HUMAN TRIAGE QUEUE → Repairs Surveyor Desk Review (SURVEYOR_DESK_REVIEW)",
        "warning",
        "Circuit breaker triggered: Low trade/SOR confidence or ambiguous margin (<0.15 gap between top two SOR codes). Held for quick Surveyor confirmation before raising works order.",
    ),
}


def render_ticket_inspection_card(ticket: Dict[str, Any], key_prefix: str = "insp") -> None:
    """Renders a 4-Stage step-by-step visual workflow explaining what happened and why each stage exists."""
    decision = ticket.get("decision", {})
    meta = decision.get("metadata", {})
    dest = decision.get("destination", "SURVEYOR_DESK_REVIEW")
    reasons = decision.get("reasons", [])

    headline, banner_kind, explanation = DESTINATION_STYLES.get(
        dest, (f"Routed to {dest}", "info", "")
    )

    # Top Outcome Banner
    if banner_kind == "success":
        st.success(f"### {headline}\n{explanation}")
    elif banner_kind == "error":
        st.error(f"### {headline}\n{explanation}")
    elif banner_kind == "warning":
        st.warning(f"### {headline}\n{explanation}")
    else:
        st.info(f"### {headline}\n{explanation}")

    st.markdown("#### 🔄 Step-by-Step Pipeline Walkthrough (What Happened & Why We Built Each Stage)")

    s1_col, s2_col, s3_col, s4_col = st.columns(4, gap="medium")

    # -----------------------------------------------------------------
    # STAGE 1: MULTIMODAL INTAKE & IMAGE NORMALIZATION
    # -----------------------------------------------------------------
    with s1_col:
        with st.container(border=True):
            st.markdown("##### 1️⃣ Stage 1: Intake & Photo Prep")
            chan = ticket.get("channel", "DASHBOARD_UI")
            tid = ticket.get("ticket_id", "")
            sor_assigned = decision.get("assigned_sor") or "Pending"
            if chan == "WHATSAPP":
                st.caption("📲 **Webhook:** `POST /api/v1/webhooks/whatsapp` (Mobile CRM Lookup + EXIF Fix)")
            elif chan == "MCP":
                st.caption("🤖 **Protocol:** `GET /mcp/sse` (`tools/call` JSON-RPC 2.0)")
            else:
                st.caption("🖥️ **Endpoint:** `POST /api/v1/complaints/triage` (Authenticated Web Portal)")

            st.markdown(
                f"- **Channel:** `{chan}`\n"
                f"- **Job/Inv Ref:** `{ticket.get('existing_job_ref') or 'None'}`"
            )
            st.markdown(f"> _{ticket.get('complaint_text')}_")

            if ticket.get("media_discarded"):
                st.error(
                    "🛑 **Photo Purged!**  \nRaw image bytes were deleted by the Stage 1 Safety Gate (`media_discarded=True`)."
                )
            elif ticket.get("normalized_image_base64"):
                try:
                    img_bytes = base64.b64decode(ticket["normalized_image_base64"])
                    tel = ticket.get("image_telemetry") or {}
                    st.image(
                        img_bytes,
                        caption=f"Normalized: {tel.get('normalized_width', 800)}x{tel.get('normalized_height', 600)}px RGB",
                        use_container_width=True,
                    )
                except Exception:
                    st.caption("Image attached & normalized.")
            else:
                st.caption("📝 Text-only message (no photo attached).")

            if chan == "WHATSAPP":
                if dest == "AUTO_DISPATCH_HMS":
                    wa_reply = f"✅ Repair booked (`{tid}`, M3NHF `{sor_assigned}`). A contractor will attend within the routine SLA."
                elif dest == "DISREPAIR_LEGAL_TEAM":
                    wa_reply = f"🚨 Damp/mould report (`{tid}`) logged under Awaab's Law. Our Environmental Health team is booking an urgent inspection."
                elif dest == "OUT_OF_HOURS_DUTY_OFFICER":
                    wa_reply = f"🚨 EMERGENCY (`{tid}`): Our 24h Out-of-Hours Duty Officer has been paged. Do not touch wet electrical switches."
                elif dest in ("CUSTOMER_SERVICE_WIP_DESK", "CONTRACTOR_FINANCE_DESK"):
                    wa_reply = f"📋 Update request (`{tid}`) linked to `{ticket.get('existing_job_ref') or 'your job'}` and routed to our admin desk."
                elif dest == "QUALITY_RECALL_SURVEYOR_REVIEW":
                    wa_reply = f"🔍 Sorry `{ticket.get('existing_job_ref') or 'your recent repair'}` is still faulty. Remedial SOR `{sor_assigned}` sent for Surveyor Recall."
                elif dest == "DISCARDED_INAPPROPRIATE_CONTENT":
                    wa_reply = f"🛑 Attachment violated acceptable use policy and was purged (`{tid}`)."
                else:
                    wa_reply = f"👷 Photo received (`{tid}`). A Technical Surveyor is confirming the exact part (`{sor_assigned}`) today."
                st.success(f"💬 **Auto-Reply to Tenant WhatsApp:**  \n_{wa_reply}_")
            else:
                st.info(
                    f"🖥️ **Web Portal Receipt:**  \nTicket `{tid}` logged synchronously → Status: `{ticket.get('status')}`"
                )

    # -----------------------------------------------------------------
    # STAGE 2: JEV PASS 1 (SAFETY, INTENT, TRADE, AWAAB'S LAW & SLA)
    # -----------------------------------------------------------------
    with s2_col:
        with st.container(border=True):
            st.markdown("##### 2️⃣ Stage 2: Jev Pass 1 Screening")
            st.caption(
                "💡 **Why:** 35%–45% of messages are WIP chasers or non-repairs, and damp/emergencies need instant flags."
            )
            inapp_p = float(meta.get("inappropriate_prob", 0.0))
            intent_val = decision.get("message_intent", "NEW_REPAIR_DEFECT")
            intent_p = float(meta.get("intent_prob", 0.0))
            trade_val = decision.get("assigned_trade") or "OTHER"
            trade_p = float(meta.get("trade_prob", 0.0))
            damp_p = float(meta.get("damp_prob", 0.0))
            prio_val = meta.get("priority_level", "1")

            st.markdown(
                f"- **Safety Check:** `{'🚨 FLAGGED' if inapp_p >= 0.5 else '✅ Clean'}` (`p={inapp_p:.0%}`)\n"
                f"- **Message Intent:** `{intent_val}` (`p={intent_p:.0%}`)\n"
                f"- **Primary Trade:** **`{trade_val}`** (`p={trade_p:.0%}`)\n"
                f"- **Awaab's Law Damp:** `{damp_p:.0%}`\n"
                f"- **SLA Priority:** `Level {prio_val}`"
            )
            if intent_val == "COMPLETED_REPAIR_COMPLAINT":
                st.warning(
                    "🔍 **Post-Repair Complaint:** Proceeding to Stage 3 so we scope the remedial SOR code for contractor recall."
                )
            elif intent_val in ("WIP_REPAIR_UPDATE", "CONTRACTOR_SCHEDULING", "CONTRACTOR_PAYMENT_INQUIRY"):
                st.info(
                    "↪️ **Non-New-Repair Intent:** Will short-circuit Stage 3 so no duplicate contractor order is raised."
                )

    # -----------------------------------------------------------------
    # STAGE 3: JEV PASS 2 (BOUNDED M3NHF SOR SELECTION & MARGIN)
    # -----------------------------------------------------------------
    with s3_col:
        with st.container(border=True):
            st.markdown("##### 3️⃣ Stage 3: Bounded M3NHF SOR")
            st.caption(
                "💡 **Why:** Bounding SOR choices to the Stage 2 trade prevents LLM code hallucinations."
            )
            s2 = ticket.get("stage2_output")
            if s2 and "answers" in s2 and "selected_sor" in s2["answers"]:
                sor_ans = s2["answers"]["selected_sor"]
                sor_code = decision.get("assigned_sor") or sor_ans.get("value")
                sor_p = float(meta.get("sor_prob", 0.0))
                margin = meta.get("sor_margin")
                sor_item = get_sor_item(sor_code)

                # Tooltip with item specification details
                sor_tooltip = (
                    f"M3NHF Specification ({sor_code}):\n\n"
                    f"{sor_item.full_specification}\n\n"
                    f"Base Rate: £{sor_item.base_rate_gbp:.2f} ({sor_item.unit_of_measure}) | "
                    f"Standard SLA: Level {sor_item.default_sla_priority} | Trade: {sor_item.trade.value}"
                    if sor_item
                    else f"M3NHF SOR Code: {sor_code}"
                )

                st.markdown(
                    f"- **Selected M3NHF Code:** **`{sor_code}`** ℹ️\n"
                    f"- **SOR Confidence:** `{sor_p:.0%}`\n"
                    + (f"- **Top-1 vs Top-2 Margin:** `{margin:.2f}`\n" if margin is not None else ""),
                    help=sor_tooltip,
                )

                if sor_item:
                    st.markdown(
                        f"**{sor_item.short_description}**",
                        help=sor_item.full_specification,
                    )
                    st.caption(
                        f"💰 **Rate:** £{sor_item.base_rate_gbp:.2f} ({sor_item.unit_of_measure}) | "
                        f"⏱️ **SLA:** Level {sor_item.default_sla_priority} | "
                        f"🔨 **Trade:** `{sor_item.trade.value}`"
                    )

                    with st.expander("📖 M3NHF Item Specification", expanded=False):
                        st.markdown(f"**Standard Specification:**  \n{sor_item.full_specification}")
                        st.markdown(
                            f"- **Code:** `{sor_item.sor_code}`\n"
                            f"- **Trade Chapter:** `{sor_item.trade.value}`\n"
                            f"- **Base Schedule Rate:** £{sor_item.base_rate_gbp:.2f} per {sor_item.unit_of_measure}\n"
                            f"- **Default SLA Priority:** Level {sor_item.default_sla_priority}\n\n"
                            f"💡 *Tip: See the '📚 M3NHF Schedule of Rates Catalog' tab below to view this code highlighted in the full schedule.*"
                        )
                elif decision.get("assigned_sor_description"):
                    st.caption(f"📋 *{decision.get('assigned_sor_description')}*")

                dist = sor_ans.get("distribution", {})
                if dist:
                    sorted_dist = sorted(dist.items(), key=lambda x: float(x[1]), reverse=True)
                    df_dist = pd.DataFrame(
                        [{"SOR": k, "Prob": float(v)} for k, v in sorted_dist]
                    )
                    st.bar_chart(df_dist.set_index("SOR"), height=140)

                    # If multiple candidates, show Top-1 vs Top-2 competitor breakdown
                    if len(sorted_dist) >= 2:
                        c1_code, c1_prob = sorted_dist[0]
                        c2_code, c2_prob = sorted_dist[1]
                        c1_it = get_sor_item(c1_code)
                        c2_it = get_sor_item(c2_code)
                        c1_label = c1_it.short_description if c1_it else c1_code
                        c2_label = c2_it.short_description if c2_it else c2_code

                        with st.expander(
                            "⚖️ Top-1 vs Top-2 Candidate Breakdown",
                            expanded=(margin is not None and margin < 0.15),
                        ):
                            st.markdown(
                                f"1. **`{c1_code}`** ({c1_prob:.0%}): {c1_label}\n"
                                f"2. **`{c2_code}`** ({c2_prob:.0%}): {c2_label}"
                            )
                            if margin is not None and margin < 0.15:
                                st.warning(
                                    f"⚠️ Margin gap `{margin:.2f}` < `0.15` threshold → Tripped AMBIGUOUS_SOR_MARGIN circuit breaker!"
                                )
            else:
                skip_reason = (
                    ticket.get("stage2_skipped_reason")
                    or "Stage 2 M3NHF SOR matching skipped."
                )
                st.info(f"⏭️ **Stage 3 Short-Circuited**  \n{skip_reason}")

    # -----------------------------------------------------------------
    # STAGE 4: CIRCUIT-BREAKER GATING & ROUTING DECISION
    # -----------------------------------------------------------------
    with s4_col:
        with st.container(border=True):
            st.markdown("##### 4️⃣ Stage 4: Circuit-Breaker Gate")
            st.caption(
                "💡 **Why:** Hard Python guardrails block low-confidence, narrow-margin, or statutory risk auto-dispatch."
            )
            st.markdown(
                f"- **Auto-Approve Order?** `{'✅ YES' if decision.get('auto_approve') else '🛑 NO (Intercepted)'}`\n"
                f"- **Final Route:** **`{dest}`**\n"
                f"- **Ticket Status:** `{ticket.get('status')}`"
            )
            if reasons:
                st.markdown("**Triggered Circuit Breakers:**")
                for r in reasons:
                    st.markdown(f"- `{r}`")
            else:
                st.success("✅ Passed all 6 circuit-breaker rules.")

            if ticket.get("surveyor_notes"):
                st.caption(f"👷 **Surveyor Note:** {ticket['surveyor_notes']}")
