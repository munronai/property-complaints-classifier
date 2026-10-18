"""Golden baseline properties and the 9 Time-Machine Scenario Presets."""

from typing import Dict, List
from app.domain.enums import (
    EscalationReason,
    IntakeChannel,
    PortfolioType,
    RoutingDestination,
)
from app.domain.schemas import PropertyBaseline, ScenarioPreset


GOLDEN_PROPERTIES: Dict[str, PropertyBaseline] = {
    "prop_oak_01": PropertyBaseline(
        property_id="prop_oak_01",
        name="Flat 4, Oak Court (1970s Masonry Block)",
        address="4 Oak Court, Lewisham, London SE13 6AA",
        portfolio_type=PortfolioType.SOCIAL_HOUSING,
        landlord_name="Metropolitan Thames Valley Housing (Sandbox)",
        tenant_Summary="Assured Tenancy — Family w/ Young Child",
        active_wip_jobs=["JOB-88412 (Plastering 2nd Coat Skim — Scheduled Thu AM)"],
        completed_jobs=["JOB-77210 (Kitchen Sink Waste Trap Replacement — Completed Yesterday)"],
    ),
    "prop_elm_02": PropertyBaseline(
        property_id="prop_elm_02",
        name="12 Elm Terrace (Victorian Street Property)",
        address="12 Elm Terrace, Hackney, London E8 1ab",
        portfolio_type=PortfolioType.SOCIAL_HOUSING,
        landlord_name="Peabody Trust (Sandbox)",
        tenant_Summary="Secure Tenancy — Ground Floor Maisonette",
        active_wip_jobs=["JOB-90104 (Gutter Clearance & Union Seal)"],
        completed_jobs=["JOB-65109 (WC Cistern Siphon Overhaul)"],
    ),
    "prop_cedar_03": PropertyBaseline(
        property_id="prop_cedar_03",
        name="Unit 3B, Cedar Business Park (Commercial FRI Lease)",
        address="Unit 3B Cedar Park, Croydon CR0 4XZ",
        portfolio_type=PortfolioType.COMMERCIAL_PROPERTY,
        landlord_name="Albion Commercial Estates",
        tenant_Summary="10-Year FRI Commercial Lease — Light Industrial / IT",
        active_wip_jobs=["PO-2026-441 (Loading Bay Roller Shutter Maintenance)"],
        completed_jobs=["INV-2026-091 (Emergency Roof Valley Flashing Repair)"],
    ),
}


SCENARIO_PRESETS: List[ScenarioPreset] = [
    ScenarioPreset(
        preset_id="preset_clean_plumbing",
        title="1. Clean Auto-Dispatch: WC Cistern Ball Valve Leak",
        badge="AUTO_DISPATCH_HMS",
        channel=IntakeChannel.DASHBOARD_UI,
        property_id="prop_oak_01",
        complaint_text=(
            "The toilet cistern in the main bathroom won't stop filling up and water is constantly "
            "trickling down the overflow pipe into the pan. The float ball valve seems stuck."
        ),
        synthetic_image_preset="cistern_valve",
        what_it_tests=(
            "Nominal happy path: unambiguous plumbing defect (PLUM -> M3NHF 194010) with high trade "
            "confidence (>0.85), high SOR confidence (>0.80), clear margin (>0.15), and no statutory damp."
        ),
        expected_outcome="Passes all gating checks and automatically raises M3NHF works order 194010.",
        expected_destination=RoutingDestination.AUTO_DISPATCH_HMS,
        expected_reasons=[],
    ),
    ScenarioPreset(
        preset_id="preset_ambiguous_margin",
        title="2. Ambiguous SOR Margin Trap: Under-Sink Pipe vs. Waste Fitting",
        badge="AMBIGUOUS_SOR_MARGIN",
        channel=IntakeChannel.DASHBOARD_UI,
        property_id="prop_oak_01",
        complaint_text=(
            "There is water pooling inside the kitchen base cupboard underneath the sink. "
            "Not sure if it is coming from the copper supply pipe joint or the plastic waste trap."
        ),
        synthetic_image_preset="sink_leak",
        what_it_tests=(
            "Tests the Top-1 vs. Top-2 probability margin circuit breaker: Stage 1 is confident it is "
            "PLUM (88%), but Stage 2 splits probability closely between 192001 (54%) and 192005 (44%)."
        ),
        expected_outcome="Blocked from auto-dispatch due to LOW_SOR_CONFIDENCE & AMBIGUOUS_SOR_MARGIN (<0.15).",
        expected_destination=RoutingDestination.SURVEYOR_DESK_REVIEW,
        expected_reasons=[
            EscalationReason.LOW_SOR_CONFIDENCE,
            EscalationReason.AMBIGUOUS_SOR_MARGIN,
        ],
    ),
    ScenarioPreset(
        preset_id="preset_awaabs_law_damp",
        title="3. Statutory Circuit Breaker: Awaab's Law Black Mould & Damp",
        badge="AWAABS_LAW_RISK",
        channel=IntakeChannel.WHATSAPP,
        property_id="prop_oak_01",
        complaint_text=(
            "Heavy black mould spreading across the child's bedroom window reveal and cold external "
            "wall. The wall feels wet to touch every morning and smells musty."
        ),
        synthetic_image_preset="black_mould",
        what_it_tests=(
            "Statutory Awaab's Law guardrail: even when the model identifies DAMP -> 114001 with high "
            "confidence, damp hazard probability >= 0.40 forces mandatory escalation."
        ),
        expected_outcome="Hard override to DISREPAIR_LEGAL_TEAM for statutory Awaab's Law inspection timeline.",
        expected_destination=RoutingDestination.DISREPAIR_LEGAL_TEAM,
        expected_reasons=[EscalationReason.AWAABS_LAW_RISK],
    ),
    ScenarioPreset(
        preset_id="preset_emergency_water_electrics",
        title="4. Emergency Priority 3: Water Pouring Through Kitchen Light Fitting",
        badge="EMERGENCY_ESCALATION",
        channel=IntakeChannel.WHATSAPP,
        property_id="prop_oak_01",
        complaint_text=(
            "URGENT! Water is pouring straight through the kitchen ceiling rose light fitting from "
            "the flat above and sparks popped when I touched the switch!"
        ),
        synthetic_image_preset="ceiling_light_leak",
        what_it_tests=(
            "24-hour Emergency SLA (Priority 3) circuit breaker: active water ingress into live electrical "
            "fittings must never sit in a routine contractor queue."
        ),
        expected_outcome="Escalated immediately to OUT_OF_HOURS_DUTY_OFFICER for 24-hour make-safe attendance.",
        expected_destination=RoutingDestination.OUT_OF_HOURS_DUTY_OFFICER,
        expected_reasons=[EscalationReason.EMERGENCY_ESCALATION],
    ),
    ScenarioPreset(
        preset_id="preset_whatsapp_photo_disambiguation",
        title="5. Multimodal Photo Disambiguation: Vague Text + Clear Photo",
        badge="AUTO_DISPATCH_HMS",
        channel=IntakeChannel.WHATSAPP,
        property_id="prop_elm_02",
        complaint_text="Hi, this metal thing snapped off in the kitchen today and the door is hanging off, see pic.",
        synthetic_image_preset="broken_hinge",
        what_it_tests=(
            "Demonstrates how TypeSafe Jev uses visual tokens in the attached photo to resolve vague "
            "resident text ('metal thing snapped') into JOIN -> M3NHF 125011 (kitchen unit door & hinges)."
        ),
        expected_outcome="Confidently resolves JOIN -> 125011 and auto-dispatches to HMS.",
        expected_destination=RoutingDestination.AUTO_DISPATCH_HMS,
        expected_reasons=[],
    ),
    ScenarioPreset(
        preset_id="preset_wip_scheduling_reroute",
        title="6. Non-Repair Intent Re-Route: WIP Update & Contractor Rescheduling",
        badge="REPAIR_UPDATE_OR_SCHEDULING",
        channel=IntakeChannel.WHATSAPP,
        property_id="prop_oak_01",
        complaint_text=(
            "Hi, chasing an update on my work-in-progress repair JOB-88412. When is the plasterer coming "
            "back to finish the second coat, and can we reschedule the slot to Thursday morning?"
        ),
        existing_job_ref="JOB-88412",
        what_it_tests=(
            "Stage 1 Intent Gate: detects that the resident is asking for a WIP update / rescheduling "
            "an existing job rather than reporting a new defect. Short-circuits Stage 2 SOR matching."
        ),
        expected_outcome="Short-circuits Stage 2 and re-routes to CUSTOMER_SERVICE_WIP_DESK (0 duplicate orders).",
        expected_destination=RoutingDestination.CUSTOMER_SERVICE_WIP_DESK,
        expected_reasons=[EscalationReason.REPAIR_UPDATE_OR_SCHEDULING],
    ),
    ScenarioPreset(
        preset_id="preset_contractor_late_payment",
        title="7. Finance Re-Route: Subcontractor Late Payment Inquiry",
        badge="NON_REPAIR_FINANCE_QUERY",
        channel=IntakeChannel.DASHBOARD_UI,
        property_id="prop_cedar_03",
        complaint_text=(
            "Accounts Payable: we are chasing overdue payment on Invoice INV-2026-091 (£1,450 + VAT) "
            "for the roof valley repair completed 45 days ago at Cedar Park. Please advise remittance date."
        ),
        existing_job_ref="INV-2026-091",
        what_it_tests=(
            "Stage 1 Intent Gate: detects a contractor late-payment / invoice query and prevents it "
            "from being classified as a roofing repair."
        ),
        expected_outcome="Short-circuits Stage 2 and re-routes directly to CONTRACTOR_FINANCE_DESK.",
        expected_destination=RoutingDestination.CONTRACTOR_FINANCE_DESK,
        expected_reasons=[EscalationReason.NON_REPAIR_FINANCE_QUERY],
    ),
    ScenarioPreset(
        preset_id="preset_completed_repair_complaint",
        title="8. Completed Repair Quality Complaint: Defective Plumbing Recall",
        badge="POST_REPAIR_QUALITY_COMPLAINT",
        channel=IntakeChannel.WHATSAPP,
        property_id="prop_oak_01",
        complaint_text=(
            "Your operative came yesterday and closed JOB-77210 as completed, but the new push-fit waste "
            "pipe under the kitchen sink was fitted crookedly and is still leaking onto the cupboard floor!"
        ),
        synthetic_image_preset="sink_leak",
        existing_job_ref="JOB-77210",
        what_it_tests=(
            "Assesses a complaint about a COMPLETED repair job: runs BOTH Pass 1 and Pass 2 to scope "
            "the remedial trade/SOR code (PLUM -> 192005), then routes to QUALITY_RECALL_SURVEYOR_REVIEW "
            "so the landlord recalls the contractor instead of paying twice."
        ),
        expected_outcome="Scopes remedial SOR 192005 and routes to QUALITY_RECALL_SURVEYOR_REVIEW.",
        expected_destination=RoutingDestination.QUALITY_RECALL_SURVEYOR_REVIEW,
        expected_reasons=[EscalationReason.POST_REPAIR_QUALITY_COMPLAINT],
    ),
    ScenarioPreset(
        preset_id="preset_inappropriate_content_discard",
        title="9. Content Safety Gate: Inappropriate / Rude Photo Flag & Discard",
        badge="INAPPROPRIATE_CONTENT_DETECTED",
        channel=IntakeChannel.WHATSAPP,
        property_id="prop_elm_02",
        complaint_text=(
            "Stop ignoring my messages!! Sending rude/offensive photo attachment to get your attention."
        ),
        synthetic_image_preset="inappropriate_placeholder",
        what_it_tests=(
            "Stage 1 Content Safety Gate: detects inappropriate/rude photos or abusive content, halts "
            "processing before Stage 2, purges raw image bytes from memory/storage, and logs moderation flag."
        ),
        expected_outcome="Purges media bytes (media_discarded=True) and routes to DISCARDED_INAPPROPRIATE_CONTENT.",
        expected_destination=RoutingDestination.DISCARDED_INAPPROPRIATE_CONTENT,
        expected_reasons=[EscalationReason.INAPPROPRIATE_CONTENT_DETECTED],
    ),
]


def get_preset_by_id(preset_id: str) -> ScenarioPreset:
    """Looks up a scenario preset by its ID or raises KeyError."""
    for preset in SCENARIO_PRESETS:
        if preset.preset_id == preset_id:
            return preset
    raise KeyError(f"Unknown scenario preset ID: {preset_id}")
