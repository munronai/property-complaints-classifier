"""WhatsApp Business Cloud / Twilio Webhook intake adapter."""

from fastapi import APIRouter, Depends

from app.api.deps import get_session_store
from app.domain.enums import IntakeChannel
from app.domain.schemas import (
    ComplaintIntakeRequest,
    TriageTicketRecord,
    WhatsAppWebhookPayload,
)
from app.storage.session_store import SessionStore

router = APIRouter(tags=["WhatsApp Webhook"])


@router.post("/webhooks/whatsapp", response_model=TriageTicketRecord)
async def handle_whatsapp_webhook(
    payload: WhatsAppWebhookPayload,
    store: SessionStore = Depends(get_session_store),
) -> TriageTicketRecord:
    """Normalizes an incoming WhatsApp text + media payload and evaluates it via TypeSafe Jev."""
    intake_request = ComplaintIntakeRequest(
        complaint_text=payload.message_body,
        property_id=payload.property_id,
        channel=IntakeChannel.WHATSAPP,
        engine_mode=payload.engine_mode,
        session_id=payload.session_id or "default",
        image_base64=payload.media_base64,
        synthetic_image_preset=payload.synthetic_image_preset,
        existing_job_ref=payload.existing_job_ref,
        thresholds=payload.thresholds,
    )
    ticket = store.orchestrator.process_intake(
        request=intake_request,
        thresholds=payload.thresholds,
    )
    saved = store.add_ticket(ticket, session_id=intake_request.session_id)
    return saved
