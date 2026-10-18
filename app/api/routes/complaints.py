"""Complaint Triage Intake and M3NHF Schedule of Rates Catalog endpoints."""

from dataclasses import asdict
from typing import Any, Dict
from fastapi import APIRouter, Depends

from app.api.deps import get_session_store
from app.domain.schemas import ComplaintIntakeRequest, TriageTicketRecord
from app.domain.sor_catalog import (
    M3NHF_SOR_CATALOG,
    MESSAGE_INTENT_CRITERIA,
    REPAIR_PRIORITY_LEVELS,
    TRADE_CRITERIA,
)
from app.engine.image_normalizer import SYNTHETIC_IMAGE_CATALOG
from app.storage.session_store import SessionStore

router = APIRouter(tags=["Complaints & M3NHF Catalog"])


@router.get("/catalog")
async def get_sor_catalog() -> Dict[str, Any]:
    """Returns the complete M3NHF SOR catalog by trade, Stage 1 criteria, and synthetic image options."""
    catalog_by_trade = {
        trade.value: [asdict(item) for item in items]
        for trade, items in M3NHF_SOR_CATALOG.items()
    }
    return {
        "trade_criteria": TRADE_CRITERIA,
        "message_intent_criteria": MESSAGE_INTENT_CRITERIA,
        "repair_priority_levels": REPAIR_PRIORITY_LEVELS,
        "m3nhf_catalog": catalog_by_trade,
        "synthetic_images": SYNTHETIC_IMAGE_CATALOG,
    }


@router.post("/complaints/triage", response_model=TriageTicketRecord)
async def triage_complaint_endpoint(
    payload: ComplaintIntakeRequest,
    store: SessionStore = Depends(get_session_store),
) -> TriageTicketRecord:
    """Evaluates a multimodal complaint through TypeSafe Jev Pass 1 & 2 and TriageEscalationGuard."""
    ticket = store.orchestrator.process_intake(
        request=payload,
        thresholds=payload.thresholds,
    )
    saved = store.add_ticket(ticket, session_id=payload.session_id)
    return saved
