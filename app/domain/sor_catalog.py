"""M3NHF Schedule of Rates (SOR) Catalog and Stage 1 TypeSafe Jev criteria definitions."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from app.domain.enums import MessageIntent, TradeCode


@dataclass(frozen=True)
class SORItem:
    """Represents a single M3NHF Schedule of Rates item."""

    sor_code: str
    trade: TradeCode
    short_description: str
    full_specification: str
    unit_of_measure: str
    base_rate_gbp: float
    default_sla_priority: str  # "1" (Routine 28d), "2" (Urgent 7d), "3" (Emergency 24h)


# Stage 1 Trade Criteria passed to TypeSafe Jev
TRADE_CRITERIA: Dict[str, str] = {
    TradeCode.PLUM.value: (
        "Plumbing, internal leaks, radiators, hot water cylinders, taps, cisterns, waste drainage"
    ),
    TradeCode.ROOF.value: (
        "Roofing, roof tile damage, chimney flashing, gutters, fascia, rainwater downpipes"
    ),
    TradeCode.PLAS.value: (
        "Plastering, water-damaged ceilings, drywall skimming, blown plaster, wall rendering"
    ),
    TradeCode.DAMP.value: (
        "Mould eradication, anti-fungal treatment, condensation mitigation, DPC or penetrating damp"
    ),
    TradeCode.JOIN.value: (
        "Carpentry, doors, window frames, locks, skirting, floorboards, kitchen base/wall units"
    ),
    TradeCode.ELEC.value: (
        "Electrical sockets, tripping consumer units, smoke alarms, extractor fans, light pendants"
    ),
    TradeCode.OTHER.value: (
        "Unmatched issue, grounds maintenance, pest control, ASB/noise, administrative or billing query"
    ),
}

# Stage 1 Message Intent Criteria passed to TypeSafe Jev
MESSAGE_INTENT_CRITERIA: Dict[str, str] = {
    MessageIntent.NEW_REPAIR_DEFECT.value: (
        "Resident reporting a physical property defect or hazard requiring a new repair diagnosis and works order"
    ),
    MessageIntent.COMPLETED_REPAIR_COMPLAINT.value: (
        "Resident complaining about a recently completed repair job (poor workmanship, unfinished work, "
        "mess left behind, or leak/fault recurring right after contractor visit) requiring recall assessment"
    ),
    MessageIntent.WIP_REPAIR_UPDATE.value: (
        "Resident requesting a status update or chasing progress on an existing work-in-progress (WIP) repair"
    ),
    MessageIntent.CONTRACTOR_SCHEDULING.value: (
        "Request to book, reschedule, cancel, confirm, or report a missed contractor appointment slot"
    ),
    MessageIntent.CONTRACTOR_PAYMENT_INQUIRY.value: (
        "Contractor or supplier chasing late invoice payment, purchase order approval, or variation payment"
    ),
    MessageIntent.GENERAL_HOUSING_QUERY.value: (
        "General housing management issue such as Anti-Social Behaviour (ASB), rent/service charges, or tenancy admin"
    ),
}

# Stage 1 Repair Priority SLA Levels passed to TypeSafe Jev
REPAIR_PRIORITY_LEVELS: Dict[str, str] = {
    "1": "Routine (28-day): Minor wear and tear, hairline plaster cracks, eased door, non-critical drip",
    "2": "Urgent (7-day): Persistent slow leak contained in bucket, partial heating fault, broken kitchen unit",
    "3": "Emergency (24-hour): Burst pipe, water pouring into electrics, sewage backflow, total heating loss in winter",
}


# Curated M3NHF Schedule of Rates Catalog structured by standard trade chapters
M3NHF_SOR_CATALOG: Dict[TradeCode, List[SORItem]] = {
    TradeCode.PLUM: [
        SORItem(
            sor_code="192001",
            trade=TradeCode.PLUM,
            short_description="Trace and repair leak on internal domestic water supply pipe up to 22mm",
            full_specification=(
                "M3NHF Section 19 (192001): Locate source of pressurized leak on copper or plastic domestic "
                "supply pipework (<=22mm), renew defective compression/solder fitting, pressure test, and reinstate insulation."
            ),
            unit_of_measure="IT",
            base_rate_gbp=84.50,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="192005",
            trade=TradeCode.PLUM,
            short_description="Replace damaged push-fit waste fitting or trap beneath kitchen sink",
            full_specification=(
                "M3NHF Section 19 (192005): Disconnect, supply, and install new 40mm tubular swivel P/S trap or push-fit "
                "waste coupling beneath kitchen sink unit, clear blockage, and test for water tightness."
            ),
            unit_of_measure="NO",
            base_rate_gbp=56.20,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="194010",
            trade=TradeCode.PLUM,
            short_description="Overhaul leaking ball valve or dual-flush siphon in WC cistern",
            full_specification=(
                "M3NHF Section 19 (194010): Isolate water supply, remove defective float valve or flush siphon in WC cistern, "
                "install WRAS-approved Fluidmaster/equilibrium valve and siphon, and verify overflow cessation."
            ),
            unit_of_measure="NO",
            base_rate_gbp=68.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="195020",
            trade=TradeCode.PLUM,
            short_description="Emergency isolate and make safe burst pipe or unvented cylinder leak",
            full_specification=(
                "M3NHF Section 19 (195020): Emergency 24h response to isolate stopcock/gate valve, drain down affected section "
                "of burst mains/heating pipework, fit temporary cap or permanent repair coupling, and make safe."
            ),
            unit_of_measure="IT",
            base_rate_gbp=142.00,
            default_sla_priority="3",
        ),
    ],
    TradeCode.DAMP: [
        SORItem(
            sor_code="112005",
            trade=TradeCode.DAMP,
            short_description="Fit injected chemical damp proof course (DPC) / barrier against rising damp",
            full_specification=(
                "M3NHF Section 11 (112005): Drill mortar bed at 150mm centres above finished ground level, inject "
                "silicone/silane micro-emulsion DPC cream to form continuous horizontal damp barrier, and plug drill holes."
            ),
            unit_of_measure="M",
            base_rate_gbp=125.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="114001",
            trade=TradeCode.DAMP,
            short_description="Awaab's Law 3-stage fungicidal mould wash, biocide treatment & stain block",
            full_specification=(
                "M3NHF Section 11 (114001): Statutory damp & mould remediation—apply HSE-approved 3-stage fungicidal wash "
                "to affected reveals/ceilings, apply two coats of moisture-resistant anti-mould membrane paint."
            ),
            unit_of_measure="M2",
            base_rate_gbp=95.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="114010",
            trade=TradeCode.DAMP,
            short_description="Inspect, clean, and overhaul humidistat mechanical ventilation unit",
            full_specification=(
                "M3NHF Section 11 (114010): Test airflow rate (L/s) on bathroom/kitchen continuous extract fan, clear ducting "
                "obstruction, recalibrate humidistat trigger threshold, and certify moisture extraction."
            ),
            unit_of_measure="NO",
            base_rate_gbp=78.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="112015",
            trade=TradeCode.DAMP,
            short_description="Trace penetrating damp ingress and repoint defective external brickwork",
            full_specification=(
                "M3NHF Section 11 (112015): Rake out perished mortar joints up to 25mm depth around external wall/window perimeter, "
                "repoint with weather-struck cement-lime mortar, and apply breathable masonry waterproofer."
            ),
            unit_of_measure="M2",
            base_rate_gbp=134.00,
            default_sla_priority="2",
        ),
    ],
    TradeCode.ELEC: [
        SORItem(
            sor_code="211001",
            trade=TradeCode.ELEC,
            short_description="Emergency make safe water ingress in ceiling rose, pendant, or spotlight",
            full_specification=(
                "M3NHF Section 21 (211001): Emergency electrical attendance to isolate lighting circuit at consumer unit, "
                "disconnect waterlogged ceiling rose/downlight, test insulation resistance, and make safe."
            ),
            unit_of_measure="IT",
            base_rate_gbp=128.00,
            default_sla_priority="3",
        ),
        SORItem(
            sor_code="212015",
            trade=TradeCode.ELEC,
            short_description="Replace faulty or cracked 13A twin switched socket outlet",
            full_specification=(
                "M3NHF Section 21 (212015): Isolate ring final circuit, remove heat-damaged or cracked twin 13A socket faceplate, "
                "re-terminate conductors, fit BS 1363 socket, and issue Minor Electrical Installation Works certificate."
            ),
            unit_of_measure="NO",
            base_rate_gbp=62.50,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="214002",
            trade=TradeCode.ELEC,
            short_description="Renew mains-wired interlinked optical smoke or heat alarm head",
            full_specification=(
                "M3NHF Section 21 (214002): Replace faulty or expired mains-powered smoke/heat detector with lithium backup "
                "(BS 5839-6 Grade D1 LD2) and test interlink across all habitable rooms."
            ),
            unit_of_measure="NO",
            base_rate_gbp=89.00,
            default_sla_priority="2",
        ),
    ],
    TradeCode.ROOF: [
        SORItem(
            sor_code="101004",
            trade=TradeCode.ROOF,
            short_description="Replace slipped or broken interlocking concrete roof tiles (up to 6 No)",
            full_specification=(
                "M3NHF Section 10 (101004): Access pitched roof, remove cracked/slipped concrete interlocking tiles, inspect "
                "breathable underlay and battens, supply and clip new matching tiles."
            ),
            unit_of_measure="IT",
            base_rate_gbp=165.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="105012",
            trade=TradeCode.ROOF,
            short_description="Clear blockage and renew leaking uPVC rainwater gutter union/downpipe",
            full_specification=(
                "M3NHF Section 10 (105012): Clear moss/debris from eaves guttering, renew defective 112mm half-round gutter "
                "union bracket and rubber seals, and water-test flow into downpipe."
            ),
            unit_of_measure="IT",
            base_rate_gbp=92.00,
            default_sla_priority="1",
        ),
    ],
    TradeCode.JOIN: [
        SORItem(
            sor_code="125011",
            trade=TradeCode.JOIN,
            short_description="Renew damaged kitchen base unit door and pair of 110-degree concealed hinges",
            full_specification=(
                "M3NHF Section 12 (125011): Remove torn/delaminated kitchen cupboard door and snapped concealed hinges, "
                "reinforce carcass mounting plate, and fit new matching door and soft-close hinges."
            ),
            unit_of_measure="NO",
            base_rate_gbp=74.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="121008",
            trade=TradeCode.JOIN,
            short_description="Ease and adjust binding internal fire door and renew intumescent strip",
            full_specification=(
                "M3NHF Section 12 (121008): Plane/adjust FD30 internal fire door to maintain 3mm perimeter gap, tighten hinges, "
                "adjust overhead closer latch action, and replace combined intumescent/smoke seal."
            ),
            unit_of_measure="NO",
            base_rate_gbp=88.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="123020",
            trade=TradeCode.JOIN,
            short_description="Repair and resecure loose timber staircase handrail or balustrade",
            full_specification=(
                "M3NHF Section 12 (123020): Refix loose wall-mounted timber mopstick handrail with heavy-duty masonry fixings "
                "and patresses to restore safe stair access."
            ),
            unit_of_measure="IT",
            base_rate_gbp=69.00,
            default_sla_priority="2",
        ),
    ],
    TradeCode.PLAS: [
        SORItem(
            sor_code="161002",
            trade=TradeCode.PLAS,
            short_description="Hack off blown wall plaster and apply 2-coat finish skim up to 2m2",
            full_specification=(
                "M3NHF Section 16 (161002): Remove hollow/loose plaster back to solid masonry, apply PVA bonding agent, "
                "undercoat plaster, and trowel smooth 2mm multi-finish skim."
            ),
            unit_of_measure="IT",
            base_rate_gbp=112.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="162008",
            trade=TradeCode.PLAS,
            short_description="Overboard water-damaged plasterboard ceiling section and skim finish",
            full_specification=(
                "M3NHF Section 16 (162008): Cut out bowed/stained plasterboard ceiling up to 3m2, fix new 12.5mm foil-backed "
                "plasterboard to joists with scrim tape, and apply 2-coat plaster skim."
            ),
            unit_of_measure="IT",
            base_rate_gbp=158.00,
            default_sla_priority="1",
        ),
    ],
}


def get_candidate_sors_for_trade(trade: str) -> Dict[str, str]:
    """Returns the trade-bounded M3NHF candidate map (code -> description) for Jev Pass 2."""
    try:
        trade_enum = TradeCode(trade)
    except ValueError:
        trade_enum = TradeCode.OTHER

    items = M3NHF_SOR_CATALOG.get(trade_enum, [])
    candidates: Dict[str, str] = {
        item.sor_code: item.short_description for item in items
    }
    candidates["OTHER"] = (
        f"Defect scope outside standard M3NHF {trade_enum.value} schedule or requires specialist survey"
    )
    return candidates


def get_sor_item(sor_code: Optional[str]) -> Optional[SORItem]:
    """Looks up full M3NHF SOR metadata by 6-digit code."""
    if not sor_code or sor_code == "OTHER":
        return None
    for items in M3NHF_SOR_CATALOG.values():
        for item in items:
            if item.sor_code == sor_code:
                return item
    return None
