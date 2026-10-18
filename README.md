# Social Housing & Property Complaint Classifier Sandbox

A **Tri-Pillar Sandbox & Prototype Platform** (Typed FastAPI REST API + Mounted FastMCP Agent Server + Modular Streamlit Control Deck) that assesses multi-channel resident and commercial property complaints (text + multimodal photos via **Web Dashboard** and **WhatsApp Business Webhooks**) using **TypeSafe Jev** and **M3NHF Schedule of Rates (SOR) codes**, wrapped in **Hard Statutory & Confidence Gating Middleware (`TriageEscalationGuard`)**.

---

## Key Capabilities

1. **Prototype Landing Page with Two Option Cards & Below-the-Fold Help**:
   - **Option Card 1 — Interactive Sandbox & Control Deck**: Live multi-channel complaint intake (Web Portal & WhatsApp simulator), 9 Time-Machine scenario presets, real-time gating threshold sliders, Surveyor review & recall queue, and an embedded browser MCP client.
   - **Option Card 2 — Product Thinking, Insights & Decisions**: Domain research breakdown (UK Housing Ombudsman & Commercial Property distributions), rationale for two-stage Jev + margin gating vs. raw LLM chat, and completed-repair recall vs. WIP re-routing logic.
   - **Below-the-Cards Help & Preset Guide**: Step-by-step usage instructions and a complete reference table explaining what each of the 9 Time-Machine presets is designed to test.
2. **Stage 1 Content Safety Gate (Flag & Purge Media)**:
   - Detects inappropriate/rude photo attachments or abusive submissions in Stage 1 (`inappropriate_content_flag`), halts Stage 2, purges raw base64 media bytes from memory/storage (`media_discarded=True`), and logs `DISCARDED_INAPPROPRIATE_CONTENT`.
3. **Stage 1 Message Intent Classification & Re-Routing**:
   - **WIP Repair Updates & Contractor Scheduling (`WIP_REPAIR_UPDATE`, `CONTRACTOR_SCHEDULING`)** $\rightarrow$ Short-circuits Stage 2 SOR matching and routes to `CUSTOMER_SERVICE_WIP_DESK`.
   - **Contractor Late Payment Inquiries (`CONTRACTOR_PAYMENT_INQUIRY`)** $\rightarrow$ Short-circuits Stage 2 and routes to `CONTRACTOR_FINANCE_DESK`.
   - **Completed Repair Job Complaints (`COMPLETED_REPAIR_COMPLAINT`)** $\rightarrow$ Evaluates **both** Pass 1 and Pass 2 (`resolve_sor_code`) to scope the remedial M3NHF SOR code, then routes to `QUALITY_RECALL_SURVEYOR_REVIEW` (`is_completed_job_recall=True`).
4. **Hard Circuit-Breaker Middleware (`TriageEscalationGuard`)**:
   - Enforces **Awaab's Law** damp hazard ($\ge 0.40 \rightarrow$ `DISREPAIR_LEGAL_TEAM`), **24-hour Priority 3 Emergencies** ($\rightarrow$ `OUT_OF_HOURS_DUTY_OFFICER`), **Trade Confidence** ($\ge 0.70$), **SOR Confidence** ($\ge 0.65$), and **Top-1 vs. Top-2 Probability Margin** ($\ge 0.15$).

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

