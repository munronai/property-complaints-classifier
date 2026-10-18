"""Below-the-cards Help Guide, 4-Stage Rationale, and 9-Preset Walkthrough with MCP Agent Prompts."""

import pandas as pd
import streamlit as st

from app.ui.components.mermaid import st_mermaid


PRESET_MCP_PROMPTS = {
    "preset_clean_plumbing": (
        "Run simulate_complaint_event with preset_id='preset_clean_plumbing' and confirm which M3NHF SOR code was auto-dispatched."
    ),
    "preset_ambiguous_margin": (
        "Simulate 'preset_ambiguous_margin' and explain why the Top-1 vs Top-2 probability margin blocked auto-dispatch."
    ),
    "preset_awaabs_law_damp": (
        "Run 'preset_awaabs_law_damp' and check why Awaab's Law overrode standard contractor dispatch."
    ),
    "preset_emergency_water_electrics": (
        "Inject 'preset_emergency_water_electrics' and verify it routes to the 24-hour Out-of-Hours Duty Officer."
    ),
    "preset_whatsapp_photo_disambiguation": (
        "Simulate 'preset_whatsapp_photo_disambiguation' to see how the kitchen hinge photo disambiguates vague WhatsApp text."
    ),
    "preset_wip_scheduling_reroute": (
        "Run 'preset_wip_scheduling_reroute' and confirm Stage 2 SOR matching was skipped so no duplicate works order is raised."
    ),
    "preset_contractor_late_payment": (
        "Simulate 'preset_contractor_late_payment' and verify the invoice query routes to Contractor Finance Desk."
    ),
    "preset_completed_repair_complaint": (
        "Run 'preset_completed_repair_complaint' and tell me which M3NHF SOR code was scoped for the contractor recall."
    ),
    "preset_inappropriate_content_discard": (
        "Simulate 'preset_inappropriate_content_discard' and confirm the inappropriate image bytes were flagged and purged."
    ),
}


def render_help_and_presets_section(show_quick_launch: bool = False) -> None:
    """Renders the 4-stage workflow rationale, 9-preset guide, and custom testing recipes below the Option Cards."""
    st.divider()

    # 1. How the 4-Stage Workflow Works & Why Each Stage Exists
    st.markdown("## ⚙️ How the 4-Stage Triage Workflow Works (And Why Each Stage Matters)")
    st.markdown(
        "If you manage social housing or commercial property portfolios, you know that **sending the wrong tradesperson** "
        "or **missing a statutory damp alert** is expensive and dangerous. Here is why the pipeline is split into 4 explicit stages:"
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        with st.container(border=True):
            st.markdown("#### 1. Multi-Channel Intake & Photo Normalization")
            st.caption("Web Portal + WhatsApp + Pillow")
            st.write(
                "**What it does:** Ingests text and photos from Web Forms or WhatsApp, rotates sideways EXIF metadata upright, "
                "and scales images $\\le 1568\\text{px}$.\n\n"
                "**Why we built it:** Residents frequently send rotated, 12MP smartphone photos with 4-word captions (*'thing broken see pic'*)."
            )
    with c2:
        with st.container(border=True):
            st.markdown("#### 2. Jev Pass 1: Safety, Intent & Hazard Screen")
            st.caption("TypeSafe AI Jev (`Noul`, `Choice`, `Score`)")
            st.write(
                "**What it does:** Screens in one pass for (1) rude/inappropriate photos, (2) message intent (new repair vs. WIP update vs. "
                "completed-job complaint vs. contractor invoice), (3) Trade, (4) Awaab's Law damp, and (5) 24h Emergency SLA.\n\n"
                "**Why we built it:** UK Housing Ombudsman data shows **35%–45% of incoming messages are NOT new repairs**. Filtering them here prevents duplicate contractor callouts."
            )
    with c3:
        with st.container(border=True):
            st.markdown("#### 3. Jev Pass 2: Trade-Bounded M3NHF SOR")
            st.caption("Zero-Hallucination SOR Selection")
            st.write(
                "**What it does:** Narrows the M3NHF Schedule of Rates catalog strictly to the trade identified in Pass 1 and scores every "
                "candidate 6-digit SOR code.\n\n"
                "**Why we built it:** Feeding 500+ SOR codes into a standard LLM causes hallucinated codes. We also run Pass 2 on **completed-repair complaints** to scope contractor recalls."
            )
    with c4:
        with st.container(border=True):
            st.markdown("#### 4. Circuit-Breaker Gate (`TriageEscalationGuard`)")
            st.caption("Confidence, Margin & Statutory Guard")
            st.write(
                "**What it does:** Blocks auto-dispatch if Awaab's Law damp $\\ge 0.40$, SLA == 3, Trade confidence $< 0.70$, SOR confidence $< 0.65$, "
                "or the **Top-1 minus Top-2 SOR margin $< 0.15$**.\n\n"
                "**Why we built it:** If two plumbing codes (`192001` supply pipe vs `192005` waste trap) are nearly tied (54% vs 44%), a human surveyor must review before a contractor is dispatched."
            )

    mermaid_pipeline = """
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
    st_mermaid(mermaid_pipeline, height=390)

    with st.expander("📐 View Deep-Dive: How Live Jev Scales to 2,000+ SOR Codes (Two-Pass Architecture Diagram)", expanded=False):
        st.caption(
            "Pass 1 identifies the Trade Chapter from 7 trades. The local application queries the M3NHF catalog "
            "and injects only that trade's codes (~4 KB JSON) into Jev's Pass 2 choice criteria, avoiding context window bloat."
        )
        mermaid_scale = """
        flowchart TD
            subgraph Intake["Tenant Complaint Intake"]
                A["Tenant Message and Photo (e.g. Water leaking under kitchen sink)"]
            end

            subgraph Pass1["Pass 1: Live Jev Trade and Risk Screening"]
                B["TypeSafe Jev Screening Schema: Safety + Intent + Trade + Hazard + SLA"]
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

    st.divider()

    # 2. Guided 9-Preset Walkthrough Table
    st.markdown("## 🧪 Part 1: What the 9 Preset Scenarios Are For (Guided Walkthrough)")
    st.markdown(
        "In the **Live Sandbox Dashboard** (sidebar under `⚡ 1-Click Scenario Presets`) or in the **MCP Agent Console**, "
        "you can click any of these 9 presets to test a specific real-world property management scenario:"
    )

    walkthrough_rows = [
        {
            "Step / Preset Button": "1️⃣ Clean Plumbing Auto-Dispatch",
            "What Arrives (Channel)": "Web Portal: Toilet cistern ball valve stuck & overflowing + photo",
            "What Happens in the 4-Stage Pipeline": "Pass 1: PLUM (88%), Damp (4%), SLA 2. Pass 2: M3NHF 194010 (86%, margin 0.79).",
            "Property Management Proof Point": "✅ Auto-Dispatches M3NHF 194010 to HMS in <200ms with zero human effort.",
            "Example MCP Agent Prompt": PRESET_MCP_PROMPTS["preset_clean_plumbing"],
        },
        {
            "Step / Preset Button": "2️⃣ Ambiguous SOR Margin Trap",
            "What Arrives (Channel)": "Web Portal: Water pooling under kitchen sink (copper pipe vs plastic trap?)",
            "What Happens in the 4-Stage Pipeline": "Pass 1: PLUM (88%). Pass 2: Splits between 192001 (54%) and 192005 (44%) -> Margin = 0.10 (<0.15 cutoff).",
            "Property Management Proof Point": "⚠️ Catches physical ambiguity and holds for Surveyor Review instead of guessing the wrong part.",
            "Example MCP Agent Prompt": PRESET_MCP_PROMPTS["preset_ambiguous_margin"],
        },
        {
            "Step / Preset Button": "3️⃣ Awaab's Law Black Mould",
            "What Arrives (Channel)": "WhatsApp: Black mould spreading across child's bedroom window reveal + photo",
            "What Happens in the 4-Stage Pipeline": "Pass 1: DAMP (91%), Awaab's Law Hazard = 88% (>= 40% cutoff). Pass 2: 114001 (87%).",
            "Property Management Proof Point": "🚨 Statutory circuit breaker overrides auto-dispatch and routes to Disrepair / Legal Team.",
            "Example MCP Agent Prompt": PRESET_MCP_PROMPTS["preset_awaabs_law_damp"],
        },
        {
            "Step / Preset Button": "4️⃣ Emergency Water in Electrics",
            "What Arrives (Channel)": "WhatsApp: Water pouring through kitchen ceiling rose light fitting & sparking",
            "What Happens in the 4-Stage Pipeline": "Pass 1: ELEC (89%), SLA Priority = Level 3 (24-Hour Emergency). Pass 2: 211001 (91%).",
            "Property Management Proof Point": "⚡ Prevents life-safety emergencies from sitting in a routine contractor queue.",
            "Example MCP Agent Prompt": PRESET_MCP_PROMPTS["preset_emergency_water_electrics"],
        },
        {
            "Step / Preset Button": "5️⃣ WhatsApp Photo Disambiguation",
            "What Arrives (Channel)": "WhatsApp: Vague text ('metal thing snapped in kitchen see pic') + hinge photo",
            "What Happens in the 4-Stage Pipeline": "Visual tokens in the photo boost JOIN confidence from 62% -> 87% and select M3NHF 125011 (85%).",
            "Property Management Proof Point": "📷 Proves multimodal value: turns a vague 9-word WhatsApp message into an exact joinery SOR code.",
            "Example MCP Agent Prompt": PRESET_MCP_PROMPTS["preset_whatsapp_photo_disambiguation"],
        },
        {
            "Step / Preset Button": "6️⃣ WIP Update / Reschedule Re-Route",
            "What Arrives (Channel)": "WhatsApp: Chasing WIP repair JOB-88412 & asking to reschedule plasterer to Thu AM",
            "What Happens in the 4-Stage Pipeline": "Pass 1 detects CONTRACTOR_SCHEDULING / WIP update and short-circuits Stage 2 SOR matching.",
            "Property Management Proof Point": "↪️ Diverts to Customer Service WIP Desk — prevents raising a duplicate plastering order.",
            "Example MCP Agent Prompt": PRESET_MCP_PROMPTS["preset_wip_scheduling_reroute"],
        },
        {
            "Step / Preset Button": "7️⃣ Contractor Late Payment Re-Route",
            "What Arrives (Channel)": "Web Portal: Subcontractor chasing overdue Invoice INV-2026-091 for roof repair",
            "What Happens in the 4-Stage Pipeline": "Pass 1 detects CONTRACTOR_PAYMENT_INQUIRY and short-circuits Stage 2.",
            "Property Management Proof Point": "💳 Routes directly to Accounts Payable / Contractor Finance Desk instead of Roofing.",
            "Example MCP Agent Prompt": PRESET_MCP_PROMPTS["preset_contractor_late_payment"],
        },
        {
            "Step / Preset Button": "8️⃣ Completed-Job Workmanship Recall",
            "What Arrives (Channel)": "WhatsApp: Plumber closed JOB-77210 yesterday, but new sink waste pipe still leaks!",
            "What Happens in the 4-Stage Pipeline": "Pass 1 flags COMPLETED_REPAIR_COMPLAINT. Pass 2 STILL runs to scope M3NHF 192005 (84%).",
            "Property Management Proof Point": "🔍 Scopes the exact remedial SOR code (192005) and routes to Recall Review so landlord doesn't pay twice.",
            "Example MCP Agent Prompt": PRESET_MCP_PROMPTS["preset_completed_repair_complaint"],
        },
        {
            "Step / Preset Button": "9️⃣ Inappropriate Photo Safety Purge",
            "What Arrives (Channel)": "WhatsApp: Abusive message with rude/offensive photo attachment",
            "What Happens in the 4-Stage Pipeline": "Pass 1 flags inappropriate_content_flag (96%), skips Stage 2, and scrubs base64 image bytes.",
            "Property Management Proof Point": "🛑 Protects housing staff and storage compliance by purging offensive images on ingestion.",
            "Example MCP Agent Prompt": PRESET_MCP_PROMPTS["preset_inappropriate_content_discard"],
        },
    ]

    st.dataframe(pd.DataFrame(walkthrough_rows), use_container_width=True, hide_index=True)

    st.divider()

    # 3. Guide to Crafting Custom Complaints & Testing Thresholds
    st.markdown("## 🛠️ Part 2: Recipes for Testing Custom Inputs in the Sandbox")
    st.markdown(
        "Open the **Live Sandbox Dashboard**, expand `➕ Create Custom Complaint / WhatsApp Message` in the sidebar, "
        "and try these 4 recipes (or adjust the `🎚️ Jev Engine & Policy Sliders` to watch the circuit breakers react):"
    )

    g1, g2 = st.columns(2)
    with g1:
        with st.container(border=True):
            st.markdown("#### 🔍 Recipe A: Test a Completed Repair Job Recall")
            st.caption("Target Outcome: `QUALITY_RECALL_SURVEYOR_REVIEW` + Remedial M3NHF SOR Attached")
            st.markdown(
                "**How to test it:** Reference a job completed yesterday (`JOB-77210`) and describe poor workmanship.\n\n"
                "*Copy-Paste Example:*\n"
                "> `Your plumber came yesterday and marked JOB-77210 as completed, but the new push-fit waste trap under the kitchen sink is still leaking onto the floor.`"
            )
        with st.container(border=True):
            st.markdown("#### ↪️ Recipe B: Test a Work-in-Progress (WIP) or Scheduling Re-Route")
            st.caption("Target Outcome: `CUSTOMER_SERVICE_WIP_DESK` (Stage 2 Short-Circuited)")
            st.markdown(
                "**How to test it:** Ask when an operative is returning or request to move an appointment slot.\n\n"
                "*Copy-Paste Example:*\n"
                "> `Hi, chasing a status update on my work-in-progress plastering job JOB-88412. Can we reschedule the appointment slot to Thursday morning?`"
            )

    with g2:
        with st.container(border=True):
            st.markdown("#### 🎚️ Recipe C: Unlock an Ambiguous SOR Margin via Policy Sliders")
            st.caption("Target Gate: `Min M3NHF SOR Confidence` & `Min Top-1 vs Top-2 Margin`")
            st.markdown(
                "**How to test it:**\n"
                "1. Click preset **2️⃣ Ambiguous SOR Margin Trap** in the sidebar — notice it is blocked (`192001` @ 54% vs `192005` @ 44%, margin `0.10`).\n"
                "2. In the sidebar under `🎚️ Jev Engine & Policy Sliders`, lower **Min SOR Confidence** to `0.50` and **Min SOR Margin** to `0.05`, click **Save Engine Mode & Thresholds**, and inject Preset #2 again — watch it switch to **✅ AUTO_DISPATCH_HMS**!"
            )
        with st.container(border=True):
            st.markdown("#### 🛑 Recipe D: Trigger the Content Safety Media Purge")
            st.caption("Target Gate: `inappropriate_content_flag` (`media_discarded = True`)")
            st.markdown(
                "**How to test it:** Select `Simulated Inappropriate / Rude Photo Attachment` as the photo attachment in the sidebar (or click Preset **9️⃣ Inappropriate Photo Safety Purge**) to verify that Stage 1 halts processing and deletes the image bytes."
            )

    st.divider()

    # 4. Connecting & Testing from a Live WhatsApp Phone (Twilio Sandbox & Terminal)
    st.markdown("## 📱 Part 3: Testing from a Real WhatsApp Phone (Twilio Sandbox Guide)")
    st.markdown(
        "You can test this system directly from the **WhatsApp app on your personal smartphone** using the free **Twilio WhatsApp Sandbox**. "
        "When you text a message or photo from your phone, our backend receives the webhook, classifies the complaint, and texts you back an automated WhatsApp confirmation."
    )

    w1, w2 = st.columns([0.55, 0.45], gap="large")
    with w1:
        st.subheader("1. Quick Setup (3 Steps in ~5 Minutes)")
        st.markdown(
            """
            1. **Expose your local FastAPI server:**
               If running locally, start `ngrok http 8000` (or use your Modal HTTPS domain). Copy your public HTTPS URL (e.g. `https://xyz.ngrok-free.app`).
            2. **Join the Twilio WhatsApp Sandbox:**
               In your free [Twilio Console](https://console.twilio.com/) -> **Messaging** -> **Try it out** -> **Send a WhatsApp message**, send the join phrase (e.g. `join <two-words>`) to the Twilio number `+1 415 523 8886` from your personal phone.
            3. **Configure the Webhook URL in Twilio:**
               In the **Sandbox Settings** tab, set **"When a message comes in"** (HTTP POST) to:
            """
        )
        st.code(
            "https://<your-ngrok-or-modal-domain>/api/v1/webhooks/whatsapp/twilio?session=default",
            language="text",
        )
        st.caption(
            "Tip: Replace `session=default` with your custom session ID from the sidebar to route your phone's messages to your active dashboard view!"
        )

    with w2:
        st.subheader("2. How Property Targeting Works from WhatsApp")
        st.markdown(
            """
            - **Default Property:** Unknown phone numbers map to `Flat 4, Oak Court` (`prop_oak_01`).
            - **Targeting Specific Properties:** Add `#elm`, `#cedar`, or `#oak` anywhere in your WhatsApp message to direct the complaint to a specific tenancy!
            - **Instant WhatsApp Bot Replies:** Your phone receives an automated two-way response immediately:
              - *Routine Repair:* Shows M3NHF SOR code & SLA confirmation.
              - *Awaab's Law:* Shows statutory Environmental Health escalation notice.
              - *Emergency:* Shows 24h Out-of-Hours Duty Officer alert.
              - *WIP/Invoice:* Confirms link to existing job with 0 duplicate orders.
            """
        )

    with st.expander("💻 Don't have Twilio? Test the WhatsApp Webhook instantly via curl"):
        st.markdown("Run this in your terminal while watching your open Live Sandbox Dashboard update:")
        st.code(
            """curl -s -X POST 'http://127.0.0.1:8000/api/v1/webhooks/whatsapp' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "from_phone": "+447700900123",
    "property_id": "prop_oak_01",
    "session_id": "default",
    "message_body": "Hi, kitchen cupboard door hinge snapped off today, see photo attached.",
    "synthetic_image_preset": "broken_hinge"
  }' | python3 -m json.tool""",
            language="bash",
        )

