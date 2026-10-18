"""End-to-end multimodal triage orchestrator coordinating Image Prep, Jev Pass 1 & 2, and Gating Guard."""

import uuid
from typing import Any, Dict, Optional

from app.config import settings
from app.domain.enums import (
    EngineMode,
    MessageIntent,
    RoutingDestination,
    TicketStatus,
)
from app.domain.presets import GOLDEN_PROPERTIES, SCENARIO_PRESETS
from app.domain.schemas import (
    ComplaintIntakeRequest,
    GatingThresholds,
    ImageTelemetry,
    TriageTicketRecord,
)
from app.domain.sor_catalog import get_candidate_sors_for_trade
from app.engine.escalation_guard import TriageEscalationGuard
from app.engine.image_normalizer import (
    generate_synthetic_defect_image,
    prepare_image_for_jev,
)
from app.engine.jev_client import JevRepairsTriageEngine
from app.engine.simulator import SimulatedJevEngine


DESTINATION_TO_TICKET_STATUS: Dict[RoutingDestination, TicketStatus] = {
    RoutingDestination.AUTO_DISPATCH_HMS: TicketStatus.AUTO_DISPATCHED,
    RoutingDestination.SURVEYOR_DESK_REVIEW: TicketStatus.PENDING_SURVEYOR_REVIEW,
    RoutingDestination.QUALITY_RECALL_SURVEYOR_REVIEW: TicketStatus.PENDING_RECALL_INSPECTION,
    RoutingDestination.CUSTOMER_SERVICE_WIP_DESK: TicketStatus.REROUTED_WIP_DESK,
    RoutingDestination.CONTRACTOR_FINANCE_DESK: TicketStatus.REROUTED_FINANCE_DESK,
    RoutingDestination.DISREPAIR_LEGAL_TEAM: TicketStatus.ESCALATED_LEGAL_AWAABS,
    RoutingDestination.OUT_OF_HOURS_DUTY_OFFICER: TicketStatus.ESCALATED_EMERGENCY_OOH,
    RoutingDestination.DISCARDED_INAPPROPRIATE_CONTENT: TicketStatus.DISCARDED_MODERATION,
}


class ComplaintTriageOrchestrator:
    """Coordinates multimodal image normalization, Pass 1 & Pass 2 Jev evaluation, and circuit-breaker gating."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.typesafe_api_key
        self.simulator = SimulatedJevEngine()

    def process_intake(
        self,
        request: ComplaintIntakeRequest,
        thresholds: Optional[GatingThresholds] = None,
    ) -> TriageTicketRecord:
        """Executes the two-stage pipeline with short-circuiting for content safety and WIP/finance re-routes."""
        active_thresholds = thresholds or request.thresholds or GatingThresholds(
            min_trade_confidence=settings.min_trade_confidence,
            min_sor_confidence=settings.min_sor_confidence,
            min_probability_margin=settings.min_probability_margin,
            damp_hazard_threshold=settings.damp_hazard_threshold,
            inappropriate_content_threshold=settings.inappropriate_content_threshold,
        )
        guard = TriageEscalationGuard.from_thresholds(active_thresholds)

        # 1. Resolve & normalize image if provided (either base64 upload or synthetic preset)
        raw_image_source: Optional[Any] = None
        if request.image_base64:
            raw_image_source = request.image_base64
        elif request.synthetic_image_preset:
            raw_image_source = generate_synthetic_defect_image(request.synthetic_image_preset)

        normalized_b64: Optional[str] = None
        image_telemetry: Optional[ImageTelemetry] = None
        if raw_image_source is not None:
            normalized_b64, _, image_telemetry = prepare_image_for_jev(raw_image_source)

        # 2. Execute Pass 1 (Content Safety, Message Intent, Trade, Awaab's Law, SLA Priority)
        use_live = (
            request.engine_mode == EngineMode.LIVE and bool(self.api_key)
        )
        if use_live:
            live_client = JevRepairsTriageEngine(api_key=self.api_key)
            stage1_output = live_client.triage_complaint(
                complaint_text=request.complaint_text,
                image_source=raw_image_source,
                existing_job_ref=request.existing_job_ref,
            )
        else:
            stage1_output = self.simulator.triage_complaint(
                complaint_text=request.complaint_text,
                synthetic_image_preset=request.synthetic_image_preset,
                has_image=(raw_image_source is not None),
                existing_job_ref=request.existing_job_ref,
            )

        answers_s1 = stage1_output.get("answers", {})

        # 3. Determine whether Stage 2 M3NHF SOR Resolution should run or short-circuit
        inappropriate_ans = answers_s1.get("inappropriate_content_flag", {})
        is_inappropriate = bool(inappropriate_ans.get("value", False)) or (
            float(inappropriate_ans.get("probability", 0.0))
            >= active_thresholds.inappropriate_content_threshold
        )

        intent_val = answers_s1.get("message_intent", {}).get(
            "value", MessageIntent.NEW_REPAIR_DEFECT.value
        )
        trade_val = answers_s1.get("primary_trade", {}).get("value", "OTHER")

        stage2_output: Optional[Dict[str, Any]] = None
        stage2_skipped_reason: Optional[str] = None

        if is_inappropriate:
            stage2_skipped_reason = (
                "Short-circuited Stage 2: Inappropriate content detected in Stage 1; media purged."
            )
        elif intent_val in (
            MessageIntent.WIP_REPAIR_UPDATE.value,
            MessageIntent.CONTRACTOR_SCHEDULING.value,
            MessageIntent.CONTRACTOR_PAYMENT_INQUIRY.value,
        ):
            stage2_skipped_reason = (
                f"Short-circuited Stage 2: Message intent '{intent_val}' re-routed without raising a new SOR order."
            )
        elif trade_val == "OTHER" or not trade_val:
            stage2_skipped_reason = (
                "Short-circuited Stage 2: Primary trade classified as OTHER (out of M3NHF repair scope)."
            )
        else:
            # Execute Pass 2 for both NEW_REPAIR_DEFECT and COMPLETED_REPAIR_COMPLAINT
            candidate_sors = get_candidate_sors_for_trade(trade_val)
            if use_live:
                live_client = JevRepairsTriageEngine(api_key=self.api_key)
                stage2_output = live_client.resolve_sor_code(
                    complaint_text=request.complaint_text,
                    trade=trade_val,
                    candidate_sors=candidate_sors,
                    image_source=raw_image_source,
                    existing_job_ref=request.existing_job_ref,
                )
            else:
                stage2_output = self.simulator.resolve_sor_code(
                    complaint_text=request.complaint_text,
                    trade=trade_val,
                    candidate_sors=candidate_sors,
                    synthetic_image_preset=request.synthetic_image_preset,
                )

        # 4. Evaluate Stage 1 & Stage 2 outputs through TriageEscalationGuard
        guard_result = guard.evaluate(
            stage1_output=stage1_output,
            stage2_output=stage2_output,
        )

        # 5. Enforce hard media purge if Content Safety Gate triggered
        media_discarded = False
        if guard_result.discard_media:
            normalized_b64 = None
            media_discarded = True
            if image_telemetry is not None:
                image_telemetry.discarded_by_safety_gate = True

        prop_baseline = GOLDEN_PROPERTIES.get(request.property_id)
        prop_name = (
            prop_baseline.name if prop_baseline else f"Property {request.property_id}"
        )

        ticket_status = DESTINATION_TO_TICKET_STATUS.get(
            guard_result.destination, TicketStatus.PENDING_SURVEYOR_REVIEW
        )

        return TriageTicketRecord(
            ticket_id=f"TKT-{uuid.uuid4().hex[:8].upper()}",
            session_id=request.session_id or "default",
            property_id=request.property_id,
            property_name=prop_name,
            channel=request.channel,
            engine_mode=EngineMode.LIVE if use_live else EngineMode.SIMULATED,
            complaint_text=request.complaint_text,
            existing_job_ref=request.existing_job_ref,
            has_image=(raw_image_source is not None),
            media_discarded=media_discarded,
            normalized_image_base64=normalized_b64,
            image_telemetry=image_telemetry,
            stage1_output=stage1_output,
            stage2_output=stage2_output,
            stage2_skipped_reason=stage2_skipped_reason,
            decision=guard_result.to_pydantic(),
            status=ticket_status,
        )


def _print_ticket_summary(title: str, ticket: TriageTicketRecord) -> None:
    dec = ticket.decision
    reasons_str = ", ".join(r.value for r in dec.reasons) if dec.reasons else "NONE (Clean Pass)"
    print(f"\n{title}")
    print(f"  Channel      : {ticket.channel.value} | Image Attached: {ticket.has_image} | Media Purged: {ticket.media_discarded}")
    print(f"  Intent       : {dec.message_intent.value} (p={dec.metadata.get('intent_prob', 0):.2f})")
    print(
        f"  Trade & SOR  : Trade={dec.assigned_trade or 'N/A'} (p={dec.metadata.get('trade_prob', 0):.2f}) "
        f"-> SOR={dec.assigned_sor or 'N/A'} (p={dec.metadata.get('sor_prob', 0):.2f}, margin={dec.metadata.get('sor_margin')})"
    )
    if dec.assigned_sor_description:
        print(f"  M3NHF Spec   : {dec.assigned_sor_description}")
    if ticket.stage2_skipped_reason:
        print(f"  Stage 2 Note : {ticket.stage2_skipped_reason}")
    print(f"  Auto-Approve : {dec.auto_approve} | Destination: {dec.destination.value}")
    print(f"  Gating Flags : {reasons_str}")


def run_cli_demo() -> None:
    """Runs all 9 Time-Machine Scenario Presets or a custom CLI complaint through the Phase 1 engine."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 1 CLI Tester for TypeSafe Jev + M3NHF SOR + Circuit-Breaker Gating Engine"
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Optional custom complaint text to classify",
    )
    parser.add_argument(
        "--image-preset",
        type=str,
        default=None,
        help="Optional synthetic image preset (cistern_valve, sink_leak, black_mould, ceiling_light_leak, broken_hinge, inappropriate_placeholder)",
    )
    args = parser.parse_args()

    orchestrator = ComplaintTriageOrchestrator()
    print("=" * 108)
    print("PHASE 1 VERIFICATION: TWO-STAGE TYPESAFE JEV + M3NHF SOR + CIRCUIT-BREAKER GATING ENGINE")
    print("=" * 108)

    if args.text:
        req = ComplaintIntakeRequest(
            complaint_text=args.text,
            synthetic_image_preset=args.image_preset,
        )
        ticket = orchestrator.process_intake(req)
        _print_ticket_summary(f"[CUSTOM INPUT] {args.text}", ticket)
        print("\n" + "=" * 108)
        return

    for preset in SCENARIO_PRESETS:
        req = ComplaintIntakeRequest(
            complaint_text=preset.complaint_text,
            property_id=preset.property_id,
            channel=preset.channel,
            synthetic_image_preset=preset.synthetic_image_preset,
            existing_job_ref=preset.existing_job_ref,
        )
        ticket = orchestrator.process_intake(req)
        _print_ticket_summary(f"[{preset.preset_id}] {preset.title}", ticket)

    print("\n" + "=" * 108)
    print("All 9 Scenario Presets evaluated successfully.")


if __name__ == "__main__":
    run_cli_demo()
