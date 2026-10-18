"""Strict Pydantic v2 data contracts for intake, TypeSafe Jev outputs, and triage tickets."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.domain.enums import (
    EngineMode,
    EscalationReason,
    IntakeChannel,
    MessageIntent,
    PortfolioType,
    RoutingDestination,
    TicketStatus,
    TradeCode,
)


class GatingThresholds(BaseModel):
    """Configurable circuit-breaker thresholds for TriageEscalationGuard."""

    min_trade_confidence: float = Field(default=0.70, ge=0.0, le=1.0)
    min_sor_confidence: float = Field(default=0.65, ge=0.0, le=1.0)
    min_probability_margin: float = Field(default=0.15, ge=0.0, le=1.0)
    damp_hazard_threshold: float = Field(default=0.40, ge=0.0, le=1.0)
    inappropriate_content_threshold: float = Field(default=0.50, ge=0.0, le=1.0)


class ImageTelemetry(BaseModel):
    """Metadata captured during Pillow EXIF normalization and <=1568px scaling."""

    asset_ref: str
    original_width: int
    original_height: int
    normalized_width: int
    normalized_height: int
    exif_transposed: bool
    resized: bool
    mime_type: str = "image/jpeg"
    size_bytes: int
    discarded_by_safety_gate: bool = False


class ComplaintIntakeRequest(BaseModel):
    """Primary payload for evaluating a resident or contractor submission."""

    complaint_text: str = Field(..., min_length=1, description="Resident or contractor message text")
    property_id: str = Field(default="prop_oak_01", description="Target property identifier")
    channel: IntakeChannel = Field(default=IntakeChannel.DASHBOARD_UI)
    engine_mode: EngineMode = Field(default=EngineMode.SIMULATED)
    session_id: Optional[str] = Field(default=None)
    image_base64: Optional[str] = Field(default=None, description="Optional raw base64 image")
    synthetic_image_preset: Optional[str] = Field(
        default=None,
        description="Optional built-in synthetic defect image key (e.g. 'black_mould', 'sink_leak')",
    )
    existing_job_ref: Optional[str] = Field(
        default=None,
        description="Optional reference to an existing or recently completed works order",
    )
    thresholds: Optional[GatingThresholds] = Field(default=None)


class WhatsAppWebhookPayload(BaseModel):
    """Incoming WhatsApp Business Cloud / Twilio webhook simulation payload."""

    from_phone: str = Field(default="+447700900123")
    resident_name: str = Field(default="A. Taylor (Flat 4, Oak Court)")
    property_id: str = Field(default="prop_oak_01")
    message_body: str = Field(..., min_length=1)
    media_base64: Optional[str] = Field(default=None)
    synthetic_image_preset: Optional[str] = Field(default=None)
    existing_job_ref: Optional[str] = Field(default=None)
    session_id: Optional[str] = Field(default=None)
    engine_mode: EngineMode = Field(default=EngineMode.SIMULATED)
    thresholds: Optional[GatingThresholds] = Field(default=None)


class TriageDecisionModel(BaseModel):
    """Pydantic representation of the TriageEscalationGuard evaluation result."""

    auto_approve: bool
    destination: RoutingDestination
    message_intent: MessageIntent = MessageIntent.NEW_REPAIR_DEFECT
    assigned_trade: Optional[str] = None
    assigned_sor: Optional[str] = None
    assigned_sor_description: Optional[str] = None
    discard_media: bool = False
    is_completed_job_recall: bool = False
    reasons: List[EscalationReason] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TriageTicketRecord(BaseModel):
    """Complete immutable/session-scoped audit record of a triaged complaint."""

    ticket_id: str
    session_id: str
    property_id: str
    property_name: str
    channel: IntakeChannel
    engine_mode: EngineMode
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    complaint_text: str
    existing_job_ref: Optional[str] = None
    has_image: bool = False
    media_discarded: bool = False
    normalized_image_base64: Optional[str] = None
    image_telemetry: Optional[ImageTelemetry] = None
    stage1_output: Dict[str, Any]
    stage2_output: Optional[Dict[str, Any]] = None
    stage2_skipped_reason: Optional[str] = None
    decision: TriageDecisionModel
    status: TicketStatus
    surveyor_override_sor: Optional[str] = None
    surveyor_notes: Optional[str] = None


class ScenarioPreset(BaseModel):
    """Pre-configured Time-Machine scenario preset with educational help metadata."""

    preset_id: str
    title: str
    badge: str
    channel: IntakeChannel
    property_id: str
    complaint_text: str
    synthetic_image_preset: Optional[str] = None
    existing_job_ref: Optional[str] = None
    what_it_tests: str
    expected_outcome: str
    expected_destination: RoutingDestination
    expected_reasons: List[EscalationReason] = Field(default_factory=list)


class PropertyBaseline(BaseModel):
    """Baseline property entity for Zero-DB multi-user session isolation."""

    property_id: str
    name: str
    address: str
    portfolio_type: PortfolioType = PortfolioType.SOCIAL_HOUSING
    landlord_name: str = "Metropolitan Thames Valley Housing (Sandbox)"
    tenant_Summary: str = "Assured Tenancy — 2 Bed Flat"
    active_wip_jobs: List[str] = Field(default_factory=list)
    completed_jobs: List[str] = Field(default_factory=list)
