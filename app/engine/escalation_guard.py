"""Hard circuit-breaker gating and intent re-routing middleware wrapping TypeSafe Jev outputs."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.domain.enums import EscalationReason, MessageIntent, RoutingDestination
from app.domain.schemas import GatingThresholds, TriageDecisionModel
from app.domain.sor_catalog import get_sor_item


@dataclass
class TriageDecisionResult:
    """Result returned by TriageEscalationGuard.evaluate()."""

    auto_approve: bool
    destination: RoutingDestination
    assigned_trade: Optional[str]
    assigned_sor: Optional[str]
    message_intent: MessageIntent = MessageIntent.NEW_REPAIR_DEFECT
    assigned_sor_description: Optional[str] = None
    discard_media: bool = False
    is_completed_job_recall: bool = False
    reasons: List[EscalationReason] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_pydantic(self) -> TriageDecisionModel:
        """Converts dataclass result into a strict Pydantic v2 TriageDecisionModel."""
        return TriageDecisionModel(
            auto_approve=self.auto_approve,
            destination=self.destination,
            message_intent=self.message_intent,
            assigned_trade=self.assigned_trade,
            assigned_sor=self.assigned_sor,
            assigned_sor_description=self.assigned_sor_description,
            discard_media=self.discard_media,
            is_completed_job_recall=self.is_completed_job_recall,
            reasons=list(self.reasons),
            metadata=dict(self.metadata),
        )


class TriageEscalationGuard:
    """Configurable threshold gatekeeper for TypeSafe Jev repair and complaint decisions."""

    def __init__(
        self,
        min_trade_confidence: float = 0.70,
        min_sor_confidence: float = 0.65,
        min_probability_margin: float = 0.15,
        damp_hazard_threshold: float = 0.40,
        inappropriate_content_threshold: float = 0.50,
    ):
        self.min_trade_conf = min_trade_confidence
        self.min_sor_conf = min_sor_confidence
        self.min_margin = min_probability_margin
        self.damp_threshold = damp_hazard_threshold
        self.inappropriate_threshold = inappropriate_content_threshold

    @classmethod
    def from_thresholds(cls, thresholds: Optional[GatingThresholds] = None) -> "TriageEscalationGuard":
        """Constructs a guard instance from a GatingThresholds Pydantic model."""
        if thresholds is None:
            return cls()
        return cls(
            min_trade_confidence=thresholds.min_trade_confidence,
            min_sor_confidence=thresholds.min_sor_confidence,
            min_probability_margin=thresholds.min_probability_margin,
            damp_hazard_threshold=thresholds.damp_hazard_threshold,
            inappropriate_content_threshold=thresholds.inappropriate_content_threshold,
        )

    def evaluate(
        self,
        stage1_output: Dict[str, Any],
        stage2_output: Optional[Dict[str, Any]] = None,
    ) -> TriageDecisionResult:
        """Evaluates Stage 1 and Stage 2 Jev outputs against all safety, intent, statutory, and confidence gates."""
        reasons: List[EscalationReason] = []
        answers_s1 = stage1_output.get("answers", {})

        # 0. Inspect Stage 1: Content Safety / Inappropriate Media or Text Gate (Priority 1 Hard Stop)
        inappropriate_ans = answers_s1.get("inappropriate_content_flag", {})
        inappropriate_flag = bool(inappropriate_ans.get("value", False))
        inappropriate_prob = float(inappropriate_ans.get("probability", 0.0))
        if inappropriate_flag or inappropriate_prob >= self.inappropriate_threshold:
            reasons.append(EscalationReason.INAPPROPRIATE_CONTENT_DETECTED)
            return TriageDecisionResult(
                auto_approve=False,
                destination=RoutingDestination.DISCARDED_INAPPROPRIATE_CONTENT,
                assigned_trade=None,
                assigned_sor=None,
                message_intent=MessageIntent.GENERAL_HOUSING_QUERY,
                discard_media=True,
                is_completed_job_recall=False,
                reasons=reasons,
                metadata={
                    "inappropriate_prob": inappropriate_prob,
                    "media_purged": True,
                },
            )

        # 1. Inspect Stage 1: Message Intent classification
        intent_ans = answers_s1.get("message_intent", {})
        raw_intent = intent_ans.get("value", MessageIntent.NEW_REPAIR_DEFECT.value)
        intent_prob = float(intent_ans.get("probability", 1.0))
        try:
            intent_enum = MessageIntent(raw_intent)
        except ValueError:
            intent_enum = MessageIntent.NEW_REPAIR_DEFECT

        # 2. Inspect Stage 1: Trade classification
        trade_ans = answers_s1.get("primary_trade", {})
        trade = trade_ans.get("value")
        trade_prob = float(trade_ans.get("probability", 0.0))

        # 3. Inspect Stage 1: Awaab's Law Damp & Mould risk
        damp_ans = answers_s1.get("awaabs_law_damp_hazard", {})
        damp_flag = bool(damp_ans.get("value", False))
        damp_prob = float(damp_ans.get("probability", 0.0))
        if damp_flag or damp_prob >= self.damp_threshold:
            reasons.append(EscalationReason.AWAABS_LAW_RISK)

        # 4. Inspect Stage 1: Urgent / Emergency SLA check
        priority_ans = answers_s1.get("repair_priority", {})
        priority_val = str(priority_ans.get("value", "1"))
        priority_prob = float(priority_ans.get("probability", 0.0))
        if priority_val == "3":  # Level 3 = 24-hour emergency
            reasons.append(EscalationReason.EMERGENCY_ESCALATION)

        # 5. Inspect Non-Repair Intents (Contractor Payment, WIP Update, Scheduling)
        if intent_enum == MessageIntent.CONTRACTOR_PAYMENT_INQUIRY:
            reasons.append(EscalationReason.NON_REPAIR_FINANCE_QUERY)
        elif intent_enum in (
            MessageIntent.WIP_REPAIR_UPDATE,
            MessageIntent.CONTRACTOR_SCHEDULING,
        ):
            reasons.append(EscalationReason.REPAIR_UPDATE_OR_SCHEDULING)
        elif intent_enum == MessageIntent.COMPLETED_REPAIR_COMPLAINT:
            reasons.append(EscalationReason.POST_REPAIR_QUALITY_COMPLAINT)

        # Only enforce trade/SOR confidence checks when evaluating a physical repair or completed-job recall
        is_repair_or_recall = intent_enum in (
            MessageIntent.NEW_REPAIR_DEFECT,
            MessageIntent.COMPLETED_REPAIR_COMPLAINT,
            MessageIntent.GENERAL_HOUSING_QUERY,
        )

        if is_repair_or_recall:
            if not trade or trade == "OTHER" or trade_prob < self.min_trade_conf:
                reasons.append(EscalationReason.LOW_TRADE_CONFIDENCE)

        # 6. Inspect Stage 2: Specific SOR Code Resolution (if executed)
        assigned_sor: Optional[str] = None
        sor_prob: float = 0.0
        sor_margin: Optional[float] = None
        sor_desc: Optional[str] = None

        if stage2_output:
            answers_s2 = stage2_output.get("answers", {})
            sor_ans = answers_s2.get("selected_sor", {})
            assigned_sor = sor_ans.get("value")
            sor_prob = float(sor_ans.get("probability", 0.0))

            sor_item = get_sor_item(assigned_sor)
            if sor_item:
                sor_desc = sor_item.short_description

            if assigned_sor == "OTHER":
                reasons.append(EscalationReason.OUT_OF_SCHEDULE_SCOPE)
            elif sor_prob < self.min_sor_conf:
                reasons.append(EscalationReason.LOW_SOR_CONFIDENCE)

            # Margin check: is the top choice clearly better than the runner-up?
            distribution = sor_ans.get("distribution", {})
            sorted_probs = sorted(
                (float(v) for v in distribution.values()), reverse=True
            )
            if len(sorted_probs) >= 2:
                top_1, top_2 = sorted_probs[0], sorted_probs[1]
                sor_margin = round(top_1 - top_2, 4)
                if sor_margin < self.min_margin:
                    reasons.append(EscalationReason.AMBIGUOUS_SOR_MARGIN)
            elif len(sorted_probs) == 1:
                sor_margin = round(sorted_probs[0], 4)

        telemetry_meta: Dict[str, Any] = {
            "intent": intent_enum.value,
            "intent_prob": round(intent_prob, 4),
            "trade_prob": round(trade_prob, 4),
            "sor_prob": round(sor_prob, 4),
            "sor_margin": sor_margin,
            "damp_prob": round(damp_prob, 4),
            "priority_level": priority_val,
            "priority_prob": round(priority_prob, 4),
            "inappropriate_prob": round(inappropriate_prob, 4),
        }

        # 7. Routing Resolution Matrix (Ordered by Statutory / Safety / Operational Priority)
        if EscalationReason.AWAABS_LAW_RISK in reasons:
            return TriageDecisionResult(
                auto_approve=False,
                destination=RoutingDestination.DISREPAIR_LEGAL_TEAM,
                assigned_trade=trade,
                assigned_sor=assigned_sor,
                message_intent=intent_enum,
                assigned_sor_description=sor_desc,
                is_completed_job_recall=(
                    intent_enum == MessageIntent.COMPLETED_REPAIR_COMPLAINT
                ),
                reasons=reasons,
                metadata=telemetry_meta,
            )

        if EscalationReason.EMERGENCY_ESCALATION in reasons:
            return TriageDecisionResult(
                auto_approve=False,
                destination=RoutingDestination.OUT_OF_HOURS_DUTY_OFFICER,
                assigned_trade=trade,
                assigned_sor=assigned_sor,
                message_intent=intent_enum,
                assigned_sor_description=sor_desc,
                is_completed_job_recall=(
                    intent_enum == MessageIntent.COMPLETED_REPAIR_COMPLAINT
                ),
                reasons=reasons,
                metadata=telemetry_meta,
            )

        if EscalationReason.NON_REPAIR_FINANCE_QUERY in reasons:
            return TriageDecisionResult(
                auto_approve=False,
                destination=RoutingDestination.CONTRACTOR_FINANCE_DESK,
                assigned_trade=None,
                assigned_sor=None,
                message_intent=intent_enum,
                reasons=reasons,
                metadata=telemetry_meta,
            )

        if EscalationReason.REPAIR_UPDATE_OR_SCHEDULING in reasons:
            return TriageDecisionResult(
                auto_approve=False,
                destination=RoutingDestination.CUSTOMER_SERVICE_WIP_DESK,
                assigned_trade=trade if trade != "OTHER" else None,
                assigned_sor=None,
                message_intent=intent_enum,
                reasons=reasons,
                metadata=telemetry_meta,
            )

        if EscalationReason.POST_REPAIR_QUALITY_COMPLAINT in reasons:
            return TriageDecisionResult(
                auto_approve=False,
                destination=RoutingDestination.QUALITY_RECALL_SURVEYOR_REVIEW,
                assigned_trade=trade,
                assigned_sor=assigned_sor,
                message_intent=intent_enum,
                assigned_sor_description=sor_desc,
                is_completed_job_recall=True,
                reasons=reasons,
                metadata=telemetry_meta,
            )

        if reasons:
            return TriageDecisionResult(
                auto_approve=False,
                destination=RoutingDestination.SURVEYOR_DESK_REVIEW,
                assigned_trade=trade,
                assigned_sor=assigned_sor,
                message_intent=intent_enum,
                assigned_sor_description=sor_desc,
                reasons=reasons,
                metadata=telemetry_meta,
            )

        # Passed all validation checks
        return TriageDecisionResult(
            auto_approve=True,
            destination=RoutingDestination.AUTO_DISPATCH_HMS,
            assigned_trade=trade,
            assigned_sor=assigned_sor,
            message_intent=intent_enum,
            assigned_sor_description=sor_desc,
            reasons=[],
            metadata=telemetry_meta,
        )
