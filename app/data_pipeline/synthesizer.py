"""
Stratified Ground-Truth Dataset Synthesizer (Phase 4).

Generates a stratified dataset of UK social housing complaints (default N=500)
matching UK Housing Ombudsman macro-intent distributions (~60% Property Condition
repairs across PLUM, DAMP, ROOF, JOIN, ELEC, PLAS; ~18% ASB; ~14% Escalation;
~8% Rent/Service Charge) with ground-truth M3NHF v8 SOR codes and Awaab's Law flags.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.data_pipeline.ombudsman_harvester import harvest_ombudsman_determinations
from app.data_pipeline.reddit_normalizer import build_colloquial_tenant_narrative
from app.data_pipeline.taxonomy import (
    OMBUDSMAN_INTENT_DISTRIBUTION,
    REPAIR_TRADE_DISTRIBUTION,
    build_extended_m3nhf_sor_feed,
    get_feed_sors_for_trade,
)
from app.data_pipeline.tribunal_harvester import harvest_tribunal_seeds


NON_REPAIR_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "ASB": [
        {
            "text": "The tenant in Flat 6B is playing loud bass music until 3:30am every night, shouting in the communal stairwell and intimidating neighbours.",
            "urgency": "URGENT",
            "expected_routing_action": "ESC_HOUSING_OFFICER",
        },
        {
            "text": "Fly-tipping of mattresses and bin bags in the communal bin store plus constant dog barking and harassment from next door.",
            "urgency": "ROUTINE",
            "expected_routing_action": "ESC_HOUSING_OFFICER",
        },
    ],
    "ESCALATION": [
        {
            "text": "I submitted a formal Stage 1 complaint three weeks ago (ref CMP-904) about missed repair appointments and nobody has replied. I want to escalate to Stage 2 and the Housing Ombudsman.",
            "urgency": "URGENT",
            "expected_routing_action": "ESC_COMPLIANCE_TEAM",
        },
        {
            "text": "Formal complaint regarding maladministration and lack of compensation after my family was left without hot water for 9 days.",
            "urgency": "URGENT",
            "expected_routing_action": "ESC_COMPLIANCE_TEAM",
        },
    ],
    "RENT_SERVICE_CHARGE": [
        {
            "text": "I am disputing the £420 communal grounds maintenance service charge on my quarterly statement and need an affordable arrears payment plan while Universal Credit is reassessed.",
            "urgency": "ROUTINE",
            "expected_routing_action": "ESC_INCOME_TEAM",
        },
        {
            "text": "My Direct Debit rent payment was taken twice this month leaving my rent account in credit; please refund or adjust my rent statement.",
            "urgency": "ROUTINE",
            "expected_routing_action": "ESC_INCOME_TEAM",
        },
    ],
}


def generate_stratified_dataset(
    total_samples: int = 500,
    seed: int = 42,
    use_extended_feed: bool = True,
) -> List[Dict[str, Any]]:
    """
    Generate `total_samples` stratified UK social housing complaint records.

    Distributions:
    - 60% REPAIR (stratified across PLUM 30%, DAMP 25%, JOIN 15%, ELEC 12%, ROOF 10%, PLAS 8%)
    - 18% ASB
    - 14% ESCALATION
    - 8% RENT_SERVICE_CHARGE
    """
    rng = random.Random(seed)
    extended_feed = build_extended_m3nhf_sor_feed()

    repair_count = round(total_samples * 0.60)
    asb_count = round(total_samples * 0.18)
    esc_count = round(total_samples * 0.14)
    rent_count = max(0, total_samples - (repair_count + asb_count + esc_count))

    records: List[Dict[str, Any]] = []
    channels = ["WEB_PORTAL", "WHATSAPP", "EMAIL", "VOICE_TRANSCRIPT"]

    # 1. Generate REPAIR records stratified by trade
    allocated_repairs = 0
    trades = list(REPAIR_TRADE_DISTRIBUTION.keys())
    for idx, trade in enumerate(trades):
        trade_name = trade.value if hasattr(trade, "value") else str(trade)
        if idx == len(trades) - 1:
            trade_n = max(0, repair_count - allocated_repairs)
        else:
            trade_n = round(repair_count * REPAIR_TRADE_DISTRIBUTION[trade])
            allocated_repairs += trade_n

        trade_sors = get_feed_sors_for_trade(trade, max_codes=20)
        tribunal_seeds = harvest_tribunal_seeds(trade_filter=trade_name)

        for i in range(trade_n):
            sor_item = trade_sors[i % len(trade_sors)]
            sor_code = sor_item.sor_code
            sor_desc = sor_item.short_description
            default_prio = (
                "EMERGENCY"
                if sor_item.default_sla_priority == "3"
                else ("URGENT" if sor_item.default_sla_priority == "2" else "ROUTINE")
            )
            is_awaab = bool(trade_name == "DAMP" and sor_code in ("111002", "114001") and (i % 3 == 0))
            include_vuln = is_awaab or (i % 5 == 0)

            # Mix curated Tribunal colloquial narratives with normalizer narratives
            matching_tribunal = [t for t in tribunal_seeds if t["sor_code"] == sor_code]
            if matching_tribunal and i < len(matching_tribunal):
                complaint_text = str(matching_tribunal[i]["colloquial_tenant_text"])
            else:
                complaint_text = build_colloquial_tenant_narrative(
                    sor_code=sor_code,
                    sor_description=sor_desc,
                    trade=trade_name,
                    rng=rng,
                    include_vulnerability=include_vuln,
                    awaabs_law=is_awaab,
                )

            expected_routing = (
                "ESC_AWAABS_LAW_TASKFORCE"
                if is_awaab
                else (
                    "ESC_EMERGENCY_CONTRACTOR"
                    if default_prio == "EMERGENCY"
                    else "AUTO_DISPATCH_HMS"
                )
            )

            records.append(
                {
                    "sample_id": f"SYN-{len(records) + 1:04d}",
                    "tenant_id": f"TEN-{10000 + len(records)}",
                    "channel": rng.choice(channels),
                    "complaint_text": complaint_text,
                    "ground_truth": {
                        "primary_intent": "REPAIR",
                        "trade": trade_name,
                        "expected_sor_code": sor_code,
                        "sor_description": sor_desc,
                        "expected_priority": "EMERGENCY" if is_awaab else default_prio,
                        "awaabs_law_trigger": is_awaab,
                        "expected_routing_action": expected_routing,
                    },
                }
            )

    # 2. Generate non-repair records (ASB, ESCALATION, RENT_SERVICE_CHARGE)
    non_repair_plan = [
        ("ASB", asb_count),
        ("ESCALATION", esc_count),
        ("RENT_SERVICE_CHARGE", rent_count),
    ]
    for intent, count in non_repair_plan:
        templates = NON_REPAIR_TEMPLATES[intent]
        for i in range(count):
            tpl = templates[i % len(templates)]
            records.append(
                {
                    "sample_id": f"SYN-{len(records) + 1:04d}",
                    "tenant_id": f"TEN-{10000 + len(records)}",
                    "channel": rng.choice(channels),
                    "complaint_text": tpl["text"],
                    "ground_truth": {
                        "primary_intent": intent,
                        "trade": intent,
                        "expected_sor_code": "N/A",
                        "sor_description": "Non-repair housing management workflow",
                        "expected_priority": tpl["urgency"],
                        "awaabs_law_trigger": False,
                        "expected_routing_action": tpl["expected_routing_action"],
                    },
                }
            )

    rng.shuffle(records)
    return records


def write_dataset_jsonl(
    output_path: Path,
    total_samples: int = 500,
    seed: int = 42,
) -> Dict[str, Any]:
    """Generate stratified dataset and persist to a JSONL file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    records = generate_stratified_dataset(total_samples=total_samples, seed=seed)
    with output_path.open("w", encoding="utf-8") as fh:
        for row in records:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    intent_counts: Dict[str, int] = {}
    trade_counts: Dict[str, int] = {}
    for row in records:
        gt = row["ground_truth"]
        intent = gt["primary_intent"]
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
        if intent == "REPAIR":
            tr = gt["trade"]
            trade_counts[tr] = trade_counts.get(tr, 0) + 1

    return {
        "output_path": str(output_path),
        "total_samples": len(records),
        "intent_counts": intent_counts,
        "repair_trade_counts": trade_counts,
        "ombudsman_seed_count": len(harvest_ombudsman_determinations()),
    }
