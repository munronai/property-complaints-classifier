"""Sandbox Tab 3: Repairs Surveyor Review Queue, Completed-Job Recall Inspector, and M3NHF Catalog Explorer."""

from typing import Any, Dict, List
import pandas as pd
import streamlit as st

from app.domain.sor_catalog import M3NHF_SOR_CATALOG
from app.ui.api_client import api_client
from app.ui.components.probability_charts import render_ticket_inspection_card


def render_surveyor_desk_view(session_id: str) -> None:
    """Renders the human-in-the-loop Surveyor Review Queue and full M3NHF Schedule of Rates Explorer."""
    st.markdown("### 👷 Repairs Surveyor Review Queue & M3NHF Schedule of Rates Explorer")
    st.caption(
        "Inspect tickets intercepted by `TriageEscalationGuard` (including **Completed-Job Workmanship Recalls**, "
        "**Ambiguous SOR Margins**, and **Awaab's Law** alerts), override or confirm their 6-digit M3NHF SOR code, "
        "and browse the complete trade-bounded M3NHF Schedule of Rates catalog."
    )

    tickets = api_client.get_tickets(session_id=session_id)

    subtab_queue, subtab_catalog = st.tabs(
        [
            f"📋 Session Triage & Recall Queue ({len(tickets)} Tickets)",
            "📚 M3NHF Schedule of Rates (SOR) Catalog Explorer",
        ]
    )

    with subtab_queue:
        if not tickets:
            st.info("No tickets in this session workspace yet. Submit a complaint or run a preset!")
            return

        filter_col1, filter_col2 = st.columns([0.45, 0.55])
        with filter_col1:
            dest_filter = st.selectbox(
                "Filter by Routing Destination",
                options=[
                    "ALL",
                    "SURVEYOR_DESK_REVIEW",
                    "QUALITY_RECALL_SURVEYOR_REVIEW",
                    "DISREPAIR_LEGAL_TEAM",
                    "OUT_OF_HOURS_DUTY_OFFICER",
                    "CUSTOMER_SERVICE_WIP_DESK",
                    "CONTRACTOR_FINANCE_DESK",
                    "DISCARDED_INAPPROPRIATE_CONTENT",
                    "AUTO_DISPATCH_HMS",
                ],
                key="surveyor_dest_filter",
            )

        filtered_tickets: List[Dict[str, Any]] = [
            t
            for t in tickets
            if dest_filter == "ALL"
            or t.get("decision", {}).get("destination") == dest_filter
        ]

        rows = []
        for t in filtered_tickets:
            dec = t.get("decision", {})
            meta = dec.get("metadata", {})
            rows.append(
                {
                    "Ticket ID": t.get("ticket_id"),
                    "Property": t.get("property_id"),
                    "Channel": t.get("channel"),
                    "Intent": dec.get("message_intent"),
                    "Trade": dec.get("assigned_trade") or "N/A",
                    "M3NHF SOR": dec.get("assigned_sor") or "None",
                    "SOR Margin": meta.get("sor_margin"),
                    "Recall?": "Yes" if dec.get("is_completed_job_recall") else "No",
                    "Media Purged?": "Yes" if t.get("media_discarded") else "No",
                    "Destination": dec.get("destination"),
                    "Status": t.get("status"),
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        if filtered_tickets:
            st.markdown("#### 🔧 Inspect & Override / Approve Selected Ticket")
            ticket_map = {
                t["ticket_id"]: (
                    f"{t['ticket_id']} | {t.get('decision', {}).get('destination')} | "
                    f"{t.get('complaint_text', '')[:65]}..."
                )
                for t in filtered_tickets
            }
            selected_tkt_id = st.selectbox(
                "Select Ticket to Inspect or Override",
                options=list(ticket_map.keys()),
                format_func=lambda tid: ticket_map[tid],
                key="surveyor_ticket_select",
            )
            selected_tkt = next(
                t for t in filtered_tickets if t["ticket_id"] == selected_tkt_id
            )

            all_sor_options = [""] + [
                item.sor_code
                for items in M3NHF_SOR_CATALOG.values()
                for item in items
            ]
            sor_label_map = {"": "Keep Current Assigned SOR"}
            for items in M3NHF_SOR_CATALOG.values():
                for item in items:
                    sor_label_map[item.sor_code] = (
                        f"{item.sor_code} ({item.trade.value}) — {item.short_description} (£{item.base_rate_gbp:.2f})"
                    )

            act_col1, act_col2, act_col3 = st.columns([0.45, 0.35, 0.20])
            with act_col1:
                override_sor = st.selectbox(
                    "Override or Confirm M3NHF SOR Code",
                    options=all_sor_options,
                    format_func=lambda code: sor_label_map.get(code, code),
                    key="surveyor_override_sor_select",
                )
            with act_col2:
                surveyor_notes = st.text_input(
                    "Surveyor Audit / Recall Note",
                    value=selected_tkt.get("surveyor_notes") or "Verified defect scope; approved for HMS dispatch.",
                    key="surveyor_notes_input",
                )
            with act_col3:
                st.write("")
                if st.button(
                    "Approve / Override →",
                    type="primary",
                    use_container_width=True,
                    key="surveyor_approve_btn",
                ):
                    updated = api_client.approve_or_override_ticket(
                        ticket_id=selected_tkt_id,
                        session_id=session_id,
                        override_sor=override_sor or None,
                        surveyor_notes=surveyor_notes,
                    )
                    if updated:
                        st.success(f"Ticket `{selected_tkt_id}` updated (`{updated.get('status')}`).")
                        st.rerun()

            render_ticket_inspection_card(selected_tkt, key_prefix="surveyor_insp")

    with subtab_catalog:
        st.markdown("#### Complete M3NHF Schedule of Rates Registry (Bounded Candidate Sets)")
        cat_rows = []
        for trade, items in M3NHF_SOR_CATALOG.items():
            for item in items:
                cat_rows.append(
                    {
                        "M3NHF SOR Code": item.sor_code,
                        "Trade": trade.value,
                        "Short Description": item.short_description,
                        "Unit": item.unit_of_measure,
                        "Base Rate (£)": f"£{item.base_rate_gbp:.2f}",
                        "Default SLA": f"Priority {item.default_sla_priority}",
                        "Full M3NHF Specification": item.full_specification,
                    }
                )
        st.dataframe(pd.DataFrame(cat_rows), use_container_width=True, hide_index=True)
