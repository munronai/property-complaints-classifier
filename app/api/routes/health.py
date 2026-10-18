"""Health, Telemetry KPI, and Property Baseline endpoints."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends

from app.api.deps import get_session_store, resolve_session_id
from app.config import settings
from app.domain.schemas import PropertyBaseline
from app.storage.session_store import SessionStore

router = APIRouter(tags=["Health & Telemetry"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Returns API health status, active engine mode, and default gating thresholds."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "live_jev_configured": bool(settings.typesafe_api_key),
        "default_engine_mode": settings.default_engine_mode,
        "default_thresholds": {
            "min_trade_confidence": settings.min_trade_confidence,
            "min_sor_confidence": settings.min_sor_confidence,
            "min_probability_margin": settings.min_probability_margin,
            "damp_hazard_threshold": settings.damp_hazard_threshold,
            "inappropriate_content_threshold": settings.inappropriate_content_threshold,
        },
    }


@router.get("/telemetry")
async def get_workspace_telemetry(
    session_id: str = Depends(resolve_session_id),
    store: SessionStore = Depends(get_session_store),
) -> Dict[str, Any]:
    """Returns real-time KPI metrics for the active session workspace."""
    return store.compute_telemetry(session_id=session_id)


@router.get("/properties", response_model=List[PropertyBaseline])
async def list_properties(
    session_id: str = Depends(resolve_session_id),
    store: SessionStore = Depends(get_session_store),
) -> List[PropertyBaseline]:
    """Returns session-isolated properties (s_{session_id}_*)."""
    return store.get_properties(session_id=session_id)
