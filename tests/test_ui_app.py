"""Unit and headless integration tests for Pillar 3 Modular Streamlit UI components and views."""

import unittest

from app.ui.api_client import SandboxAPIClient
from app.ui.views.mcp_console import discover_mcp_primitives, execute_embedded_mcp_tool


class TestStreamlitUIComponentsAndClient(unittest.TestCase):
    """Verifies SandboxAPIClient standalone resilience and Embedded MCP Console execution."""

    def setUp(self) -> None:
        # Point to an unused port to verify non-blocking fallback to in-process store
        self.client = SandboxAPIClient(base_url="http://127.0.0.1:59999/api/v1")

    def test_api_client_falls_back_cleanly_when_backend_offline(self) -> None:
        """SandboxAPIClient never crashes when FastAPI is offline and serves session-isolated data."""
        health = self.client.get_health()
        self.assertEqual(health["status"], "ok")
        self.assertEqual(health["connection_mode"], "IN_PROCESS_DIRECT")

        telemetry = self.client.get_telemetry(session_id="ui_tester")
        self.assertEqual(telemetry["session_id"], "ui_tester")
        self.assertGreaterEqual(telemetry["total_tickets"], 3)

        presets = self.client.get_presets()
        self.assertEqual(len(presets), 9)

        tkt = self.client.trigger_preset(
            preset_id="preset_completed_repair_complaint",
            session_id="ui_tester",
        )
        self.assertIsNotNone(tkt)
        self.assertTrue(tkt["decision"]["is_completed_job_recall"])
        self.assertEqual(tkt["decision"]["assigned_sor"], "192005")

        rst = self.client.reset_workspace(session_id="ui_tester")
        self.assertIsNotNone(rst)
        self.assertEqual(rst["status"], "session_reset_complete")

    def test_embedded_mcp_console_tool_runner_and_discovery(self) -> None:
        """Verifies Option 2 Embedded MCP Console discovers primitives and executes tools cleanly."""
        discovered = discover_mcp_primitives()
        self.assertIn("tools", discovered)
        self.assertEqual(len(discovered["tools"]), 4)
        self.assertIn("resources", discovered)
        self.assertIn("templates", discovered)

        res = execute_embedded_mcp_tool(
            "get_latest_triage",
            {"property_id": "prop_oak_01", "session_id": "ui_mcp_test"},
        )
        self.assertEqual(res["tool_called"], "get_latest_triage")
        self.assertIn("result", res)
        self.assertIn("discovered_tools", res)

    def test_all_ui_modules_import_cleanly(self) -> None:
        """Verifies all modular UI views and components import without syntax or circular import errors."""
        import app.ui.components.help_and_presets as hp
        import app.ui.components.kpi_header as kh
        import app.ui.components.mermaid as mm
        import app.ui.components.probability_charts as pc
        import app.ui.dashboard_app as da
        import app.ui.views.landing_page as lp
        import app.ui.views.mcp_console as mc
        import app.ui.views.mcp_guides as mg
        import app.ui.views.product_insights as pi
        import app.ui.views.sandbox_dashboard as sd

        self.assertTrue(callable(da.main))
        self.assertTrue(callable(lp.render_landing_page))
        self.assertTrue(callable(sd.render_sandbox_dashboard_page))
        self.assertTrue(callable(pi.render_product_insights_view))
        self.assertTrue(callable(mc.render_mcp_console_view))
        self.assertTrue(callable(mg.render_claude_cursor_guide))
        self.assertTrue(callable(mg.render_mcp_inspector_guide))
        self.assertTrue(callable(hp.render_help_and_presets_section))
        self.assertTrue(callable(kh.render_kpi_header))
        self.assertTrue(callable(pc.render_ticket_inspection_card))
        self.assertTrue(callable(mm.st_mermaid))


if __name__ == "__main__":
    unittest.main()
