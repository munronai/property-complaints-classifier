"""Complaint Triage Intake and M3NHF Schedule of Rates Catalog endpoints."""

from dataclasses import asdict
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_session_store
from app.domain.schemas import ComplaintIntakeRequest, TriageTicketRecord
from app.domain.sor_catalog import (
    M3NHF_SOR_CATALOG,
    MESSAGE_INTENT_CRITERIA,
    REPAIR_PRIORITY_LEVELS,
    TRADE_CRITERIA,
    get_catalog_summary,
    refresh_sor_catalog_for_trade,
    reset_sor_catalog_to_base,
)
from app.engine.image_normalizer import SYNTHETIC_IMAGE_CATALOG
from app.storage.session_store import SessionStore

router = APIRouter(tags=["Complaints & M3NHF Catalog"])


class CatalogRefreshRequest(BaseModel):
    trade: str = Field(
        default="PLUM",
        description="Trade code (PLUM, DAMP, ROOF, JOIN, ELEC, PLAS, or ALL) to import SOR codes for.",
    )
    max_codes: int = Field(
        default=20,
        ge=1,
        le=20,
        description="Maximum SOR codes per trade to import from the Phase 4 open-data feed (up to 20).",
    )
    session_id: Optional[str] = Field(default="default")


@router.get("/catalog")
async def get_sor_catalog() -> Dict[str, Any]:
    """Returns the complete M3NHF SOR catalog by trade, Stage 1 criteria, summary counts, and synthetic image options."""
    catalog_by_trade = {
        trade.value: [asdict(item) for item in items]
        for trade, items in M3NHF_SOR_CATALOG.items()
    }
    return {
        "trade_criteria": TRADE_CRITERIA,
        "message_intent_criteria": MESSAGE_INTENT_CRITERIA,
        "repair_priority_levels": REPAIR_PRIORITY_LEVELS,
        "m3nhf_catalog": catalog_by_trade,
        "catalog_summary": get_catalog_summary(),
        "synthetic_images": SYNTHETIC_IMAGE_CATALOG,
    }


@router.post("/catalog/refresh")
async def refresh_sor_catalog_endpoint(
    payload: CatalogRefreshRequest,
) -> Dict[str, Any]:
    """Imports up to `max_codes` (up to 20) M3NHF SOR codes for the selected trade from the Phase 4 feed."""
    try:
        return refresh_sor_catalog_for_trade(
            trade=payload.trade,
            max_codes=payload.max_codes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/catalog/reset")
async def reset_sor_catalog_endpoint() -> Dict[str, Any]:
    """Resets the active M3NHF Schedule of Rates catalog back to the 17-item Base Set."""
    return reset_sor_catalog_to_base()


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
