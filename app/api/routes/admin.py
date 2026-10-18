"""Session Workspace Reset & Role-Scoped Admin Key Protection endpoints."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_session_store
from app.storage.session_store import PermissionDeniedError, SessionStore

router = APIRouter(tags=["Workspace Administration"])


class WorkspaceResetRequest(BaseModel):
    """JSON POST body for resetting a user session workspace or protected Golden Baseline."""

    session_id: str = Field(default="default", description="Session workspace to reset")
    all: bool = Field(
        default=False,
        description="Set to true to wipe all sessions and reseed Golden Baseline (requires admin_key)",
    )
    admin_key: Optional[str] = Field(
        default=None,
        description="SANDBOX_ADMIN_KEY passed inside JSON POST body (never in URL querystring)",
    )


@router.post("/reset")
async def reset_workspace_endpoint(
    payload: WorkspaceResetRequest,
    store: SessionStore = Depends(get_session_store),
) -> Dict[str, Any]:
    """Resets a scoped user session (unrestricted) or wipes the global baseline (requires admin_key)."""
    try:
        return store.reset_workspace(
            session_id=payload.session_id,
            reset_all=payload.all,
            admin_key=payload.admin_key,
        )
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
