"""Unit tests for TriageEscalationGuard covering all safety, intent, statutory, and confidence circuit breakers."""

import unittest

from app.domain.enums import EscalationReason, MessageIntent, RoutingDestination
from app.engine.escalation_guard import TriageEscalationGuard


class TestTriageEscalationGuard(unittest.TestCase):
    """Verifies all gating and re-routing conditions in TriageEscalationGuard."""

    def setUp(self) -> None:
        self.guard = TriageEscalationGuard(
            min_trade_confidence=0.70,
            min_sor_confidence=0.65,
            min_probability_margin=0.15,
            damp_hazard_threshold=0.40,
            inappropriate_content_threshold=0.50,
        )

    def test_clean_auto_approve_plumbing(self) -> None:
        """High confidence trade & SOR with clear margin and no statutory risk auto-dispatches to HMS."""
        s1 = {
            "answers": {
                "inappropriate_content_flag": {"value": False, "probability": 0.01},
                "message_intent": {"value": "NEW_REPAIR_DEFECT", "probability": 0.94},
                "primary_trade": {"value": "PLUM", "probability": 0.88},
                "awaabs_law_damp_hazard": {"value": False, "probability": 0.05},
                "repair_priority": {"value": "2", "probability": 0.91},
            }
        }
        s2 = {
            "answers": {
                "selected_sor": {
                    "value": "114010",
                    "probability": 0.86,
                    "distribution": {"114010": 0.86, "112001": 0.08, "OTHER": 0.06},
                }
            }
        }
        res = self.guard.evaluate(s1, s2)
        self.assertTrue(res.auto_approve)
        self.assertEqual(res.destination, RoutingDestination.AUTO_DISPATCH_HMS)
        self.assertEqual(res.assigned_trade, "PLUM")
        self.assertEqual(res.assigned_sor, "114010")
        self.assertEqual(res.reasons, [])
        self.assertFalse(res.discard_media)

    def test_ambiguous_sor_margin_and_low_sor_confidence(self) -> None:
        """Top-1 (0.54) minus Top-2 (0.44) = 0.10 < 0.15 triggers AMBIGUOUS_SOR_MARGIN and LOW_SOR_CONFIDENCE."""
        s1 = {
            "answers": {
                "primary_trade": {"value": "PLUM", "probability": 0.88},
                "awaabs_law_damp_hazard": {"value": False, "probability": 0.08},
                "repair_priority": {"value": "2", "probability": 0.92},
            }
        }
        s2 = {
            "answers": {
                "selected_sor": {
                    "value": "112001",
                    "probability": 0.54,
                    "distribution": {"112001": 0.54, "112005": 0.44, "OTHER": 0.02},
                }
            }
        }
        res = self.guard.evaluate(s1, s2)
        self.assertFalse(res.auto_approve)
        self.assertEqual(res.destination, RoutingDestination.SURVEYOR_DESK_REVIEW)
        self.assertIn(EscalationReason.LOW_SOR_CONFIDENCE, res.reasons)
        self.assertIn(EscalationReason.AMBIGUOUS_SOR_MARGIN, res.reasons)
        self.assertAlmostEqual(res.metadata["sor_margin"], 0.10, places=3)

    def test_awaabs_law_damp_hazard_override(self) -> None:
        """Awaab's Law damp probability >= 0.40 forces escalation to DISREPAIR_LEGAL_TEAM."""
        s1 = {
            "answers": {
                "primary_trade": {"value": "DAMP", "probability": 0.92},
                "awaabs_law_damp_hazard": {"value": True, "probability": 0.85},
                "repair_priority": {"value": "2", "probability": 0.89},
            }
        }
        s2 = {
            "answers": {
                "selected_sor": {
                    "value": "241001",
                    "probability": 0.87,
                    "distribution": {"241001": 0.87, "241010": 0.10, "OTHER": 0.03},
                }
            }
        }
        res = self.guard.evaluate(s1, s2)
        self.assertFalse(res.auto_approve)
        self.assertEqual(res.destination, RoutingDestination.DISREPAIR_LEGAL_TEAM)
        self.assertIn(EscalationReason.AWAABS_LAW_RISK, res.reasons)

    def test_emergency_priority_3_escalation(self) -> None:
        """Priority level 3 routes to OUT_OF_HOURS_DUTY_OFFICER."""
        s1 = {
            "answers": {
                "primary_trade": {"value": "ELEC", "probability": 0.90},
                "awaabs_law_damp_hazard": {"value": False, "probability": 0.05},
                "repair_priority": {"value": "3", "probability": 0.95},
            }
        }
        s2 = {
            "answers": {
                "selected_sor": {
                    "value": "611001",
                    "probability": 0.91,
                    "distribution": {"611001": 0.91, "612015": 0.06, "OTHER": 0.03},
                }
            }
        }
        res = self.guard.evaluate(s1, s2)
        self.assertFalse(res.auto_approve)
        self.assertEqual(res.destination, RoutingDestination.OUT_OF_HOURS_DUTY_OFFICER)
        self.assertIn(EscalationReason.EMERGENCY_ESCALATION, res.reasons)

    def test_inappropriate_content_flags_and_discards_media(self) -> None:
        """Inappropriate photo/text triggers INAPPROPRIATE_CONTENT_DETECTED and sets discard_media=True."""
        s1 = {
            "answers": {
                "inappropriate_content_flag": {"value": True, "probability": 0.96},
                "primary_trade": {"value": "OTHER", "probability": 0.80},
                "awaabs_law_damp_hazard": {"value": False, "probability": 0.01},
                "repair_priority": {"value": "1", "probability": 0.90},
            }
        }
        res = self.guard.evaluate(s1, None)
        self.assertFalse(res.auto_approve)
        self.assertTrue(res.discard_media)
        self.assertEqual(res.destination, RoutingDestination.DISCARDED_INAPPROPRIATE_CONTENT)
        self.assertEqual(res.reasons, [EscalationReason.INAPPROPRIATE_CONTENT_DETECTED])

    def test_wip_repair_update_and_scheduling_reroute(self) -> None:
        """WIP repair updates and contractor scheduling requests route to CUSTOMER_SERVICE_WIP_DESK."""
        s1 = {
            "answers": {
                "message_intent": {"value": MessageIntent.WIP_REPAIR_UPDATE.value, "probability": 0.91},
                "primary_trade": {"value": "PLAS", "probability": 0.82},
                "awaabs_law_damp_hazard": {"value": False, "probability": 0.02},
                "repair_priority": {"value": "1", "probability": 0.88},
            }
        }
        res = self.guard.evaluate(s1, None)
        self.assertFalse(res.auto_approve)
        self.assertEqual(res.destination, RoutingDestination.CUSTOMER_SERVICE_WIP_DESK)
        self.assertIn(EscalationReason.REPAIR_UPDATE_OR_SCHEDULING, res.reasons)
        self.assertIsNone(res.assigned_sor)

    def test_contractor_payment_inquiry_reroute(self) -> None:
        """Late payment inquiries route to CONTRACTOR_FINANCE_DESK without raising works orders."""
        s1 = {
            "answers": {
                "message_intent": {"value": MessageIntent.CONTRACTOR_PAYMENT_INQUIRY.value, "probability": 0.95},
                "primary_trade": {"value": "OTHER", "probability": 0.40},
                "awaabs_law_damp_hazard": {"value": False, "probability": 0.01},
                "repair_priority": {"value": "1", "probability": 0.90},
            }
        }
        res = self.guard.evaluate(s1, None)
        self.assertFalse(res.auto_approve)
        self.assertEqual(res.destination, RoutingDestination.CONTRACTOR_FINANCE_DESK)
        self.assertIn(EscalationReason.NON_REPAIR_FINANCE_QUERY, res.reasons)

    def test_completed_repair_complaint_assesses_sor_and_routes_to_recall(self) -> None:
        """Complaints about completed repair jobs keep their assessed M3NHF SOR code and route to recall review."""
        s1 = {
            "answers": {
                "message_intent": {"value": MessageIntent.COMPLETED_REPAIR_COMPLAINT.value, "probability": 0.93},
                "primary_trade": {"value": "PLUM", "probability": 0.89},
                "awaabs_law_damp_hazard": {"value": False, "probability": 0.06},
                "repair_priority": {"value": "2", "probability": 0.90},
            }
        }
        s2 = {
            "answers": {
                "selected_sor": {
                    "value": "112005",
                    "probability": 0.84,
                    "distribution": {"112005": 0.84, "112001": 0.11, "OTHER": 0.05},
                }
            }
        }
        res = self.guard.evaluate(s1, s2)
        self.assertFalse(res.auto_approve)
        self.assertTrue(res.is_completed_job_recall)
        self.assertEqual(res.destination, RoutingDestination.QUALITY_RECALL_SURVEYOR_REVIEW)
        self.assertEqual(res.assigned_trade, "PLUM")
        self.assertEqual(res.assigned_sor, "112005")
        self.assertIn(EscalationReason.POST_REPAIR_QUALITY_COMPLAINT, res.reasons)


if __name__ == "__main__":
    unittest.main()
