"""WhatsApp Business Cloud & Twilio Webhook intake adapters."""

import base64
import os
import re
from typing import Optional
from fastapi import APIRouter, Depends, Form, Query, Request, Response
import httpx

from app.api.deps import get_session_store
from app.domain.enums import IntakeChannel
from app.domain.schemas import (
    ComplaintIntakeRequest,
    TriageTicketRecord,
    WhatsAppWebhookPayload,
)
from app.storage.session_store import SessionStore

router = APIRouter(tags=["WhatsApp Webhook"])

# Known phone numbers mapped to baseline properties (fallback to prop_oak_01)
PHONE_PROPERTY_MAP = {
    "+447700900123": "prop_oak_01",
    "+447700900124": "prop_elm_02",
    "+447700900125": "prop_cedar_03",
}


def _resolve_property_from_message(body: str, from_phone: str) -> tuple[str, str]:
    """Extracts explicit hashtag tag like #elm, #cedar, or #oak if provided; otherwise matches phone or defaults to prop_oak_01."""
    clean_body = body
    if "#elm" in body.lower():
        clean_body = re.sub(r"#elm", "", clean_body, flags=re.IGNORECASE).strip()
        return "prop_elm_02", clean_body
    if "#cedar" in body.lower():
        clean_body = re.sub(r"#cedar", "", clean_body, flags=re.IGNORECASE).strip()
        return "prop_cedar_03", clean_body
    if "#oak" in body.lower():
        clean_body = re.sub(r"#oak", "", clean_body, flags=re.IGNORECASE).strip()
        return "prop_oak_01", clean_body

    normalized_phone = from_phone.replace("whatsapp:", "").strip()
    matched_prop = PHONE_PROPERTY_MAP.get(normalized_phone, "prop_oak_01")
    return matched_prop, clean_body


def _build_twiml_reply(ticket: TriageTicketRecord) -> str:
    """Generates an automated two-way WhatsApp message body formatted as TwiML XML."""
    tid = ticket.ticket_id
    dec = ticket.decision
    dest = dec.destination.value if hasattr(dec.destination, "value") else str(dec.destination)
    sor_assigned = dec.assigned_sor or "Under Review"

    if dest == "AUTO_DISPATCH_HMS":
        msg = f"✅ Repair booked (Ref: {tid}, M3NHF SOR: {sor_assigned}). A contractor will attend within the routine SLA."
    elif dest == "DISREPAIR_LEGAL_TEAM":
        msg = f"🚨 Damp/mould report (Ref: {tid}) logged under Awaab's Law. Our Environmental Health & Disrepair team has been alerted for priority inspection."
    elif dest == "OUT_OF_HOURS_DUTY_OFFICER":
        msg = f"🚨 EMERGENCY (Ref: {tid}): Paged 24h Out-of-Hours Duty Officer. Please do not touch wet electrical switches."
    elif dest in ("CUSTOMER_SERVICE_WIP_DESK", "CONTRACTOR_FINANCE_DESK"):
        ref = ticket.existing_job_ref or "your reference"
        msg = f"📋 Update request (Ref: {tid}) linked to {ref} and forwarded to Customer Service / Finance. No duplicate order raised."
    elif dest == "QUALITY_RECALL_SURVEYOR_REVIEW":
        ref = ticket.existing_job_ref or "recent repair"
        msg = f"🔍 Sorry {ref} is still faulty. Remedial SOR {sor_assigned} has been scoped and escalated to our Quality Recall Surveyor."
    elif dest == "DISCARDED_INAPPROPRIATE_CONTENT":
        msg = f"🛑 Attachment violated acceptable use policy and was purged (Ref: {tid})."
    else:
        msg = f"👷 Photo received (Ref: {tid}). A Technical Surveyor is confirming the exact part ({sor_assigned}) today before dispatch."

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{msg}</Message>
</Response>"""


@router.post("/webhooks/whatsapp", response_model=TriageTicketRecord)
async def handle_whatsapp_webhook(
    payload: WhatsAppWebhookPayload,
    store: SessionStore = Depends(get_session_store),
) -> TriageTicketRecord:
    """Normalizes an incoming WhatsApp JSON payload (simulator or webhook) and evaluates it via TypeSafe Jev."""
    effective_synth = (
        None
        if (payload.media_base64 and str(payload.media_base64).strip())
        else payload.synthetic_image_preset
    )
    intake_request = ComplaintIntakeRequest(
        complaint_text=payload.message_body,
        property_id=payload.property_id,
        channel=IntakeChannel.WHATSAPP,
        engine_mode=payload.engine_mode,
        session_id=payload.session_id or "default",
        image_base64=payload.media_base64,
        synthetic_image_preset=effective_synth,
        existing_job_ref=payload.existing_job_ref,
        thresholds=payload.thresholds,
    )
    ticket = store.orchestrator.process_intake(
        request=intake_request,
        thresholds=payload.thresholds,
    )
    saved = store.add_ticket(ticket, session_id=intake_request.session_id)
    return saved


@router.post("/webhooks/whatsapp/twilio")
async def handle_twilio_whatsapp_webhook(
    request: Request,
    From: str = Form("whatsapp:+447700900123"),
    Body: str = Form(""),
    NumMedia: int = Form(0),
    MediaUrl0: Optional[str] = Form(None),
    session: Optional[str] = Query(None),
    store: SessionStore = Depends(get_session_store),
) -> Response:
    """Twilio WhatsApp Sandbox webhook adapter.

    Accepts application/x-www-form-urlencoded payloads from Twilio, downloads attached media
    (with HTTP Basic Auth if TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN are set), processes the complaint
    through the 4-stage engine, and returns TwiML XML so the sender gets an instant WhatsApp reply.
    """
    session_id = session or request.query_params.get("session") or "default"
    property_id, message_body = _resolve_property_from_message(Body, From)

    image_base64: Optional[str] = None
    if NumMedia > 0 and MediaUrl0:
        try:
            auth = None
            twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
            twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
            if twilio_sid and twilio_token:
                auth = (twilio_sid, twilio_token)

            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                resp = client.get(MediaUrl0, auth=auth)
                if resp.status_code == 200:
                    image_base64 = base64.b64encode(resp.content).decode("utf-8")
        except Exception:
            image_base64 = None

    intake_request = ComplaintIntakeRequest(
        complaint_text=message_body or "Photo sent via WhatsApp",
        property_id=property_id,
        channel=IntakeChannel.WHATSAPP,
        session_id=session_id,
        image_base64=image_base64,
    )
    ticket = store.orchestrator.process_intake(request=intake_request)
    saved = store.add_ticket(ticket, session_id=session_id)

    twiml = _build_twiml_reply(saved)
    return Response(content=twiml, media_type="application/xml")
