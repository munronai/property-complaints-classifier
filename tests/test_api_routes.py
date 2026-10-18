"""Integration tests for Pillar 1 Modular FastAPI routers (Complaints, WhatsApp Webhook, Simulation, Surveyor, Admin)."""

import unittest
from fastapi.testclient import TestClient

from app.api.main import app
from app.config import settings
from app.domain.enums import RoutingDestination, TicketStatus


class TestModularFastAPIRoutes(unittest.TestCase):
    """Tests all REST API endpoints under /api/v1."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_health_and_catalog_endpoints(self) -> None:
        """Verifies /api/v1/health and /api/v1/catalog return structured schemas."""
        health_resp = self.client.get("/api/v1/health")
        self.assertEqual(health_resp.status_code, 200)
        health_data = health_resp.json()
        self.assertEqual(health_data["status"], "ok")
        self.assertIn("default_thresholds", health_data)

        cat_resp = self.client.get("/api/v1/catalog")
        self.assertEqual(cat_resp.status_code, 200)
        cat_data = cat_resp.json()
        self.assertIn("PLUM", cat_data["m3nhf_catalog"])
        self.assertIn("COMPLETED_REPAIR_COMPLAINT", cat_data["message_intent_criteria"])

    def test_complaint_triage_and_whatsapp_webhook(self) -> None:
        """Tests POST /api/v1/complaints/triage and POST /api/v1/webhooks/whatsapp."""
        # 1. Dashboard UI complaint intake
        triage_resp = self.client.post(
            "/api/v1/complaints/triage",
            json={
                "complaint_text": "Toilet cistern ball valve stuck and overflowing continuously",
                "property_id": "prop_oak_01",
                "channel": "DASHBOARD_UI",
                "synthetic_image_preset": "cistern_valve",
                "session_id": "api_test_user",
            },
        )
        self.assertEqual(triage_resp.status_code, 200)
        tkt = triage_resp.json()
        self.assertTrue(tkt["decision"]["auto_approve"])
        self.assertEqual(tkt["decision"]["assigned_sor"], "194010")
        self.assertEqual(tkt["property_id"], "s_api_test_user_prop_oak_01")

        # 2. WhatsApp Webhook for a Completed Repair Job Quality Complaint
        wa_resp = self.client.post(
            "/api/v1/webhooks/whatsapp",
            json={
                "from_phone": "+447700900555",
                "property_id": "prop_oak_01",
                "message_body": (
                    "Your plumber came out yesterday and marked JOB-77210 completed, "
                    "but the push-fit waste trap under the sink is still leaking!"
                ),
                "synthetic_image_preset": "sink_leak",
                "existing_job_ref": "JOB-77210",
                "session_id": "api_test_user",
            },
        )
        self.assertEqual(wa_resp.status_code, 200)
        wa_tkt = wa_resp.json()
        self.assertEqual(wa_tkt["channel"], "WHATSAPP")
        self.assertTrue(wa_tkt["decision"]["is_completed_job_recall"])
        self.assertEqual(wa_tkt["decision"]["assigned_sor"], "192005")
        self.assertEqual(
            wa_tkt["decision"]["destination"],
            RoutingDestination.QUALITY_RECALL_SURVEYOR_REVIEW.value,
        )

        # 3. Twilio WhatsApp Form Webhook returning TwiML
        twilio_resp = self.client.post(
            "/api/v1/webhooks/whatsapp/twilio?session=api_test_user",
            data={
                "From": "whatsapp:+447700900123",
                "Body": "Water is leaking through ceiling rose! #oak",
                "NumMedia": "0",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(twilio_resp.status_code, 200)
        self.assertIn("application/xml", twilio_resp.headers["content-type"])
        self.assertIn("<Response>", twilio_resp.text)
        self.assertIn("<Message>", twilio_resp.text)
        self.assertIn("Ref:", twilio_resp.text)

    def test_simulate_preset_and_surveyor_override(self) -> None:
        """Tests POST /api/v1/simulate and POST /api/v1/tickets/{ticket_id}/approve."""
        sim_resp = self.client.post(
            "/api/v1/simulate",
            json={
                "preset_id": "preset_ambiguous_margin",
                "session_id": "surveyor_test",
            },
        )
        self.assertEqual(sim_resp.status_code, 200)
        sim_tkt = sim_resp.json()
        ticket_id = sim_tkt["ticket_id"]
        self.assertFalse(sim_tkt["decision"]["auto_approve"])
        self.assertEqual(
            sim_tkt["decision"]["destination"],
            RoutingDestination.SURVEYOR_DESK_REVIEW.value,
        )

        # Surveyor overrides SOR from 192001 to 192005 and approves
        approve_resp = self.client.post(
            f"/api/v1/tickets/{ticket_id}/approve",
            json={
                "session_id": "surveyor_test",
                "override_sor": "192005",
                "surveyor_notes": "Confirmed push-fit waste trap leak from photo; dispatching 192005.",
            },
        )
        self.assertEqual(approve_resp.status_code, 200)
        updated = approve_resp.json()
        self.assertTrue(updated["decision"]["auto_approve"])
        self.assertEqual(updated["decision"]["assigned_sor"], "192005")
        self.assertEqual(updated["status"], TicketStatus.SURVEYOR_OVERRIDDEN.value)

    def test_reset_endpoint_enforces_admin_key_for_global_wipe(self) -> None:
        """Verifies /api/v1/reset allows session resets and requires admin_key in JSON body for all=True."""
        # Unrestricted session reset
        ok_resp = self.client.post(
            "/api/v1/reset",
            json={"session_id": "api_test_user", "all": False},
        )
        self.assertEqual(ok_resp.status_code, 200)

        # Protected global wipe without admin_key -> HTTP 403
        forbidden_resp = self.client.post(
            "/api/v1/reset",
            json={"session_id": "default", "all": True},
        )
        self.assertEqual(forbidden_resp.status_code, 403)

        # Protected global wipe with valid admin_key -> HTTP 200
        admin_resp = self.client.post(
            "/api/v1/reset",
            json={
                "session_id": "default",
                "all": True,
                "admin_key": settings.sandbox_admin_key,
            },
        )
        self.assertEqual(admin_resp.status_code, 200)
        self.assertEqual(admin_resp.json()["status"], "global_reset_complete")


if __name__ == "__main__":
    unittest.main()
