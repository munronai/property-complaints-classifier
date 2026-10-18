"""Zero-Database Multi-User Session Isolation Store (Copy-on-First-Access with 48h TTL pruning)."""

import copy
import time
from typing import Any, Dict, List, Optional

from app.config import settings
from app.domain.enums import (
    IntakeChannel,
    RoutingDestination,
    TicketStatus,
)
from app.domain.presets import GOLDEN_PROPERTIES
from app.domain.schemas import (
    ComplaintIntakeRequest,
    PropertyBaseline,
    TriageTicketRecord,
)
from app.domain.sor_catalog import get_sor_item, reset_sor_catalog_to_base
from app.engine.orchestrator import ComplaintTriageOrchestrator


class PermissionDeniedError(Exception):
    """Raised when a protected baseline or global wipe operation is attempted with an invalid admin key."""


class SessionStore:
    """Manages immutable Golden Baselines and Copy-on-First-Access user session workspaces (s_{session_id}_*)."""

    def __init__(self, ttl_seconds: Optional[int] = None):
        self.ttl_seconds = (
            ttl_seconds if ttl_seconds is not None else settings.session_ttl_seconds
        )
        self.orchestrator = ComplaintTriageOrchestrator()

        # Immutable Golden Baseline Entities & Seed Tickets
        self._golden_properties: Dict[str, PropertyBaseline] = copy.deepcopy(
            GOLDEN_PROPERTIES
        )
        self._golden_tickets: List[TriageTicketRecord] = self._build_golden_baseline_tickets()

        # Session-isolated state keyed by scoped entity ID (e.g., s_{session_id}_prop_oak_01)
        self._session_properties: Dict[str, Dict[str, PropertyBaseline]] = {}
        self._session_tickets: Dict[str, List[TriageTicketRecord]] = {}
        self._session_last_access: Dict[str, float] = {}

    def _build_golden_baseline_tickets(self) -> List[TriageTicketRecord]:
        """Creates the immutable clean baseline tickets representing nominal, low-risk initial state across all 3 properties."""
        seed_requests = [
            ComplaintIntakeRequest(
                complaint_text=(
                    "The toilet cistern in the ground floor washroom won't stop filling up and water is "
                    "trickling down the overflow pipe into the pan. The float ball valve seems stuck."
                ),
                property_id="prop_cedar_03",
                channel=IntakeChannel.DASHBOARD_UI,
                synthetic_image_preset="cistern_valve",
                session_id="golden_baseline",
            ),
            ComplaintIntakeRequest(
                complaint_text=(
                    "Hi, this metal thing snapped off on the kitchen cupboard door today and the door is hanging off, see pic."
                ),
                property_id="prop_elm_02",
                channel=IntakeChannel.WHATSAPP,
                synthetic_image_preset="broken_hinge",
                session_id="golden_baseline",
            ),
            ComplaintIntakeRequest(
                complaint_text=(
                    "The toilet cistern in the main bathroom won't stop filling up and water is "
                    "constantly trickling down the overflow pipe into the pan. The float ball valve seems stuck."
                ),
                property_id="prop_oak_01",
                channel=IntakeChannel.DASHBOARD_UI,
                synthetic_image_preset="cistern_valve",
                session_id="golden_baseline",
            ),
        ]
        tickets: List[TriageTicketRecord] = []
        for idx, req in enumerate(seed_requests, start=1):
            tkt = self.orchestrator.process_intake(req)
            tkt.ticket_id = f"TKT-BASE-0{idx}"
            tickets.append(tkt)
        return tickets

    @staticmethod
    def format_scoped_property_id(session_id: str, property_id: str) -> str:
        """Formats a property ID into its session-isolated form: s_{session_id}_{property_id}."""
        if not session_id or session_id == "golden_baseline":
            return property_id
        prefix = f"s_{session_id}_"
        if property_id.startswith(prefix):
            return property_id
        return f"{prefix}{property_id}"

    @staticmethod
    def strip_session_prefix(session_id: str, scoped_id: str) -> str:
        """Extracts the canonical property ID from a session-scoped ID."""
        prefix = f"s_{session_id}_"
        if scoped_id.startswith(prefix):
            return scoped_id[len(prefix) :]
        return scoped_id

    def prune_expired_sessions(self, now: Optional[float] = None) -> List[str]:
        """Discards session entities inactive for > 48 hours (ttl_seconds) to prevent cloud storage leaks."""
        current_time = now if now is not None else time.time()
        expired_sessions = [
            sid
            for sid, last_seen in self._session_last_access.items()
            if (current_time - last_seen) > self.ttl_seconds
        ]
        for sid in expired_sessions:
            self._session_properties.pop(sid, None)
            self._session_tickets.pop(sid, None)
            self._session_last_access.pop(sid, None)
        return expired_sessions

    def _ensure_session_initialized(self, session_id: str) -> str:
        """Lazily deep-copies the immutable Golden Baseline into s_{session_id}_* on first access."""
        self.prune_expired_sessions()
        norm_sid = (session_id or "default").strip() or "default"
        self._session_last_access[norm_sid] = time.time()

        if norm_sid not in self._session_properties:
            scoped_props: Dict[str, PropertyBaseline] = {}
            for base_id, prop in self._golden_properties.items():
                scoped_key = self.format_scoped_property_id(norm_sid, base_id)
                copied_prop = copy.deepcopy(prop)
                copied_prop.property_id = scoped_key
                scoped_props[scoped_key] = copied_prop
            self._session_properties[norm_sid] = scoped_props

            scoped_tickets: List[TriageTicketRecord] = []
            for base_tkt in self._golden_tickets:
                copied_tkt = copy.deepcopy(base_tkt)
                copied_tkt.session_id = norm_sid
                copied_tkt.property_id = self.format_scoped_property_id(
                    norm_sid, base_tkt.property_id
                )
                scoped_tickets.append(copied_tkt)
            self._session_tickets[norm_sid] = scoped_tickets

        return norm_sid

    def get_properties(self, session_id: str = "default") -> List[PropertyBaseline]:
        """Returns the session-isolated properties for the given session_id."""
        norm_sid = self._ensure_session_initialized(session_id)
        return list(self._session_properties[norm_sid].values())

    def get_tickets(
        self,
        session_id: str = "default",
        property_id: Optional[str] = None,
    ) -> List[TriageTicketRecord]:
        """Returns session-isolated tickets (newest first), optionally filtered by property_id."""
        norm_sid = self._ensure_session_initialized(session_id)
        tickets = self._session_tickets[norm_sid]
        if property_id:
            scoped_prop_id = self.format_scoped_property_id(norm_sid, property_id)
            tickets = [
                t
                for t in tickets
                if t.property_id in (property_id, scoped_prop_id)
            ]
        return list(reversed(tickets))

    def get_latest_ticket_for_property(
        self,
        property_id: str,
        session_id: str = "default",
    ) -> Optional[TriageTicketRecord]:
        """Returns the most recent triage ticket for a property (or from Golden Baseline if golden ID used)."""
        if property_id in self._golden_properties and session_id == "golden_baseline":
            matching = [
                t for t in self._golden_tickets if t.property_id == property_id
            ]
            return matching[-1] if matching else None

        tickets = self.get_tickets(session_id=session_id, property_id=property_id)
        return tickets[0] if tickets else None

    def add_ticket(
        self,
        ticket: TriageTicketRecord,
        session_id: Optional[str] = None,
    ) -> TriageTicketRecord:
        """Persists a newly evaluated TriageTicketRecord into the session-isolated store."""
        target_sid = self._ensure_session_initialized(
            session_id or ticket.session_id or "default"
        )
        ticket.session_id = target_sid
        ticket.property_id = self.format_scoped_property_id(
            target_sid, ticket.property_id
        )
        self._session_tickets[target_sid].append(ticket)
        return ticket

    def approve_or_override_ticket(
        self,
        ticket_id: str,
        session_id: str = "default",
        override_sor: Optional[str] = None,
        surveyor_notes: Optional[str] = None,
    ) -> TriageTicketRecord:
        """Allows a human surveyor or authorized MCP agent to approve or override an escalated ticket's SOR."""
        norm_sid = self._ensure_session_initialized(session_id)
        for ticket in self._session_tickets[norm_sid]:
            if ticket.ticket_id == ticket_id:
                if override_sor:
                    ticket.surveyor_override_sor = override_sor
                    ticket.decision.assigned_sor = override_sor
                    sor_item = get_sor_item(override_sor)
                    if sor_item:
                        ticket.decision.assigned_sor_description = (
                            sor_item.short_description
                        )
                    ticket.status = TicketStatus.SURVEYOR_OVERRIDDEN
                else:
                    ticket.status = TicketStatus.SURVEYOR_APPROVED
                ticket.decision.auto_approve = True
                if surveyor_notes:
                    ticket.surveyor_notes = surveyor_notes
                return ticket
        raise KeyError(f"Ticket '{ticket_id}' not found in session '{norm_sid}'.")

    def compute_telemetry(self, session_id: str = "default") -> Dict[str, Any]:
        """Computes real-time KPI metrics across the active user session workspace."""
        norm_sid = self._ensure_session_initialized(session_id)
        tickets = self._session_tickets[norm_sid]
        total = len(tickets)
        if total == 0:
            return {
                "session_id": norm_sid,
                "total_tickets": 0,
                "auto_dispatch_count": 0,
                "auto_dispatch_rate": 0.0,
                "awaabs_law_intercepts": 0,
                "emergency_escalations": 0,
                "wip_and_finance_reroutes": 0,
                "completed_job_recalls": 0,
                "inappropriate_discards": 0,
                "surveyor_review_queue": 0,
                "mean_trade_confidence": 0.0,
                "mean_sor_confidence": 0.0,
            }

        auto_count = sum(
            1
            for t in tickets
            if t.decision.destination == RoutingDestination.AUTO_DISPATCH_HMS
        )
        awaabs_count = sum(
            1
            for t in tickets
            if t.decision.destination == RoutingDestination.DISREPAIR_LEGAL_TEAM
        )
        emergency_count = sum(
            1
            for t in tickets
            if t.decision.destination == RoutingDestination.OUT_OF_HOURS_DUTY_OFFICER
        )
        reroute_count = sum(
            1
            for t in tickets
            if t.decision.destination
            in (
                RoutingDestination.CUSTOMER_SERVICE_WIP_DESK,
                RoutingDestination.CONTRACTOR_FINANCE_DESK,
            )
        )
        recall_count = sum(
            1
            for t in tickets
            if t.decision.destination
            == RoutingDestination.QUALITY_RECALL_SURVEYOR_REVIEW
        )
        discard_count = sum(
            1
            for t in tickets
            if t.decision.destination
            == RoutingDestination.DISCARDED_INAPPROPRIATE_CONTENT
        )
        surveyor_count = sum(
            1
            for t in tickets
            if t.decision.destination == RoutingDestination.SURVEYOR_DESK_REVIEW
        )

        trade_probs = [
            float(t.decision.metadata.get("trade_prob", 0.0))
            for t in tickets
            if t.decision.metadata.get("trade_prob", 0.0) > 0
        ]
        sor_probs = [
            float(t.decision.metadata.get("sor_prob", 0.0))
            for t in tickets
            if t.decision.metadata.get("sor_prob", 0.0) > 0
        ]

        return {
            "session_id": norm_sid,
            "total_tickets": total,
            "auto_dispatch_count": auto_count,
            "auto_dispatch_rate": round(auto_count / total, 4),
            "awaabs_law_intercepts": awaabs_count,
            "emergency_escalations": emergency_count,
            "wip_and_finance_reroutes": reroute_count,
            "completed_job_recalls": recall_count,
            "inappropriate_discards": discard_count,
            "surveyor_review_queue": surveyor_count,
            "mean_trade_confidence": (
                round(sum(trade_probs) / len(trade_probs), 4) if trade_probs else 0.0
            ),
            "mean_sor_confidence": (
                round(sum(sor_probs) / len(sor_probs), 4) if sor_probs else 0.0
            ),
            "active_sessions_count": len(self._session_properties),
        }

    def reset_workspace(
        self,
        session_id: str = "default",
        reset_all: bool = False,
        admin_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Resets either a single user session workspace (unrestricted) or all workspaces + baseline (protected)."""
        is_protected_target = reset_all or session_id in (
            "golden_baseline",
            "prop_oak_01",
            "prop_elm_02",
            "prop_cedar_03",
        )
        if is_protected_target:
            if not admin_key or admin_key != settings.sandbox_admin_key:
                raise PermissionDeniedError(
                    "Resetting the shared Golden Baseline or performing a global wipe (all=true) "
                    "strictly requires a valid SANDBOX_ADMIN_KEY in the JSON POST body."
                )
            catalog_reset = reset_sor_catalog_to_base()
            self._session_properties.clear()
            self._session_tickets.clear()
            self._session_last_access.clear()
            self._golden_properties = copy.deepcopy(GOLDEN_PROPERTIES)
            self._golden_tickets = self._build_golden_baseline_tickets()
            return {
                "status": "global_reset_complete",
                "scope": "all_sessions_and_golden_baseline",
                "sor_catalog_reset": catalog_reset,
            }

        catalog_reset = reset_sor_catalog_to_base()
        norm_sid = (session_id or "default").strip() or "default"
        self._session_properties.pop(norm_sid, None)
        self._session_tickets.pop(norm_sid, None)
        self._session_last_access.pop(norm_sid, None)
        self._ensure_session_initialized(norm_sid)
        return {
            "status": "session_reset_complete",
            "scope": f"s_{norm_sid}_*",
            "session_id": norm_sid,
            "sor_catalog_reset": catalog_reset,
        }


# Singleton session store instance
session_store = SessionStore()
