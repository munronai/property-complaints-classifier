"""Unit tests for Pillow image normalization, Live TypeSafe Jev client schemas, and the 9 Scenario Presets."""

import io
import unittest
from unittest.mock import MagicMock, patch
from PIL import Image

from app.domain.enums import EscalationReason, RoutingDestination
from app.domain.presets import SCENARIO_PRESETS
from app.domain.schemas import ComplaintIntakeRequest
from app.engine.image_normalizer import (
    MAX_JEV_IMAGE_EDGE,
    generate_synthetic_defect_image,
    prepare_image_for_jev,
)
from app.engine.jev_client import JevRepairsTriageEngine
from app.engine.orchestrator import ComplaintTriageOrchestrator


class TestImageNormalizationAndJevEngine(unittest.TestCase):
    """Tests multimodal image preparation, Jev protocol formatting, and end-to-end preset orchestration."""

    def test_oversized_rgba_image_is_resized_to_1568px_and_converted_to_rgb(self) -> None:
        """Images larger than 1568px along their longest edge are scaled down to <=1568px and saved as JPEG."""
        large_img = Image.new("RGBA", (2400, 1800), color=(120, 160, 200, 255))
        b64_str, mime, telemetry = prepare_image_for_jev(large_img)

        self.assertEqual(mime, "image/jpeg")
        self.assertTrue(len(b64_str) > 100)
        self.assertTrue(telemetry.resized)
        self.assertEqual(telemetry.original_width, 2400)
        self.assertEqual(telemetry.original_height, 1800)
        self.assertEqual(telemetry.normalized_width, MAX_JEV_IMAGE_EDGE)
        self.assertLessEqual(telemetry.normalized_height, MAX_JEV_IMAGE_EDGE)

    def test_exif_rotated_image_is_transposed_upright(self) -> None:
        """An image with EXIF Orientation=6 (90 deg CW) is transposed upright during normalization."""
        raw_img = Image.new("RGB", (600, 400), color=(200, 100, 50))
        exif = raw_img.getexif()
        exif[0x0112] = 6  # Rotate 90 CW -> transposed dimensions should become 400x600
        buf = io.BytesIO()
        raw_img.save(buf, format="JPEG", exif=exif.tobytes())

        _, _, telemetry = prepare_image_for_jev(buf.getvalue())
        self.assertTrue(telemetry.exif_transposed)
        self.assertEqual(telemetry.normalized_width, 400)
        self.assertEqual(telemetry.normalized_height, 600)

    def test_live_jev_client_sets_danger_zone_header_and_assets_table(self) -> None:
        """Verifies JevRepairsTriageEngine attaches TypeSafe-Danger-Zone-Images: true and assets map."""
        engine = JevRepairsTriageEngine(api_key="test-jev-key-123")
        self.assertEqual(
            engine.session.headers.get("TypeSafe-Danger-Zone-Images"), "true"
        )
        self.assertEqual(
            engine.session.headers.get("Authorization"), "Bearer test-jev-key-123"
        )

        sample_bytes = generate_synthetic_defect_image("black_mould")
        mock_response = MagicMock()
        mock_response.json.return_value = {"answers": {"primary_trade": {"value": "DAMP", "probability": 0.91}}}

        with patch.object(engine.session, "post", return_value=mock_response) as mock_post:
            engine.triage_complaint(
                complaint_text="Black mould on bedroom wall",
                image_source=sample_bytes,
            )
            mock_post.assert_called_once()
            _, kwargs = mock_post.call_args
            payload = kwargs["json"]
            self.assertIn("assets", payload)
            self.assertIn("attached_evidence", payload["state"])
            asset_key = payload["state"]["attached_evidence"]
            self.assertIn(asset_key, payload["assets"])
            self.assertEqual(payload["assets"][asset_key]["format"], "image/jpeg")

    def test_all_nine_scenario_presets_match_expected_destinations_and_reasons(self) -> None:
        """Runs all 9 Time-Machine Scenario Presets through ComplaintTriageOrchestrator and validates outcomes."""
        orchestrator = ComplaintTriageOrchestrator()

        for preset in SCENARIO_PRESETS:
            with self.subTest(preset_id=preset.preset_id):
                req = ComplaintIntakeRequest(
                    complaint_text=preset.complaint_text,
                    property_id=preset.property_id,
                    channel=preset.channel,
                    synthetic_image_preset=preset.synthetic_image_preset,
                    existing_job_ref=preset.existing_job_ref,
                )
                ticket = orchestrator.process_intake(req)

                self.assertEqual(
                    ticket.decision.destination,
                    preset.expected_destination,
                    f"Destination mismatch for {preset.preset_id}",
                )
                for expected_reason in preset.expected_reasons:
                    self.assertIn(
                        expected_reason,
                        ticket.decision.reasons,
                        f"Missing expected reason {expected_reason} for {preset.preset_id}",
                    )

                # Verify media purge behavior on Preset 9 (inappropriate content)
                if preset.preset_id == "preset_inappropriate_content_discard":
                    self.assertTrue(ticket.media_discarded)
                    self.assertIsNone(ticket.normalized_image_base64)
                    self.assertIsNone(ticket.stage2_output)
                    self.assertIn(
                        EscalationReason.INAPPROPRIATE_CONTENT_DETECTED,
                        ticket.decision.reasons,
                    )

                # Verify completed repair complaint (Preset 8) runs Stage 2 SOR resolution
                if preset.preset_id == "preset_completed_repair_complaint":
                    self.assertIsNotNone(ticket.stage2_output)
                    self.assertEqual(ticket.decision.assigned_trade, "PLUM")
                    self.assertEqual(ticket.decision.assigned_sor, "112005")
                    self.assertTrue(ticket.decision.is_completed_job_recall)


if __name__ == "__main__":
    unittest.main()
