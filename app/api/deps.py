"""FastAPI dependency injection providers for session store and triage orchestrator."""

from typing import Optional
from fastapi import Query

from app.engine.orchestrator import ComplaintTriageOrchestrator
from app.storage.session_store import SessionStore, session_store


def get_session_store() -> SessionStore:
    """Provides the singleton SessionStore instance."""
    return session_store


def get_orchestrator() -> ComplaintTriageOrchestrator:
    """Provides the ComplaintTriageOrchestrator instance."""
    return session_store.orchestrator


def resolve_session_id(
    session: Optional[str] = Query(
        default="default",
        description="Session ID for Zero-DB Copy-on-First-Access workspace isolation",
    ),
) -> str:
    """Normalizes the session query parameter."""
    return (session or "default").strip() or "default"
