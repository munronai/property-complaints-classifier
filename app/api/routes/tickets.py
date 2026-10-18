"""Surveyor Review Queue, Ticket Inspection, and M3NHF SOR Override endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.deps import get_session_store, resolve_session_id
from app.domain.schemas import TriageTicketRecord
from app.storage.session_store import SessionStore

router = APIRouter(tags=["Tickets & Surveyor Review"])


class TicketApprovalRequest(BaseModel):
    """Payload for a Repairs Surveyor or Agent to approve or override an escalated ticket."""

    session_id: str = Field(default="default")
    override_sor: Optional[str] = Field(
        default=None,
        description="Optional replacement 6-digit M3NHF SOR code (e.g. '192005')",
    )
    surveyor_notes: Optional[str] = Field(
        default=None,
        description="Audit note explaining surveyor approval or recall action",
    )


@router.get("/tickets", response_model=List[TriageTicketRecord])
async def list_tickets(
    session_id: str = Depends(resolve_session_id),
    property_id: Optional[str] = Query(default=None),
    store: SessionStore = Depends(get_session_store),
) -> List[TriageTicketRecord]:
    """Returns all triaged tickets in the active session workspace (newest first)."""
    return store.get_tickets(session_id=session_id, property_id=property_id)


@router.post("/tickets/{ticket_id}/approve", response_model=TriageTicketRecord)
async def approve_or_override_ticket(
    ticket_id: str,
    payload: TicketApprovalRequest,
    store: SessionStore = Depends(get_session_store),
) -> TriageTicketRecord:
    """Approves an escalated ticket or overrides its M3NHF SOR code for HMS dispatch."""
    try:
        return store.approve_or_override_ticket(
            ticket_id=ticket_id,
            session_id=payload.session_id,
            override_sor=payload.override_sor,
            surveyor_notes=payload.surveyor_notes,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
