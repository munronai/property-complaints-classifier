"""Unit and headless integration tests for Pillar 3 Modular Streamlit UI components and views."""

import unittest

from app.ui.api_client import SandboxAPIClient
from app.ui.views.mcp_console import execute_embedded_mcp_tool


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
        self.assertEqual(tkt["decision"]["assigned_sor"], "112005")

    def test_embedded_mcp_console_tool_runner(self) -> None:
        """Verifies Option 2 Embedded MCP Console executes tools and returns structured JSON."""
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
        import app.ui.components.probability_charts as pc
        import app.ui.components.threshold_sidebar as ts
        import app.ui.dashboard_app as da
        import app.ui.views.landing_page as lp
        import app.ui.views.live_intake as li
        import app.ui.views.mcp_console as mc
        import app.ui.views.product_insights as pi
        import app.ui.views.surveyor_desk as sd
        import app.ui.views.time_machine as tm

        self.assertTrue(callable(da.main))
        self.assertTrue(callable(lp.render_landing_page))
        self.assertTrue(callable(pi.render_product_insights_view))
        self.assertTrue(callable(li.render_live_intake_view))
        self.assertTrue(callable(tm.render_time_machine_view))
        self.assertTrue(callable(sd.render_surveyor_desk_view))
        self.assertTrue(callable(mc.render_mcp_console_view))
        self.assertTrue(callable(hp.render_help_and_presets_section))
        self.assertTrue(callable(kh.render_kpi_header))
        self.assertTrue(callable(pc.render_ticket_inspection_card))
        self.assertTrue(callable(ts.render_sidebar))


if __name__ == "__main__":
    unittest.main()
