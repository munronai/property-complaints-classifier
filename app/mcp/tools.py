"""Model-Controlled Read, Simulation, and Actuator Tools for FastMCP."""

from typing import Any, Dict, Optional

from app.domain.enums import IntakeChannel
from app.domain.presets import get_preset_by_id
from app.domain.schemas import ComplaintIntakeRequest
from app.storage.session_store import session_store


def exec_get_latest_triage(
    property_id: str = "prop_oak_01",
    session_id: str = "default",
) -> Dict[str, Any]:
    """Read Tool implementation: retrieves the latest triage ticket and session KPI telemetry."""
    ticket = session_store.get_latest_ticket_for_property(
        property_id=property_id, session_id=session_id
    )
    return {
        "property_id": property_id,
        "session_id": session_id,
        "latest_ticket": ticket.model_dump() if ticket else None,
        "telemetry": session_store.compute_telemetry(session_id=session_id),
    }


def exec_submit_complaint_triage(
    complaint_text: str,
    property_id: str = "prop_oak_01",
    synthetic_image_preset: Optional[str] = None,
    existing_job_ref: Optional[str] = None,
    session_id: str = "default",
) -> Dict[str, Any]:
    """Intake & Classification Tool implementation: runs TypeSafe Jev Pass 1 & 2 and TriageEscalationGuard."""
    req = ComplaintIntakeRequest(
        complaint_text=complaint_text,
        property_id=property_id,
        channel=IntakeChannel.MCP_AGENT,
        synthetic_image_preset=synthetic_image_preset,
        existing_job_ref=existing_job_ref,
        session_id=session_id,
    )
    ticket = session_store.orchestrator.process_intake(req)
    saved = session_store.add_ticket(ticket, session_id=session_id)
    return {
        "ticket": saved.model_dump(exclude={"normalized_image_base64"}),
        "telemetry": session_store.compute_telemetry(session_id=session_id),
    }


def exec_simulate_complaint_event(
    preset_id: str = "preset_ambiguous_margin",
    session_id: str = "default",
) -> Dict[str, Any]:
    """Simulation Tool implementation: injects one of the 9 Time-Machine scenario presets and returns telemetry."""
    preset = get_preset_by_id(preset_id)
    req = ComplaintIntakeRequest(
        complaint_text=preset.complaint_text,
        property_id=preset.property_id,
        channel=preset.channel,
        synthetic_image_preset=preset.synthetic_image_preset,
        existing_job_ref=preset.existing_job_ref,
        session_id=session_id,
    )
    ticket = session_store.orchestrator.process_intake(req)
    saved = session_store.add_ticket(ticket, session_id=session_id)
    return {
        "preset_id": preset.preset_id,
        "preset_title": preset.title,
        "ticket": saved.model_dump(exclude={"normalized_image_base64"}),
        "telemetry": session_store.compute_telemetry(session_id=session_id),
    }


def exec_approve_or_override_work_order(
    ticket_id: str,
    override_sor: Optional[str] = None,
    surveyor_notes: Optional[str] = None,
    session_id: str = "default",
) -> Dict[str, Any]:
    """Actuator Tool implementation: approves an escalated ticket or overrides its M3NHF SOR code."""
    updated = session_store.approve_or_override_ticket(
        ticket_id=ticket_id,
        session_id=session_id,
        override_sor=override_sor,
        surveyor_notes=surveyor_notes,
    )
    return {
        "status": "approved_or_overridden",
        "ticket": updated.model_dump(exclude={"normalized_image_base64"}),
        "telemetry": session_store.compute_telemetry(session_id=session_id),
    }


def register_mcp_tools(mcp: Any) -> None:
    """Registers Read, Simulation, and Actuator tools on the FastMCP server."""

    @mcp.tool()
    def get_latest_triage(
        property_id: str = "prop_oak_01",
        session_id: str = "default",
    ) -> Dict[str, Any]:
        """Read Tool: Fetches the latest resident complaint triage report and telemetry for a property."""
        return exec_get_latest_triage(property_id=property_id, session_id=session_id)

    @mcp.tool()
    def submit_complaint_triage(
        complaint_text: str,
        property_id: str = "prop_oak_01",
        synthetic_image_preset: Optional[str] = None,
        existing_job_ref: Optional[str] = None,
        session_id: str = "default",
    ) -> Dict[str, Any]:
        """Intake Tool: Evaluates a resident/contractor complaint via TypeSafe Jev + M3NHF SOR gating."""
        return exec_submit_complaint_triage(
            complaint_text=complaint_text,
            property_id=property_id,
            synthetic_image_preset=synthetic_image_preset,
            existing_job_ref=existing_job_ref,
            session_id=session_id,
        )

    @mcp.tool()
    def simulate_complaint_event(
        preset_id: str = "preset_ambiguous_margin",
        session_id: str = "default",
    ) -> Dict[str, Any]:
        """Simulation Tool: Injects one of the 9 Time-Machine scenario presets and returns gating telemetry."""
        return exec_simulate_complaint_event(preset_id=preset_id, session_id=session_id)

    @mcp.tool()
    def approve_or_override_work_order(
        ticket_id: str,
        override_sor: Optional[str] = None,
        surveyor_notes: Optional[str] = None,
        session_id: str = "default",
    ) -> Dict[str, Any]:
        """Actuator Tool: Approves an escalated repair ticket or overrides its M3NHF SOR code for HMS dispatch."""
        return exec_approve_or_override_work_order(
            ticket_id=ticket_id,
            override_sor=override_sor,
            surveyor_notes=surveyor_notes,
            session_id=session_id,
        )
