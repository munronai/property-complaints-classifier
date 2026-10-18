"""
First-tier Tribunal (Property Chamber - Residential Property) Harvester (Phase 4).

Provides technical building-pathology and HHSRS (Housing Health and Safety Rating System)
defect narratives linked to M3NHF v8 Schedule of Rates codes across all 6 repair trades.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class TribunalDefectSeed:
    decision_ref: str
    hhsrs_hazard: str
    trade: str
    sor_code: str
    technical_narrative: str
    colloquial_tenant_text: str
    urgency: str
    awaabs_law: bool = False


TRIBUNAL_DEFECT_SEEDS: List[TribunalDefectSeed] = [
    # PLUM
    TribunalDefectSeed(
        decision_ref="LON/00AG/LSC/2025/0014",
        hhsrs_hazard="Sanitation and Drainage",
        trade="PLUM",
        sor_code="191004",
        technical_narrative="Defective 40mm polypropylene bottle trap beneath kitchen sink unit discharging foul greywater into base cabinet.",
        colloquial_tenant_text="Water is dripping steadily from the plastic bottle trap pipe under the kitchen sink whenever we drain the bowl.",
        urgency="ROUTINE",
    ),
    TribunalDefectSeed(
        decision_ref="LON/00AG/LSC/2025/0029",
        hhsrs_hazard="Excess Cold",
        trade="PLUM",
        sor_code="196012",
        technical_narrative="Defective 15mm angled thermostatic radiator valve (TRV) body and sensor head stuck closed on lounge panel radiator.",
        colloquial_tenant_text="The thermostatic radiator valve TRV on our living room radiator is snapped and stuck off so the radiator stays stone cold.",
        urgency="URGENT",
    ),
    TribunalDefectSeed(
        decision_ref="MAN/00BN/LSC/2025/0041",
        hhsrs_hazard="Water Supply / Flooding",
        trade="PLUM",
        sor_code="195001",
        technical_narrative="Ruptured 15mm internal copper hot water distribution pipe below floorboards causing uncontrolled escape of water.",
        colloquial_tenant_text="Emergency! A copper water pipe has burst under the hallway floorboards and water is spraying everywhere.",
        urgency="EMERGENCY",
    ),
    # DAMP
    TribunalDefectSeed(
        decision_ref="LON/00BK/LSC/2025/0088",
        hhsrs_hazard="Damp and Mould Growth (Category 1)",
        trade="DAMP",
        sor_code="111002",
        technical_narrative="Extensive Aspergillus/Cladosporium black mould colonisation on cold thermal bridge in child bedroom with infant asthma risk.",
        colloquial_tenant_text="Thick black mould covers my baby's bedroom wall and ceiling, the flat smells damp and my 1 year old is wheezing with asthma.",
        urgency="EMERGENCY",
        awaabs_law=True,
    ),
    TribunalDefectSeed(
        decision_ref="BIR/00CN/LSC/2025/0052",
        hhsrs_hazard="Damp and Mould Growth (Rising Damp)",
        trade="DAMP",
        sor_code="112005",
        technical_narrative="Bridged or failed horizontal damp proof course (DPC) along ground floor masonry wall resulting in hygroscopic salt tide marks.",
        colloquial_tenant_text="Rising damp is creeping up the ground floor living room brick wall from the skirting board with white salt tide marks; needs chemical DPC injection.",
        urgency="ROUTINE",
    ),
    TribunalDefectSeed(
        decision_ref="MAN/00CA/LSC/2025/0063",
        hhsrs_hazard="Damp and Mould Growth (Subfloor Ventilation)",
        trade="DAMP",
        sor_code="113008",
        technical_narrative="Cracked and choked 225x75mm clay terracotta subfloor airbrick obstructing cross-ventilation to suspended timber floor void.",
        colloquial_tenant_text="The outside clay airbrick vent near the bottom of the wall is smashed and blocked up, making the floorboards smell musty.",
        urgency="ROUTINE",
    ),
    # ROOF
    TribunalDefectSeed(
        decision_ref="LON/00AU/LSC/2025/0077",
        hhsrs_hazard="Structural Collapse and Falling Elements / Penetrating Damp",
        trade="ROOF",
        sor_code="101003",
        technical_narrative="Displaced concrete interlocking roof tiles to main pitched roof slope following storm damage.",
        colloquial_tenant_text="Three roof tiles have slipped off the roof in the storm and rain is dripping into the loft.",
        urgency="URGENT",
    ),
    TribunalDefectSeed(
        decision_ref="BIR/00CT/LSC/2025/0091",
        hhsrs_hazard="Penetrating Dampness (Rainwater Goods)",
        trade="ROOF",
        sor_code="103005",
        technical_narrative="Accumulated moss and silt obstructing half-round uPVC eaves guttering causing rainwater cascade down external brickwork.",
        colloquial_tenant_text="The guttering at the top of the house is completely blocked with moss and overflowing like a waterfall down the bedroom wall.",
        urgency="ROUTINE",
    ),
    # JOIN
    TribunalDefectSeed(
        decision_ref="LON/00AY/LSC/2025/0105",
        hhsrs_hazard="Entry by Intruders",
        trade="JOIN",
        sor_code="121004",
        technical_narrative="Sheared euro-profile cylinder cam and multipoint gear mechanism to front entrance composite door.",
        colloquial_tenant_text="My front door multipoint lock euro cylinder has jammed and won't lock at all, leaving the flat insecure tonight.",
        urgency="URGENT",
    ),
    TribunalDefectSeed(
        decision_ref="MAN/00DA/LSC/2025/0119",
        hhsrs_hazard="Falls between Levels / Window Safety",
        trade="JOIN",
        sor_code="122004",
        technical_narrative="Stripped gearbox on uPVC casement window espagnolette locking mechanism preventing secure closure.",
        colloquial_tenant_text="The espagnolette lock mechanism inside the bedroom uPVC window handle is broken and the window won't stay shut.",
        urgency="URGENT",
    ),
    # ELEC
    TribunalDefectSeed(
        decision_ref="LON/00BE/LSC/2025/0133",
        hhsrs_hazard="Electrical Hazards",
        trade="ELEC",
        sor_code="214011",
        technical_narrative="Thermal arcing and charring to 13A twin switched socket outlet faceplate in kitchen.",
        colloquial_tenant_text="The double plug socket in the kitchen is sparking, smells of burning plastic and keeps tripping the consumer unit fuse box.",
        urgency="EMERGENCY",
    ),
    TribunalDefectSeed(
        decision_ref="BIR/00CW/LSC/2025/0147",
        hhsrs_hazard="Damp and Mould / Mechanical Ventilation",
        trade="ELEC",
        sor_code="212004",
        technical_narrative="Open-circuit motor winding on 100mm wall-mounted centrifugal humidistat extractor fan in bathroom.",
        colloquial_tenant_text="The bathroom humidistat extractor fan on the wall has stopped spinning completely so steam fills the whole flat.",
        urgency="ROUTINE",
    ),
    # PLAS
    TribunalDefectSeed(
        decision_ref="LON/00BH/LSC/2025/0160",
        hhsrs_hazard="Falling Elements (Plaster)",
        trade="PLAS",
        sor_code="161001",
        technical_narrative="Delaminated and perished gypsum undercoat and finish plaster (~1.5m2) to masonry wall requiring hacking off and two-coat replastering.",
        colloquial_tenant_text="A large patch of wall plaster in the hallway is blown, hollow and crumbling off the brick wall; needs hacking off and replastering.",
        urgency="ROUTINE",
    ),
    TribunalDefectSeed(
        decision_ref="MAN/00DR/LSC/2025/0174",
        hhsrs_hazard="Sanitation / Wet Area Splashback",
        trade="PLAS",
        sor_code="163002",
        technical_narrative="Loose and missing 150x150mm glazed ceramic wall tiles and perished waterproof grout around bath shower splashback.",
        colloquial_tenant_text="Several white ceramic wall tiles around the bath shower splashback have come loose and fallen off the wall.",
        urgency="ROUTINE",
    ),
]


def harvest_tribunal_seeds(trade_filter: Optional[str] = None) -> List[Dict[str, object]]:
    """Return First-tier Tribunal building defect seeds, optionally filtered by trade."""
    seeds = TRIBUNAL_DEFECT_SEEDS
    if trade_filter and trade_filter.upper() != "ALL":
        target = trade_filter.upper()
        seeds = [s for s in seeds if s.trade.upper() == target]

    return [
        {
            "decision_ref": s.decision_ref,
            "hhsrs_hazard": s.hhsrs_hazard,
            "trade": s.trade,
            "sor_code": s.sor_code,
            "technical_narrative": s.technical_narrative,
            "colloquial_tenant_text": s.colloquial_tenant_text,
            "urgency": s.urgency,
            "awaabs_law": s.awaabs_law,
        }
        for s in seeds
    ]
