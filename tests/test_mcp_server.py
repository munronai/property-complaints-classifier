"""Unit and integration tests for Pillar 2 FastMCP Server, Tools, Resources, and Cloud Networking Safeguards."""

import json
import unittest
from fastapi.testclient import TestClient

from app.api.main import app
from app.mcp.resources import get_latest_triage_json
from app.mcp.security import MCP_TRANSPORT_SECURITY
from app.mcp.tools import (
    exec_approve_or_override_work_order,
    exec_get_latest_triage,
    exec_simulate_complaint_event,
    exec_submit_complaint_triage,
)


class TestFastMCPServerAndNetworkingSafeguards(unittest.TestCase):
    """Verifies Gotcha A (HTTP 421 DNS rebinding settings), Gotcha B (POST /mcp/sse -> 404), and MCP tools."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_gotcha_a_transport_security_whitelists_local_and_modal_domains(self) -> None:
        """Verifies TransportSecuritySettings is configured with localhost and *.modal.run wildcards."""
        self.assertIsNotNone(MCP_TRANSPORT_SECURITY)
        self.assertTrue(MCP_TRANSPORT_SECURITY.enable_dns_rebinding_protection)
        self.assertIn("localhost:*", MCP_TRANSPORT_SECURITY.allowed_hosts)
        self.assertIn("*.modal.run", MCP_TRANSPORT_SECURITY.allowed_hosts)
        self.assertIn("https://*.modal.run", MCP_TRANSPORT_SECURITY.allowed_origins)

    def test_gotcha_b_post_mcp_sse_returns_404_instead_of_405(self) -> None:
        """Verifies POST /mcp/sse returns HTTP 404 so mcp-remote falls back cleanly to GET SSE."""
        resp = self.client.post("/mcp/sse")
        self.assertEqual(resp.status_code, 404)
        self.assertIn(
            "requires HTTP GET. Pass '--transport sse-only' to mcp-remote.",
            resp.json()["detail"],
        )

    def test_mcp_resources_and_tools_execution(self) -> None:
        """Verifies MCP static/dynamic resource JSON and Read, Simulation, Intake, and Actuator tools."""
        # 1. Resource JSON lookup
        res_json = get_latest_triage_json("prop_oak_01", session_id="mcp_tester")
        parsed = json.loads(res_json)
        self.assertEqual(parsed["property_id"], "prop_oak_01")
        self.assertIsNotNone(parsed["latest_ticket"])

        # 2. Read Tool: get_latest_triage
        read_res = exec_get_latest_triage(
            property_id="prop_oak_01", session_id="mcp_tester"
        )
        self.assertIn("telemetry", read_res)
        self.assertIsNotNone(read_res["latest_ticket"])

        # 3. Intake Tool: submit_complaint_triage
        intake_res = exec_submit_complaint_triage(
            complaint_text="Snapped hinge on kitchen cupboard door, see attached photo",
            property_id="prop_elm_02",
            synthetic_image_preset="broken_hinge",
            session_id="mcp_tester",
        )
        self.assertTrue(intake_res["ticket"]["decision"]["auto_approve"])
        self.assertEqual(intake_res["ticket"]["decision"]["assigned_sor"], "125011")

        # 4. Simulation Tool: simulate_complaint_event
        sim_res = exec_simulate_complaint_event(
            preset_id="preset_ambiguous_margin",
            session_id="mcp_tester",
        )
        sim_ticket_id = sim_res["ticket"]["ticket_id"]
        self.assertFalse(sim_res["ticket"]["decision"]["auto_approve"])

        # 5. Actuator Tool: approve_or_override_work_order
        act_res = exec_approve_or_override_work_order(
            ticket_id=sim_ticket_id,
            override_sor="192001",
            surveyor_notes="Approved via MCP Actuator Tool",
            session_id="mcp_tester",
        )
        self.assertEqual(act_res["status"], "approved_or_overridden")
        self.assertEqual(act_res["ticket"]["decision"]["assigned_sor"], "192001")


if __name__ == "__main__":
    unittest.main()
