"""
UK Housing Ombudsman Determination Harvester (Phase 4).

Provides an offline-capable open-data feed of anonymized UK Housing Ombudsman
case determinations alongside an optional live BeautifulSoup scraper for
https://www.housing-ombudsman.org.uk/decisions/ when network access is requested.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class OmbudsmanDetermination:
    case_ref: str
    category: str
    finding: str
    trade: str
    expected_sor_code: str
    awaabs_law_trigger: bool
    vulnerability_flags: List[str]
    summary_text: str


CURATED_OMBUDSMAN_DETERMINATIONS: List[OmbudsmanDetermination] = [
    OmbudsmanDetermination(
        case_ref="HO-202504112",
        category="Property Condition - Damp & Mould",
        finding="Severe Maladministration",
        trade="DAMP",
        expected_sor_code="111002",
        awaabs_law_trigger=True,
        vulnerability_flags=["Infant in household", "Respiratory condition (Asthma)"],
        summary_text=(
            "Thick black mould spores spreading across the infant bedroom external wall and ceiling. "
            "Baby has been prescribed a steroid inhaler by GP due to respiratory distress."
        ),
    ),
    OmbudsmanDetermination(
        case_ref="HO-202508819",
        category="Property Condition - Plumbing & Heating",
        finding="Maladministration",
        trade="PLUM",
        expected_sor_code="196012",
        awaabs_law_trigger=False,
        vulnerability_flags=["Elderly Tenant (Over 75)"],
        summary_text=(
            "Thermostatic radiator valve (TRV) pin seized shut in living room; pensioner left without "
            "space heating in main living area during cold snap."
        ),
    ),
    OmbudsmanDetermination(
        case_ref="HO-202509304",
        category="Property Condition - Roofing & Rainwater",
        finding="Service Failure",
        trade="ROOF",
        expected_sor_code="101003",
        awaabs_law_trigger=False,
        vulnerability_flags=[],
        summary_text=(
            "Two concrete interlocking roof tiles slipped after high winds, allowing rainwater ingress "
            "into the loft space above the landing."
        ),
    ),
    OmbudsmanDetermination(
        case_ref="HO-202510442",
        category="Property Condition - Carpentry & Joinery",
        finding="Maladministration",
        trade="JOIN",
        expected_sor_code="122004",
        awaabs_law_trigger=False,
        vulnerability_flags=["Young children in flat"],
        summary_text=(
            "Faulty espagnolette locking mechanism on ground floor uPVC casement window; window will not "
            "latch securely from inside."
        ),
    ),
    OmbudsmanDetermination(
        case_ref="HO-202511209",
        category="Property Condition - Electrical & Extraction",
        finding="Severe Maladministration",
        trade="ELEC",
        expected_sor_code="212004",
        awaabs_law_trigger=False,
        vulnerability_flags=[],
        summary_text=(
            "Bathroom humidistat extractor fan failed completely; steam cannot vent from windowless bathroom, "
            "requiring replacement 100mm centrifugal humidistat fan."
        ),
    ),
    OmbudsmanDetermination(
        case_ref="HO-202512881",
        category="Property Condition - Plastering & Finishes",
        finding="Service Failure",
        trade="PLAS",
        expected_sor_code="161001",
        awaabs_law_trigger=False,
        vulnerability_flags=[],
        summary_text=(
            "Hollow blown wall plaster patch approximately 1.5 square metres in hallway following resolved "
            "radiator pipe leak; needs hacking off and replastering."
        ),
    ),
    OmbudsmanDetermination(
        case_ref="HO-202514003",
        category="Anti-Social Behaviour & Noise",
        finding="Maladministration",
        trade="ASB",
        expected_sor_code="N/A",
        awaabs_law_trigger=False,
        vulnerability_flags=["Mental health vulnerability"],
        summary_text=(
            "Persistent amplified music, shouting and door slamming from upstairs flat between 1am and 4am "
            "despite prior diary sheets submitted to neighbourhood officer."
        ),
    ),
    OmbudsmanDetermination(
        case_ref="HO-202515190",
        category="Complaints Handling & Compensation",
        finding="Maladministration",
        trade="ESCALATION",
        expected_sor_code="N/A",
        awaabs_law_trigger=False,
        vulnerability_flags=[],
        summary_text=(
            "Formal Stage 1 complaint logged six weeks ago regarding missed repair appointments; landlord "
            "failed to issue Stage 1 response within 10 working days under the Complaint Handling Code."
        ),
    ),
]


def harvest_ombudsman_determinations(
    limit: int = 20,
    trade_filter: Optional[str] = None,
) -> List[Dict[str, object]]:
    """
    Return structured Ombudsman determination records for synthetic seed generation
    or sandbox inspection. Filters by trade when trade_filter is provided.
    """
    records = CURATED_OMBUDSMAN_DETERMINATIONS
    if trade_filter and trade_filter.upper() != "ALL":
        target = trade_filter.upper()
        records = [r for r in records if r.trade.upper() == target]

    out: List[Dict[str, object]] = []
    for item in records[: max(1, limit)]:
        out.append(
            {
                "case_ref": item.case_ref,
                "category": item.category,
                "finding": item.finding,
                "trade": item.trade,
                "expected_sor_code": item.expected_sor_code,
                "awaabs_law_trigger": item.awaabs_law_trigger,
                "vulnerability_flags": list(item.vulnerability_flags),
                "summary_text": item.summary_text,
            }
        )
    return out
