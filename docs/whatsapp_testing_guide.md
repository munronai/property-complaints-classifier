# Testing Across Intake Channels & Connecting a Live WhatsApp Phone

## 1. Why Web Portal, WhatsApp, and MCP Feel Similar After Intake (And Where They Actually Differ)

In the **Complaint Classifier**, all three intake channels intentionally converge into a single canonical domain schema (`ComplaintIntakeRequest` in `app/domain/schemas.py`) before entering **Stages 2, 3, and 4** (TypeSafe Jev Pass 1 -> Bounded M3NHF SOR Pass 2 -> `TriageEscalationGuard`).

**Why unify the downstream pipeline?**
In social housing and commercial property management, **Awaab's Law statutory timelines**, **24-hour Emergency SLAs**, and **M3NHF Schedule of Rates (SOR) codes** must be enforced identically whether a tenant reports black mould on a web form, texts a photo on WhatsApp at 11 PM, or speaks to an AI voice/chat agent over MCP.

However, at **Stage 1 (The Channel Boundary)** and **Post-Stage 4 (The Tenant Response)**, the three channels have very different real-world responsibilities:

| Dimension | Web Portal (`DASHBOARD_UI`) | WhatsApp (`WHATSAPP`) | AI Agent (`MCP`) |
| :--- | :--- | :--- | :--- |
| **How Tenant Identity is Known** | Authenticated portal session (`property_id` and tenancy already known) | Unstructured phone number (`from_phone: +447700900123`) mapped to a tenancy record via CRM lookup | Agent passes `property_id` + `session_id` after reading `sor://properties/{id}/latest-triage` |
| **Input Structure** | Structured form fields (Category dropdown, Job Reference box, Description, File upload) | Conversational free-text (*"hi metal thing snapped see pic"*), voice notes, or multi-message threads | JSON-RPC 2.0 tool call (`submit_complaint_triage`) |
| **Media Characteristics** | Desktop/mobile file upload | Smartphone camera JPEG/HEIC with **rotated EXIF orientation tags** and WhatsApp media URLs requiring bearer-token download | Base64 or synthetic preset reference |
| **FastAPI Endpoint** | `POST /api/v1/complaints/triage` | `POST /api/v1/webhooks/whatsapp` | `GET /mcp/sse` (`tools/call`) |
| **Outbound Feedback Loop** | Synchronous HTTP JSON receipt rendered on the portal screen | **Asynchronous 2-way WhatsApp reply message** sent back to the resident's phone (e.g., booking confirmation, WIP status update, or emergency safety advice) | Structured JSON-RPC tool result returned into the LLM agent's context window |

---

## 2. What It Takes to Test Live from Your Real WhatsApp Phone

Our FastAPI backend already exposes `POST /api/v1/webhooks/whatsapp` (`app/api/routes/webhooks.py`). To send a message and photo from WhatsApp on your smartphone and watch it appear live on the Streamlit dashboard, you need **three small pieces**:

### Option A: Fastest Prototype Path — Twilio WhatsApp Sandbox (~10 Minutes, No Meta App Review)

Twilio provides a pre-approved **WhatsApp Sandbox** number so you can test from your personal phone immediately without waiting for Meta Business verification.

1. **Expose Your Local FastAPI Server Over HTTPS**:
   - Run `ngrok http 8000` locally (or deploy to Modal for a permanent `https://*.modal.run` URL).
2. **Activate the Twilio WhatsApp Sandbox**:
   - In the Twilio Console -> **Messaging** -> **Try it out** -> **Send a WhatsApp message**, join the sandbox from your phone.
   - Set the **"When a message comes in"** (`POST`) webhook URL to:
     `https://<your-ngrok-or-modal-domain>/api/v1/webhooks/whatsapp?session=<your_session_id>`
3. **Twilio Form-Data Adapter (~35 lines in `app/api/routes/webhooks.py`)**:
   - Twilio sends `application/x-www-form-urlencoded` fields (`From`, `Body`, `NumMedia`, `MediaUrl0`).
   - Map `From` (`whatsapp:+447...`) to a sandbox property (`prop_oak_01`), download `MediaUrl0` bytes into `image_base64`, run the orchestrator, and return a `<Response><Message>...</Message></Response>` TwiML reply so your phone gets an instant WhatsApp response with the Ticket ID, M3NHF SOR code, and routing decision.

### Option B: Production Path — Meta WhatsApp Business Cloud API

1. **Webhook Verification (`GET /api/v1/webhooks/whatsapp`)**: Echo `int(hub.challenge)` when `hub.verify_token` matches.
2. **Media Download (`POST /api/v1/webhooks/whatsapp`)**: Extract `messages[0].image.id`, query `https://graph.facebook.com/v21.0/{media_id}` with `Authorization: Bearer <WHATSAPP_TOKEN>`, download the JPEG bytes, and pass them to `normalize_image_bytes()`.
3. **Outbound Reply**: POST the Stage 4 routing summary back to `https://graph.facebook.com/v21.0/{phone_number_id}/messages`.
