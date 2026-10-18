"""
Colloquial UK Tenant Narrative Normalizer (Phase 4).

Transforms informal UK tenant phrasing (inspired by r/HousingUK, r/LegalAdviceUK,
WhatsApp voice-notes, and web forms) into realistic test complaints while preserving
colloquialisms that challenge the 2-pass neuro-symbolic triage pipeline.
"""
from __future__ import annotations

import random
from typing import Dict, List


UK_COLLOQUIAL_OPENERS: List[str] = [
    "Hiya, sorry to bother you again but",
    "Honestly at my wits' end here —",
    "Quick update from Flat 4B:",
    "Reporting a repair needed ASAP:",
    "Hello housing team, please can someone come out because",
    "Been trying to get through on the phone all morning —",
]

UK_COLLOQUIAL_CLOSERS: List[str] = [
    "Cheers, appreciate someone sorting a works order.",
    "Please let me know when an operative can attend.",
    "It's getting worse every day, thanks.",
    "Can you text me the appointment slot please?",
    "Thanks in advance.",
]

COLLOQUIAL_SLANG_SYNONYMS: Dict[str, List[str]] = {
    "radiator": ["rad", "radiator"],
    "toilet": ["loo", "toilet", "WC"],
    "Consumer Unit": ["fuse box", "consumer unit", "trip switch box"],
    "extractor fan": ["extractor fan", "vent fan"],
    "plaster": ["plaster", "skimming"],
}


def build_colloquial_tenant_narrative(
    sor_code: str,
    sor_description: str,
    trade: str,
    rng: random.Random,
    include_vulnerability: bool = False,
    awaabs_law: bool = False,
) -> str:
    """
    Construct a realistic UK tenant complaint narrative that describes the defect
    covered by `sor_description` in natural, everyday tenant language without
    ever mentioning the numeric SOR code itself.
    """
    opener = rng.choice(UK_COLLOQUIAL_OPENERS)
    closer = rng.choice(UK_COLLOQUIAL_CLOSERS)

    # Convert formal M3NHF schedule wording into natural tenant description
    desc_clean = sor_description.strip().rstrip(".")
    desc_lower = desc_clean[0].lower() + desc_clean[1:] if desc_clean else "a repair issue"

    trade_context = {
        "PLUM": "in our kitchen/bathroom plumbing",
        "DAMP": "on the bedroom and hallway walls",
        "ROOF": "up on the roof and guttering",
        "JOIN": "with the doors, locks and windows",
        "ELEC": "with the electrics and switches",
        "PLAS": "with the wall and ceiling plasterwork",
    }.get(trade.upper(), "in the property")

    if awaabs_law:
        return (
            f"{opener} there is severe damp and black mould spores growing {trade_context} "
            f"(we urgently need someone to {desc_lower}). My 14-month-old baby is coughing "
            f"all night with asthma and the GP said the damp hazard is dangerous. {closer}"
        )

    vuln_clause = ""
    if include_vulnerability:
        vuln_clause = rng.choice(
            [
                " My elderly mum (81) lives here and has mobility issues.",
                " We have a newborn baby in the flat so we are really worried.",
                " I am disabled and rely on this being safe.",
            ]
        )

    return (
        f"{opener} we have a fault {trade_context} where we need a contractor to "
        f"{desc_lower}.{vuln_clause} {closer}"
    )
