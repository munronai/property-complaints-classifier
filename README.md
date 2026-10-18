# Social Housing & Property Complaint Classifier Sandbox

A **Sandbox & Prototype Platform** (Typed FastAPI REST API + Mounted FastMCP Agent Server + Modular Streamlit Control Deck) that assesses multi-channel resident and commercial property complaints (text + multimodal photos via **Web Dashboard** and **WhatsApp Business Webhooks**) using **TypeSafe Jev** and **M3NHF Schedule of Rates (SOR) codes**, wrapped in **Hard Statutory & Confidence Gating Middleware (`TriageEscalationGuard`)**.

---

## Key Capabilities & User Interface Architecture

The platform provides an intuitive, surveyor-grade UI designed for both technical evaluators and housing maintenance operations:

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                STREAMLIT CONTROL DECK                                    │
│                                                                                          │
│ ┌──────────────────────┐  ┌────────────────────────────────────────────────────────────┐ │
│ │ SIDEBAR CONTROL DECK │  │ 1. REAL-TIME KPI HEADER                                    │ │
│ │                      │  │ Total Tickets | Auto-Approved % | Median Margin | Mode     │ │
│ │ • Session Switcher   │  ├────────────────────────────────────────────────────────────┤ │
│ │ • Engine Mode Toggle │  │ 2. 4-STAGE PIPELINE WALKTHROUGH (WHAT HAPPENED & WHY)      │ │
│ │   (SIMULATED vs LIVE)│  │ [Stage 1: Intake] [Stage 2: Pass 1] [Stage 3] [Stage 4]   │ │
│ │ • 9 Scenario Presets │  ├────────────────────────────────────────────────────────────┤ │
│ │ • Custom Complaint   │  │ 3. SURVEYOR & RECALL QUEUE (Confirm or Override SOR)       │ │
│ │   (Web & WhatsApp)   │  ├─────────────────────────────┬──────────────────────────────┤ │
│ │ • Policy Sliders     │  │ 4. PROPERTY & M3NHF CATALOG │ 5. JEV GATEKEEPER AUDIT      │ │
│ │ • Reset Workspace    │  │ Active Job Context & SOR    │ Stream of Session Tickets    │ │
│ └──────────────────────┘  └─────────────────────────────┴──────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Prototype Landing Page (`/`)
- **Direct Navigation Cards**: Quick links to the **Live Sandbox Dashboard**, **Product Thinking & Mermaid Diagrams**, and **MCP Agent Console**.
- **Streamlined Layout**: Removed duplicate stats from the landing page—focusing attention on the problem statement and workflow entry points.
- **Below-the-Fold Reference Guide**:
  - Full walkthrough table explaining what each of the **9 Time-Machine Presets** demonstrates.
  - Copy-paste prompts showing how an AI agent uses MCP tools/resources for each scenario.
  - Step-by-step guide for testing from a real smartphone via the **Twilio WhatsApp Sandbox**.

### 2. Live Interactive Sandbox Dashboard (`/sandbox`)
- **Sidebar Control Deck**:
  - **Multi-User Session Isolation**: Isolate experiments per browser session or URL query parameter (`?session=abc123`).
  - **Live Jev Toggle with Instant Feedback**: Switch between `SIMULATED` and `LIVE` TypeSafe AI Jev in one click with instant status badges and toast feedback.
  - **9 Time-Machine Scenario Presets**: 1-click injection of real-world edge cases (clean plumbing, ambiguous margins, Awaab's Law black mould, emergency electrical leaks, vague WhatsApp photos, WIP chasers, contractor invoices, completed-repair workmanship recalls, and inappropriate photos).
  - **Custom Complaint Builder**: Test custom complaints through authenticated **Web Portal** or **WhatsApp Webhook** (with sender phone CRM lookup and synthetic defect photo attachments).
  - **Dynamic Policy Threshold Sliders**: Adjust Min Trade Confidence, Min SOR Confidence, Min Top-1 vs Top-2 Margin, and Content Safety thresholds in real time to observe circuit-breaker gating behavior.
  - **Refresh SOR Codes from Phase 4 Feed**: Select any repair trade (`PLUM`, `DAMP`, `ROOF`, `JOIN`, `ELEC`, `PLAS`, or `ALL`) and import up to **20 authentic M3NHF v8 codes** per trade (up to **120 codes** total) into the active catalog so custom complaints across trades resolve to specific SOR codes without falling back to `OTHER`.
  - **Reset to Baseline & Sys Admin Reset**: Both **"🔄 Reset My Workspace to Baseline"** and **"⚙️ System Admin Reset"** restore the workspace tickets/properties **and** reset the active M3NHF Schedule of Rates back to the **18-code Base Set**.
- **Top KPI Header**: Live telemetry showing total tickets, auto-approval percentage, surveyor review rate, median probability margin, and active session ID.
- **4-Stage Visual Workflow Inspector**:
  - **Stage 1 (Intake & Photo Prep)**: Displays intake channel (`WHATSAPP`, `DASHBOARD_UI`, `MCP`), job/invoice reference, normalized image preview, photo purge alerts, and automated WhatsApp replies sent to the resident.
  - **Stage 2 (TypeSafe Jev Pass 1 Screening)**: Evaluates Content Safety (`noul`), Message Intent (`choice`), Primary Trade Chapter (`choice`), Awaab's Law Damp Risk (`noul`), and Repair Priority SLA Level (`score`). Non-repair intents (WIP, scheduling, finance) are immediately short-circuited here.
  - **Stage 3 (Bounded M3NHF SOR Selection & Margin)**:
    - Displays selected 6-digit M3NHF SOR code and confidence score.
    - **Native Hover Tooltip (`help=...`)**: Instant surveyor hover card with the full technical specification, base schedule rate, unit of measure, and trade chapter.
    - **Specification Expander (`📖 M3NHF Item Specification`)**: Detailed specification, schedule rate, and default SLA priority.
    - **Probability Distribution Bar Chart**: Visual breakdown across candidate codes.
    - **Top-1 vs. Top-2 Competitor Expander**: Compares competing codes side-by-side; automatically expands if the margin is below the `0.15` threshold.
  - **Stage 4 (Circuit-Breaker Gate & Routing Decision)**: Clear badge showing whether the works order was auto-approved or intercepted by `TriageEscalationGuard`, listing all triggered circuit breakers.
- **Surveyor & Recall Review Queue**:
  - Pauses tickets with low confidence, ambiguous margins, or workmanship recalls.
  - Allows repairs surveyors to review photo evidence, select/override the M3NHF SOR code, and approve direct HMS contractor dispatch.
- **Property Context & M3NHF Catalog Tab (Left Pane)**:
  - **Active Property Context**: Displays open WIP jobs and recently completed repairs to prevent duplicate orders and catch workmanship recalls.
  - **M3NHF Schedule of Rates Catalog**:
    - Inline **Phase 4 Trade Feed Importer** to expand any trade up to 20 M3NHF SOR codes or reset back to the 18-code Base Set.
    - Highlights the active inspected ticket's SOR code in an alert banner.
    - Marks the selected code with `Status: 👉 SELECTED` and **automatically floats it to row #1**.
    - **Dynamic Expansion**: Any custom code selected by Live Jev or entered via surveyor override is dynamically added to the table.
- **Jev Gatekeeper Audit Stream (Right Pane)**:
  - Chronological audit cards for all session tickets with Intent, Trade/SOR, and Damp/SLA metrics.
  - Single-click **"Load into 4-Stage Walkthrough"** button to inspect any past ticket in the visual pipeline.

### 3. Product Thinking, Insights & Mermaid Diagrams (`/insights`)
- **Tab 1: Problem Framing**: Why responsive repairs triage requires hard statutory circuit breakers (Awaab's Law, £65–£165 wasted callout costs, duplicate order prevention).
- **Tab 2: Visual Mermaid Diagrams**:
  1. *4-Stage Guardrailed Triage Architecture* (Flowchart).
  2. *End-to-End Multimodal Triage & MCP Sequence Diagram* (Sequence).
  3. *Dynamic Bounded SOR Resolution & Jev Context Window Scaling* (Flowchart illustrating how Pass 1 bounds Pass 2 criteria to eliminate context bloat and prevent hallucinations).
- **Tab 3: Ombudsman & Commercial Data Insights**: Real-world distribution data from the UK Housing Ombudsman Service and Property Chamber tribunals.
- **Tab 4: Two-Stage Jev vs. Raw LLM Chat**: Architectural comparison detailing why bounded schema evaluation outperforms unconstrained prompt engineering.

### 4. Embedded FastMCP Agent Console & Developer Guides (`/mcp`)
- **Embedded MCP Tool Runner**: Interactive form to run and inspect all 4 FastMCP primitives directly in the browser:
  - Read Tool: `get_latest_triage`
  - Intake Tool: `submit_complaint_triage`
  - Simulation Tool: `simulate_complaint_event`
  - Actuator Tool: `approve_or_override_work_order`
- **MCP Agent Prompts**: Curated prompts for Claude Desktop, Cursor, and Gemini to demonstrate how autonomous agents query resources and invoke triage tools.

---

## M3NHF Schedule of Rates Trade Chapter Standard

All SOR codes in the platform match real-world UK social housing M3NHF Schedule of Rates section chapters:

| Section | Trade Chapter | Example Codes & Standard Scope |
| :--- | :--- | :--- |
| **Section 19** | **Plumbing (PLUM)** | `192005` (Kitchen sink waste trap), `192001` (Internal supply pipe repair <=22mm), `194010` (WC cistern ball valve overhaul), `195020` (Emergency burst pipe isolate) |
| **Section 11** | **Damp Proofing (DAMP)** | `114001` (Awaab's Law fungicidal wash), `114010` (Humidistat extract fan), `112005` (Chemical DPC injection), `112015` (External brickwork repointing) |
| **Section 10** | **Roofing (ROOF)** | `101004` (Interlocking concrete tiles), `105012` (Rainwater gutter & downpipe clearance) |
| **Section 12** | **Joinery (JOIN)** | `125011` (Kitchen cupboard door & hinges), `121008` (Internal fire door ease), `123020` (Staircase handrail) |
| **Section 16** | **Plastering (PLAS)** | `161002` (Blown wall plaster skim), `162008` (Water-damaged ceiling overboard & skim) |
| **Section 21** | **Electrical (ELEC)** | `211001` (Emergency make safe water in ceiling rose), `212015` (13A twin socket), `214002` (Optical smoke alarm) |

---

## Configuration & Secrets Management

The platform supports running in **SIMULATED mode** out of the box with zero external API keys. When connecting to live TypeSafe AI Jev, securing administrative endpoints, or enabling live WhatsApp phone testing via Twilio, configure the secrets below.

### Secret Variables Reference

| Variable | Description | Required? | Default / Example |
| :--- | :--- | :--- | :--- |
| `TYPESAFE_API_KEY` | TypeSafe AI API Key for live Jev classification | No (falls back to `SIMULATED`) | `ts_live_...` |
| `TYPESAFE_API_URL` | TypeSafe decision endpoint | No | `https://api.typesafe.ai/v1/decide` |
| `DEFAULT_ENGINE_MODE` | Default engine mode | No | `SIMULATED` (or `LIVE`) |
| `SANDBOX_ADMIN_KEY` | Master key to authorize global workspace wipe (`POST /api/v1/reset`) | Recommended for production | `sor-admin-secret-2026` |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID (for downloading incoming WhatsApp MMS) | Optional (for real WhatsApp phone) | `ACxxxxxxxx...` |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token (for downloading incoming WhatsApp MMS) | Optional (for real WhatsApp phone) | `your_twilio_token` |

---

### Setting Secrets Locally

For local development and testing, create a `.env` file in the project root:

```bash
# 1. Copy the template to .env
cp .env.example .env

# 2. Edit .env with your values or set via shell
export TYPESAFE_API_KEY="your-typesafe-key-here"
export SANDBOX_ADMIN_KEY="your-custom-admin-key"
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="your-twilio-auth-token"
```

To set secrets directly from your terminal using inline environment variables:

```bash
# Run FastAPI with custom secrets
TYPESAFE_API_KEY="your-key" SANDBOX_ADMIN_KEY="custom-admin" .venv/bin/uvicorn app.api.main:app --port 8000

# Run Streamlit with custom secrets
TYPESAFE_API_KEY="your-key" .venv/bin/streamlit run app/ui/dashboard_app.py
```

---

### Setting Secrets for Modal Deployment

Modal uses managed secret stores via the `modal` CLI. As defined in [`modal_deploy.py`](modal_deploy.py), the app looks for the secret group named **`complaint-sandbox-secrets`**.

#### 1. Install & Authenticate Modal CLI (if not already installed)
```bash
# Install modal in your environment
pip install modal

# Authenticate with Modal
modal setup
```

#### 2. Create the Secret Group via Modal CLI

You can create the secret group in Modal directly from command line arguments:

```bash
modal secret create complaint-sandbox-secrets \
  TYPESAFE_API_KEY="your-typesafe-key-here" \
  TYPESAFE_API_URL="https://api.typesafe.ai/v1/decide" \
  DEFAULT_ENGINE_MODE="SIMULATED" \
  SANDBOX_ADMIN_KEY="your-custom-admin-key" \
  TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  TWILIO_AUTH_TOKEN="your-twilio-auth-token"
```

Or, if you already have a configured local `.env` file, populate the Modal secret directly from it:

```bash
modal secret create complaint-sandbox-secrets --from-dotenv .env
```

#### 3. Update Existing Modal Secrets
To update an existing secret group with new values without re-creating it:
```bash
modal secret update complaint-sandbox-secrets \
  TYPESAFE_API_KEY="your-updated-key"
```

---

## Deployment to Modal

Deploy the full tri-pillar stack (FastAPI REST API, Mounted FastMCP Server, and Streamlit Dashboard) to Modal serverless infrastructure:

```bash
# 1. Deploy the app
modal deploy modal_deploy.py

# 2. View live logs and endpoints
modal app list
```

Modal will print:
- **`api` URL**: `https://<workspace>--social-housing-complaint-classifier-sandbox-api.modal.run`
  - Docs: `.../docs`
  - MCP SSE: `.../mcp/sse`
  - Twilio WhatsApp Webhook: `.../api/v1/webhooks/whatsapp/twilio`
- **`dashboard` URL**: `https://<workspace>--social-housing-complaint-classifier-sandbox-dashboard.modal.run`

---

## Quickstart

### 1. Run the Automated Test Suite
```bash
.venv/bin/pytest -v
```

### 2. Launch the Interactive Streamlit Prototype (Landing Page + Sandbox + Product Insights)
```bash
.venv/bin/streamlit run app/ui/dashboard_app.py
```
*(Note: The Streamlit dashboard automatically connects to `http://127.0.0.1:8000/api/v1` when the FastAPI server is running, or seamlessly runs in standalone in-process mode if `uvicorn` is not started.)*

### 3. (Optional) Run the FastAPI + FastMCP Server Alongside Streamlit
```bash
.venv/bin/uvicorn app.api.main:app --reload --port 8000
```
- **Interactive OpenAPI Docs**: `http://127.0.0.1:8000/docs`
- **FastMCP SSE Endpoint**: `http://127.0.0.1:8000/mcp/sse`
- **Twilio WhatsApp Webhook**: `http://127.0.0.1:8000/api/v1/webhooks/whatsapp/twilio`

### 4. Phase 4 Open-Data Pipeline & Feeds CLI
Generate stratified benchmark datasets (Ombudsman proportions) or refresh trade SOR schedules:
```bash
# Generate 500 stratified complaints (JSONL)
.venv/bin/python -m app.data_pipeline.cli --samples 500 --output data/synthetic_complaints_500.jsonl

# Refresh active catalog for a trade (up to 20 codes)
.venv/bin/python -m app.data_pipeline.cli --refresh-trade PLUM --max-codes 20

# Reset active catalog back to the 18-code Base Set
.venv/bin/python -m app.data_pipeline.cli --reset-catalog
```
For full architectural details, feed inventories, and walkthroughs, see the [Phase 4 Feeds Guide](docs/phase_4_feeds_guide.md).


