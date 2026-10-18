"""MCP Static Baseline Resources and Dynamic Resource Templates."""

import json
from typing import Any

from app.storage.session_store import session_store


def get_latest_triage_json(property_id: str, session_id: str = "default") -> str:
    """Serializes the latest triage report and telemetry for a given property ID."""
    ticket = session_store.get_latest_ticket_for_property(
        property_id=property_id, session_id=session_id
    )
    telemetry = session_store.compute_telemetry(session_id=session_id)
    payload = {
        "property_id": property_id,
        "session_id": session_id,
        "latest_ticket": ticket.model_dump() if ticket else None,
        "workspace_telemetry": telemetry,
    }
    return json.dumps(payload, indent=2)


def register_mcp_resources(mcp: Any) -> None:
    """Registers concrete static resources and parameterized resource templates on FastMCP."""

    @mcp.resource("sor://properties/prop_oak_01/latest-triage")
    def get_golden_oak_latest_triage() -> str:
        """Concrete static resource for primary baseline property prop_oak_01."""
        return get_latest_triage_json(property_id="prop_oak_01", session_id="default")

    @mcp.resource("sor://properties/{property_id}/latest-triage")
    def get_dynamic_property_latest_triage(property_id: str) -> str:
        """Dynamic resource template for looking up any property's latest triage report."""
        return get_latest_triage_json(property_id=property_id, session_id="default")
