"""Product Thinking, Domain Insights, and Architectural Decision Rationale view (Option Card 2)."""

from typing import Any
import pandas as pd
import streamlit as st

from app.ui.components.help_and_presets import render_help_and_presets_section
from app.ui.components.mermaid import st_mermaid


def render_product_insights_view(
    session_id: str,
    page_home: Any = None,
    page_dashboard: Any = None,
) -> None:
    """Renders the Product Thinking, Insights & Decisions showcase."""
    top_col1, top_col2 = st.columns([0.72, 0.28])
    with top_col1:
        st.markdown("# 📘 Product Thinking, Domain Insights & Architectural Decisions")
        st.caption(
            "Exposing the domain research, 4-stage workflow rationale, and gating mathematics behind the Complaint Classifier."
        )
    with top_col2:
        st.write("")
        if page_home is not None:
            st.page_link(
                page_home,
                label="← Back to Overview & Walkthrough",
                icon="🧭",
                use_container_width=True,
            )
        if page_dashboard is not None:
            st.page_link(
                page_dashboard,
                label="Open Live Sandbox Dashboard →",
                icon="🎛️",
                use_container_width=True,
            )

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "1. Why We Built This (Problem Framing)",
            "2. Visual 4-Stage Pipeline & Mermaid Diagrams",
            "3. Domain Data Insights (Ombudsman & Commercial)",
            "4. Two-Stage Jev vs. Raw LLM Chat",
        ]
    )

    with tab1:
        st.markdown("### Why Social Housing & Commercial Repairs Triage Needs a Calibrated Circuit Breaker")
        c1, c2, c3 = st.columns(3)
        with c1:
            with st.container(border=True):
                st.markdown("#### ❌ Wrong Trade & SOR Dispatch")
                st.markdown(
                    "Resident descriptions are often colloquial or vague (*'water under sink'* or *'thing snapped'*). "
                    "When call-handlers pick the wrong M3NHF SOR code (e.g., `192001` supply pipe vs. `192005` waste "
                    "trap, or sending a plasterer before a roof leak is fixed), contractors abort the visit—costing "
                    "**£65–£165 per wasted callout** and delaying tenant resolution."
                )
        with c2:
            with st.container(border=True):
                st.markdown("#### ⚖️ Statutory Awaab's Law Exposure")
                st.markdown(
                    "Under **Awaab's Law** and Section 11 of the Landlord and Tenant Act, damp and black mould "
                    "hazards carry strict statutory investigation and remediation timelines. An automated system "
                    "**must never** bury a damp/mould report inside a routine 28-day contractor queue—even if the "
                    "model's SOR confidence is 90%+."
                )
        with c3:
            with st.container(border=True):
                st.markdown("#### 🔁 Duplicate Orders & Double Billing")
                st.markdown(
                    "Tenants frequently message on WhatsApp to **chase a work-in-progress (WIP) repair** or "
                    "**complain that a completed repair job is still leaking**. Naive classifiers treat every incoming "
                    "message as a net-new repair, raising duplicate billable works orders or paying a contractor twice "
                    "for poor workmanship."
                )

        st.divider()
        st.markdown("### Key Product Decisions: Why Each Guardrail Exists")
        d1, d2, d3 = st.columns(3)
        with d1:
            with st.container(border=True):
                st.markdown("#### 1️⃣ Re-Routing WIP, Scheduling & Finance")
                st.markdown(
                    "- **Decision**: Classify `message_intent` in Pass 1 before running Pass 2 SOR matching.\n"
                    "- **Why**: If a resident asks *'When is the plasterer coming back to finish JOB-88412?'* or a "
                    "subcontractor chases *'Overdue Invoice INV-2026-091'*, running Stage 2 M3NHF SOR selection would "
                    "risk raising a duplicate works order.\n"
                    "- **Outcome**: Stage 3 is **short-circuited** and the ticket routes directly to "
                    "`CUSTOMER_SERVICE_WIP_DESK` or `CONTRACTOR_FINANCE_DESK`."
                )
        with d2:
            with st.container(border=True):
                st.markdown("#### 2️⃣ Assessing Completed Repair Complaints")
                st.markdown(
                    "- **Decision**: Treat `COMPLETED_REPAIR_COMPLAINT` as a first-class multimodal SOR assessment target.\n"
                    "- **Why**: When a resident sends a photo saying *'Your plumber closed JOB-77210 yesterday, but the new "
                    "push-fit trap is still leaking'*, the landlord needs to know **both** the exact remedial M3NHF SOR "
                    "scope (`PLUM -> 192005`) **and** that this is a defective workmanship recall.\n"
                    "- **Outcome**: Runs **both** Pass 1 & Pass 2 to attach the M3NHF SOR code, then routes to "
                    "`QUALITY_RECALL_SURVEYOR_REVIEW` (`is_completed_job_recall=True`)."
                )
        with d3:
            with st.container(border=True):
                st.markdown("#### 3️⃣ Content Safety: Flag & Purge Media")
                st.markdown(
                    "- **Decision**: Screen every upload in Pass 1 with `inappropriate_content_flag` (`noul`) and purge raw bytes on hit.\n"
                    "- **Why**: Public WhatsApp webhooks and web forms occasionally receive rude, explicit, or abusive images. "
                    "Persisting those bytes in databases or displaying them on surveyor screens creates legal and workplace safety issues.\n"
                    "- **Outcome**: Immediately halts Stage 3, sets `normalized_image_base64 = None` and `media_discarded = True`, "
                    "and logs `DISCARDED_INAPPROPRIATE_CONTENT`."
                )

    with tab2:
        st.markdown("### 1. 4-Stage Multimodal Triage & Circuit-Breaker Flowchart")
        st.caption(
            "Every complaint—whether submitted via Dashboard UI, WhatsApp Webhook, or AI Agent MCP Tool—flows through this deterministic 4-stage pipeline."
        )
        mermaid_arch = """
        flowchart LR
            subgraph S1["Stage 1: Intake and Photo Prep"]
                A["Dashboard / WhatsApp / MCP"] --> B["EXIF Transpose and Max 1568px JPEG"]
            end
            subgraph S2["Stage 2: TypeSafe Jev Pass 1"]
                B --> C["Safety (noul) + Intent + Trade + Hazard"]
            end
            subgraph S3["Stage 3: Bounded M3NHF SOR"]
                C -->|"Inappropriate ≥ 0.50"| P["Purge Image Bytes and Discard"]
                C -->|"WIP / Scheduling / Finance"| W["Short-Circuit to Admin Desk"]
                C -->|"New Repair OR Completed-Job Recall"| M["Pass 2: Bounded Trade SOR Catalog"]
            end
            subgraph S4["Stage 4: Circuit-Breaker Gate"]
                M --> G{"TriageEscalationGuard"}
                G -->|"Completed Job Recall"| R1["QUALITY_RECALL_SURVEYOR_REVIEW"]
                G -->|"Priority 3 Emergency"| R2["OUT_OF_HOURS_DUTY_OFFICER"]
                G -->|"Damp and Mould ≥ 0.40"| R3["DISREPAIR_LEGAL_TEAM"]
                G -->|"Low Conf or Margin ≤ 0.15"| R4["SURVEYOR_DESK_REVIEW"]
                G -->|"Calibrated and Safe"| R5["AUTO_DISPATCH_HMS"]
            end
        """
        st_mermaid(mermaid_arch, height=400)

        st.markdown("### 2. End-to-End Multimodal Triage & MCP Sequence Diagram")
        mermaid_seq = """
        sequenceDiagram
            autonumber
            actor Tenant as Resident / Commercial Tenant
            participant Intake as Stage 1: Photo Normalizer
            participant Jev as Stage 2 and 3: TypeSafe Jev Engine
            participant Guard as Stage 4: TriageEscalationGuard
            participant Store as Session-Isolated Store
            actor Surveyor as Surveyor / AI Agent (MCP)

            Tenant->>Intake: Submit Text + Smartphone Photo (Web or WhatsApp)
            Intake->>Intake: EXIF Transpose Upright + Scale ≤ 1568px
            Intake->>Jev: Pass 1 (Safety noul, Intent, Trade, Damp, Priority)
            alt Inappropriate Media (≥ 0.50)
                Jev-->>Guard: Halt Stage 3 + Purge Raw Image Bytes
            else WIP Update / Scheduling / Contractor Invoice
                Jev-->>Guard: Short-Circuit Stage 3 (Prevent Duplicate Order)
            else New Defect OR Completed-Job Quality Complaint
                Jev->>Jev: Pass 2 (Bounded Trade M3NHF 6-Digit SOR Choice)
                Jev-->>Guard: Top-1 and Top-2 SOR Probabilities
            end
            Guard->>Store: Persist Calibrated Decision and Audit Trail
            Surveyor->>Store: Inspect via Dashboard or MCP (sor://properties/{id}/latest-triage)
            Surveyor->>Store: Approve or Override M3NHF SOR Code
        """
        st_mermaid(mermaid_seq, height=480)

        st.markdown("### 3. Dynamic Bounded SOR Resolution & Jev Context Window Scaling")
        st.caption(
            "How TypeSafe Jev evaluates custom complaints without requiring prior training on 2,000+ SOR codes: "
            "Pass 1 identifies the Trade Chapter; the local system pulls only that trade's codes (~4 KB JSON); "
            "and Pass 2 injects them dynamically into Jev's `choice.criteria`."
        )
        mermaid_scale = """
        flowchart TD
            subgraph Intake["Tenant Complaint Intake"]
                A["Tenant Message and Photo (e.g. Water leaking under kitchen sink)"]
            end

            subgraph Pass1["Pass 1: Live Jev Trade and Risk Screening"]
                B["TypeSafe Jev Screening Schema: Safety (noul) + Intent (choice) + Trade (choice) + Hazard + SLA"]
                A --> B
                B --> C["Identified Trade: PLUM Plumbing (p = 88%)"]
            end

            subgraph Bounding["Local Application: Trade Bounding Lookup"]
                D[("Local M3NHF Catalog Database: 2,000+ codes across 30+ trades")]
                C -->|"get_candidate_sors_for_trade('PLUM')"| E["Bounded Candidate Set: Section 19 Plumbing (10 to 20 codes, ~4KB JSON, zero context bloat)"]
                D -.-> E
            end

            subgraph Pass2["Pass 2: Live Jev Dynamic Choice Evaluation"]
                E -->|"Dynamically inject as choice criteria"| F["TypeSafe Jev Pass 2 Schema: questions.selected_sor.criteria = candidate_sors"]
                A -.->|"Multimodal text and photo evidence"| F
                F --> G["Calibrated SOR Probability Distribution: 192001 (54%) vs 192005 (44%)"]
            end

            subgraph Guard["Stage 4: Circuit-Breaker Gating"]
                G --> H{"TriageEscalationGuard"}
                H -->|"Margin = 0.10 < 0.15 cutoff"| I["SURVEYOR_DESK_REVIEW: Held for human surveyor review"]
                H -->|"Margin >= 0.15 and Conf >= 0.65"| J["AUTO_DISPATCH_HMS: Direct Contractor Works Order"]
            end
        """
        st_mermaid(mermaid_scale, height=560)

    with tab3:
        st.markdown("### What Real-World Complaint Datasets Reveal")
        st.markdown(
            "Analysis of public **UK Housing Ombudsman Service** determinations and **First-tier Tribunal (Property Chamber)** "
            "commercial disputes shows that **35%–45% of incoming complaints are not standard responsive repairs**."
        )

        col_res, col_com = st.columns(2)
        with col_res:
            st.markdown("#### 🏠 Housing Association Breakdown (UK Housing Ombudsman)")
            df_ha = pd.DataFrame(
                [
                    {
                        "Category": "Property Condition & Responsive Repairs",
                        "Typical %": "55% – 65%",
                        "Core Triggers": "Damp/mould (Awaab's Law), roof/water leaks, winter heating, completed-job recalls, WIP no-shows",
                        "System Action": "Stage 2 + Stage 3 M3NHF SOR + Stage 4 Gating",
                    },
                    {
                        "Category": "Complaint Handling & Process Failures",
                        "Typical %": "15% – 20%",
                        "Core Triggers": "Breach of Complaint Handling Code timescales, Stage 1->2 delays, WIP status chasers",
                        "System Action": "Short-Circuit Stage 3 -> CUSTOMER_SERVICE_WIP_DESK",
                    },
                    {
                        "Category": "Anti-Social Behaviour (ASB) & Noise",
                        "Typical %": "8% – 12%",
                        "Core Triggers": "Domestic disturbance, communal harassment, acoustic insulation complaints",
                        "System Action": "Flagged OTHER -> Intercepted before trade dispatch",
                    },
                    {
                        "Category": "Estate Management & Communal Areas",
                        "Typical %": "5% – 8%",
                        "Core Triggers": "Security intercoms/doors (ELEC/JOIN), fly-tipping, lift outages, grounds",
                        "System Action": "Hardware -> ELEC/JOIN; Grounds/Lifts -> SURVEYOR_DESK_REVIEW",
                    },
                    {
                        "Category": "Service Charges, Rent & Finance Admin",
                        "Typical %": "3% – 5%",
                        "Core Triggers": "Service charge apportionment, billing errors, contractor late payment chasers",
                        "System Action": "Short-Circuit Stage 3 -> CONTRACTOR_FINANCE_DESK / Admin",
                    },
                ]
            )
            st.dataframe(df_ha, use_container_width=True, hide_index=True)

        with col_com:
            st.markdown("#### 🏢 Commercial Property Breakdown (Tribunal / RICS / BOMA)")
            df_com = pd.DataFrame(
                [
                    {
                        "Category": "Service Charge Transparency & CAM",
                        "Typical %": "35% – 40%",
                        "Core Triggers": "Excessive CAM charges, missing reconciliation, CapEx billed as repair",
                        "System Action": "Intercepted -> Commercial Leasehold Review",
                    },
                    {
                        "Category": "Facilities Management & Critical Plant",
                        "Typical %": "25% – 30%",
                        "Core Triggers": "Peak HVAC failure, goods lift downtime, roof leak threatening IT/stock",
                        "System Action": "ROOF/ELEC/PLUM + Priority 3 Emergency Escalation",
                    },
                    {
                        "Category": "Repair & Dilapidations Scope (s.146)",
                        "Typical %": "15% – 20%",
                        "Core Triggers": "FRI vs internal repairing covenant disputes, terminal dilapidations",
                        "System Action": "Ambiguous scope -> SURVEYOR_DESK_REVIEW",
                    },
                    {
                        "Category": "Building Access & Security Operations",
                        "Typical %": "8% – 12%",
                        "Core Triggers": "FOB/intercom faults, loading bay restrictions, scaffolding disruption",
                        "System Action": "Hardware -> ELEC/JOIN; Access ops -> Review",
                    },
                    {
                        "Category": "Sustainability & ESG Compliance",
                        "Typical %": "3% – 5%",
                        "Core Triggers": "Green tariff discrepancies, EPC upgrade disruption, EV charger faults",
                        "System Action": "EV hardware -> ELEC; Tariff -> Admin Review",
                    },
                ]
            )
            st.dataframe(df_com, use_container_width=True, hide_index=True)

    with tab4:
        st.markdown("### Why Two-Stage TypeSafe Jev + Margin Gating Beats Raw LLM Chat")
        st.markdown(
            r"""
            | Architectural Dimension | Raw Single-Pass Frontier LLM Chat | Two-Stage TypeSafe Jev + `TriageEscalationGuard` |
            | :--- | :--- | :--- |
            | **M3NHF SOR Hallucination Risk** | High — LLMs invent plausible-sounding 6-digit codes or mix trades when given 500+ SOR codes at once | **Zero** — Stage 2 identifies the primary trade; Stage 3 bounds Jev's `choice` criteria strictly to valid M3NHF codes for that trade |
            | **Ambiguity Detection** | Verbal confidence (*"I am 90% sure"*) is poorly calibrated | **Top-1 vs. Top-2 Margin Gate ($\text{Top}_1 - \text{Top}_2 \ge 0.15$)** catches cases where two SOR codes (`192001` @ 54% vs `192005` @ 44%) are nearly tied |
            | **Multimodal Image Handling** | Often requires separate OCR/vision pipelines | Native single-pass multimodal evaluation (`TypeSafe-Danger-Zone-Images: true`) with automatic EXIF transpose and $\le 1568\text{px}$ normalization |
            | **Statutory Circuit Breakers** | Soft prompt instructions can be bypassed | Deterministic Python `TriageEscalationGuard` acts as a hard circuit breaker for Awaab's Law ($\ge 0.40$) and Priority 3 Emergencies |
            """
        )

    render_help_and_presets_section(show_quick_launch=False)
