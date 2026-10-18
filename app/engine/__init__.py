"""Multimodal TypeSafe Jev Engine, Image Normalizer, Simulator, and Escalation Guard."""

from app.engine.escalation_guard import TriageDecisionResult, TriageEscalationGuard
from app.engine.image_normalizer import (
    SYNTHETIC_IMAGE_CATALOG,
    generate_synthetic_defect_image,
    prepare_image_for_jev,
)
from app.engine.jev_client import JevRepairsTriageEngine
from app.engine.simulator import SimulatedJevEngine


def __getattr__(name: str):
    if name == "ComplaintTriageOrchestrator":
        from app.engine.orchestrator import ComplaintTriageOrchestrator

        return ComplaintTriageOrchestrator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ComplaintTriageOrchestrator",
    "JevRepairsTriageEngine",
    "SYNTHETIC_IMAGE_CATALOG",
    "SimulatedJevEngine",
    "TriageDecisionResult",
    "TriageEscalationGuard",
    "generate_synthetic_defect_image",
    "prepare_image_for_jev",
]
