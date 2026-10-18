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
