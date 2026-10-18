"""Time-Machine Scenario Presets and Simulation Injection endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_session_store
from app.domain.enums import EngineMode
from app.domain.presets import SCENARIO_PRESETS, get_preset_by_id
from app.domain.schemas import (
    ComplaintIntakeRequest,
    GatingThresholds,
    ScenarioPreset,
    TriageTicketRecord,
)
from app.storage.session_store import SessionStore

router = APIRouter(tags=["Time-Machine Simulation"])


class SimulationTriggerRequest(BaseModel):
    """Payload to inject one of the 9 Time-Machine Scenario Presets into a session workspace."""

    preset_id: str = Field(..., description="Preset identifier from /api/v1/presets")
    session_id: str = Field(default="default")
    engine_mode: EngineMode = Field(default=EngineMode.SIMULATED)
    thresholds: Optional[GatingThresholds] = Field(default=None)


@router.get("/presets", response_model=List[ScenarioPreset])
async def list_scenario_presets() -> List[ScenarioPreset]:
    """Returns all 9 pre-configured Time-Machine scenario presets with help metadata."""
    return SCENARIO_PRESETS


@router.post("/simulate", response_model=TriageTicketRecord)
async def trigger_scenario_preset(
    payload: SimulationTriggerRequest,
    store: SessionStore = Depends(get_session_store),
) -> TriageTicketRecord:
    """Executes a Time-Machine preset scenario and records the ticket in the session store."""
    try:
        preset = get_preset_by_id(payload.preset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    intake_req = ComplaintIntakeRequest(
        complaint_text=preset.complaint_text,
        property_id=preset.property_id,
        channel=preset.channel,
        engine_mode=payload.engine_mode,
        session_id=payload.session_id,
        synthetic_image_preset=preset.synthetic_image_preset,
        existing_job_ref=preset.existing_job_ref,
        thresholds=payload.thresholds,
    )
    ticket = store.orchestrator.process_intake(
        request=intake_req,
        thresholds=payload.thresholds,
    )
    saved = store.add_ticket(ticket, session_id=payload.session_id)
    return saved
