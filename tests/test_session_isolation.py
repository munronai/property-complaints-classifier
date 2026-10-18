"""Unit tests for Zero-DB Multi-User Session Isolation, 48h TTL Pruning, and Protected Admin Resets."""

import time
import unittest

from app.config import settings
from app.domain.enums import IntakeChannel
from app.domain.schemas import ComplaintIntakeRequest
from app.storage.session_store import PermissionDeniedError, SessionStore


class TestSessionIsolationAndSecurity(unittest.TestCase):
    """Verifies Copy-on-First-Access (s_{session_id}_*), TTL pruning, and SANDBOX_ADMIN_KEY protection."""

    def setUp(self) -> None:
        self.store = SessionStore(ttl_seconds=48 * 3600)

    def test_copy_on_first_access_creates_scoped_property_ids(self) -> None:
        """Accessing workspace '4f2a1b' lazily deep-copies Golden Baseline into s_4f2a1b_prop_oak_01."""
        props = self.store.get_properties(session_id="4f2a1b")
        prop_ids = [p.property_id for p in props]
        self.assertIn("s_4f2a1b_prop_oak_01", prop_ids)
        self.assertIn("s_4f2a1b_prop_elm_02", prop_ids)
        self.assertIn("s_4f2a1b_prop_cedar_03", prop_ids)

    def test_multi_user_isolation_prevents_cross_session_interference(self) -> None:
        """Adding a ticket or resetting session 'alice' never mutates session 'bob' or Golden Baseline."""
        alice_initial = len(self.store.get_tickets(session_id="alice"))
        bob_initial = len(self.store.get_tickets(session_id="bob"))
        self.assertEqual(alice_initial, bob_initial)

        req = ComplaintIntakeRequest(
            complaint_text="Cistern ball valve leaking into overflow pipe",
            property_id="prop_oak_01",
            channel=IntakeChannel.DASHBOARD_UI,
            session_id="alice",
        )
        tkt = self.store.orchestrator.process_intake(req)
        self.store.add_ticket(tkt, session_id="alice")

        self.assertEqual(len(self.store.get_tickets(session_id="alice")), alice_initial + 1)
        self.assertEqual(len(self.store.get_tickets(session_id="bob")), bob_initial)

        # Resetting alice only resets s_alice_*
        reset_res = self.store.reset_workspace(session_id="alice", reset_all=False)
        self.assertEqual(reset_res["scope"], "s_alice_*")
        self.assertEqual(len(self.store.get_tickets(session_id="alice")), alice_initial)

    def test_inactive_session_pruning_after_48_hours_ttl(self) -> None:
        """Sessions inactive for > 48 hours are automatically pruned."""
        self.store.get_properties(session_id="stale_user")
        self.store.get_properties(session_id="active_user")

        # Backdate stale_user's last access timestamp by 49 hours
        self.store._session_last_access["stale_user"] = time.time() - (49 * 3600)
        pruned = self.store.prune_expired_sessions()

        self.assertIn("stale_user", pruned)
        self.assertNotIn("stale_user", self.store._session_properties)
        self.assertIn("active_user", self.store._session_properties)

    def test_protected_admin_key_required_for_global_wipe_or_golden_baseline(self) -> None:
        """Global reset (all=True) or resetting golden_baseline requires SANDBOX_ADMIN_KEY."""
        with self.assertRaises(PermissionDeniedError):
            self.store.reset_workspace(session_id="default", reset_all=True, admin_key=None)

        with self.assertRaises(PermissionDeniedError):
            self.store.reset_workspace(session_id="default", reset_all=True, admin_key="wrong-key")

        with self.assertRaises(PermissionDeniedError):
            self.store.reset_workspace(session_id="golden_baseline", reset_all=False, admin_key=None)

        # Succeeds when valid SANDBOX_ADMIN_KEY is provided
        res = self.store.reset_workspace(
            session_id="default",
            reset_all=True,
            admin_key=settings.sandbox_admin_key,
        )
        self.assertEqual(res["status"], "global_reset_complete")


if __name__ == "__main__":
    unittest.main()
