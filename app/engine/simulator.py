"""Deterministic calibrated mathematical simulator for offline/repeatable TypeSafe Jev testing."""

from typing import Any, Dict, Optional
from app.domain.enums import MessageIntent, TradeCode


class SimulatedJevEngine:
    """Provides sub-millisecond calibrated Stage 1 & Stage 2 Jev responses for repeatable testing."""

    def triage_complaint(
        self,
        complaint_text: str,
        synthetic_image_preset: Optional[str] = None,
        has_image: bool = False,
        existing_job_ref: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Simulates Pass 1 multimodal evaluation across safety, intent, trade, Awaab's Law, and SLA."""
        text_lower = complaint_text.lower()
        preset = (synthetic_image_preset or "").lower()

        # 1. Content Safety Check (Inappropriate / Rude Photo or Abusive Submission)
        is_inappropriate = (
            preset == "inappropriate_placeholder"
            or any(
                kw in text_lower
                for kw in [
                    "rude/offensive photo",
                    "inappropriate photo",
                    "rude photo",
                    "explicit photo",
                    "offensive image",
                    "nsfw",
                ]
            )
        )
        if is_inappropriate:
            return {
                "engine": "typesafe-jev-simulator-v1",
                "answers": {
                    "inappropriate_content_flag": {
                        "value": True,
                        "probability": 0.96,
                    },
                    "message_intent": {
                        "value": MessageIntent.GENERAL_HOUSING_QUERY.value,
                        "probability": 0.85,
                    },
                    "primary_trade": {
                        "value": TradeCode.OTHER.value,
                        "probability": 0.91,
                    },
                    "awaabs_law_damp_hazard": {
                        "value": False,
                        "probability": 0.01,
                    },
                    "repair_priority": {
                        "value": "1",
                        "probability": 0.95,
                    },
                },
            }

        # 2. Message Intent Evaluation
        intent = MessageIntent.NEW_REPAIR_DEFECT.value
        intent_prob = 0.91

        if any(
            kw in text_lower
            for kw in [
                "accounts payable",
                "overdue payment",
                "invoice",
                "remittance",
                "late payment",
                "purchase order",
            ]
        ):
            intent = MessageIntent.CONTRACTOR_PAYMENT_INQUIRY.value
            intent_prob = 0.95
        elif any(
            kw in text_lower
            for kw in [
                "closed job",
                "marked as completed",
                "marked job",
                "came yesterday",
                "came out yesterday",
                "still leaking",
                "fitted crookedly",
                "poor workmanship",
                "botched",
                "completed repair",
            ]
        ):
            intent = MessageIntent.COMPLETED_REPAIR_COMPLAINT.value
            intent_prob = 0.92
        elif any(
            kw in text_lower
            for kw in [
                "reschedule",
                "appointment slot",
                "missed appointment",
                "book a slot",
                "thursday morning",
                "cancel my appointment",
            ]
        ):
            intent = MessageIntent.CONTRACTOR_SCHEDULING.value
            intent_prob = 0.90
        elif any(
            kw in text_lower
            for kw in [
                "work-in-progress",
                "chasing an update",
                "when is the",
                "status update",
                "coming back to finish",
                "update on my repair",
            ]
        ):
            intent = MessageIntent.WIP_REPAIR_UPDATE.value
            intent_prob = 0.89
        elif any(
            kw in text_lower
            for kw in [
                "loud music",
                "antisocial",
                "anti-social",
                "neighbour noise",
                "service charge increase",
                "fly-tipping",
                "wasps nest",
            ]
        ):
            intent = MessageIntent.GENERAL_HOUSING_QUERY.value
            intent_prob = 0.84

        # 3. Awaab's Law Damp & Mould Assessment
        damp_prob = 0.04
        damp_flag = False
        if preset == "black_mould" or any(
            kw in text_lower
            for kw in ["black mould", "mould", "damp", "fungal", "musty", "condensation"]
        ):
            damp_prob = 0.88 if ("black mould" in text_lower or preset == "black_mould") else 0.52
            damp_flag = True
        elif "pooling" in text_lower or "underneath the sink" in text_lower:
            damp_prob = 0.08
            damp_flag = False

        # 4. Emergency SLA Assessment
        priority = "1"
        priority_prob = 0.86
        if preset == "ceiling_light_leak" or any(
            kw in text_lower
            for kw in [
                "pouring",
                "sparks",
                "burst pipe",
                "ceiling rose",
                "light fitting",
                "sewage",
                "urgent!",
                "electrics",
            ]
        ):
            priority = "3"
            priority_prob = 0.94
        elif any(
            kw in text_lower
            for kw in [
                "leak",
                "cistern",
                "overflow",
                "mould",
                "broken",
                "snapped",
                "hanging off",
                "pooling",
            ]
        ):
            priority = "2"
            priority_prob = 0.91

        # 5. Primary Trade Classification (combining text + visual preset evidence)
        trade = TradeCode.OTHER.value
        trade_prob = 0.45

        if intent in (
            MessageIntent.CONTRACTOR_PAYMENT_INQUIRY.value,
            MessageIntent.GENERAL_HOUSING_QUERY.value,
        ):
            trade = TradeCode.OTHER.value
            trade_prob = 0.42
        elif preset == "ceiling_light_leak" or any(
            kw in text_lower
            for kw in [
                "light fitting",
                "ceiling rose",
                "socket",
                "smoke alarm",
                "rcd",
                "mcb",
                "rcbo",
                "consumer unit",
                "circuit breaker",
                "pull-cord",
                "pull cord",
                "light switch",
                "cooker switch",
                "fused spur",
                "pendant",
                "bulkhead",
                "floodlight",
                "carbon monoxide",
                "electric shower",
                "room thermostat",
                "storage heater",
                "intercom",
                "earth bonding",
                "eicr",
            ]
        ):
            trade = TradeCode.ELEC.value
            trade_prob = 0.89
        elif preset == "black_mould" or (
            any(
                kw in text_lower
                for kw in [
                    "black mould",
                    "mould",
                    "rising damp",
                    "dpc",
                    "damp proof",
                    "airbrick",
                    "cavity tray",
                    "tanking",
                    "humidistat",
                    "trickle vent",
                    "piv unit",
                    "positive input ventilation",
                    "wet rot",
                    "dry rot",
                    "mastic sealant",
                    "weep vent",
                    "condensation",
                ]
            )
            and "pipe" not in text_lower
        ):
            trade = TradeCode.DAMP.value
            trade_prob = 0.91
        elif preset == "broken_hinge" or any(
            kw in text_lower
            for kw in [
                "hinge",
                "cupboard door",
                "fire door",
                "handrail",
                "banister",
                "door is hanging off",
                "door closer",
                "multipoint",
                "multi-point",
                "euro cylinder",
                "espagnolette",
                "window handle",
                "window lock",
                "sash cord",
                "sash window",
                "double-glazed",
                "double glazed",
                "window sill",
                "floorboard",
                "chipboard floor",
                "skirting",
                "architrave",
                "pipe boxing",
                "worktop",
                "drawer runner",
                "kitchen drawer",
                "base unit carcass",
                "mortice",
                "deadlock",
                "nightlatch",
                "board up",
            ]
        ):
            trade = TradeCode.JOIN.value
            trade_prob = 0.87 if (has_image or preset == "broken_hinge") else (0.62 if "metal thing snapped" in text_lower else 0.86)
        elif preset in ("cistern_valve", "sink_leak") or any(
            kw in text_lower
            for kw in [
                "cistern",
                "ball valve",
                "siphon",
                "syphon",
                "sink",
                "pipe",
                "waste trap",
                "push-fit",
                "plumber",
                "toilet",
                "wc pan",
                "toilet seat",
                "wc seat",
                "stopcock",
                "isolation valve",
                "blocked bath",
                "shower waste",
                "soil stack",
                "pillar tap",
                "mixer tap",
                "radiator",
                "trv",
                "lockshield",
                "immersion heater",
                "hot water cylinder",
                "unvented cylinder",
                "tundish",
                "expansion vessel",
                "standpipe",
            ]
        ):
            trade = TradeCode.PLUM.value
            trade_prob = 0.88
        elif any(
            kw in text_lower
            for kw in [
                "roof",
                "slate",
                "ridge tile",
                "hip tile",
                "dry-verge",
                "dry verge",
                "epdm",
                "balcony deck",
                "gutter",
                "downpipe",
                "flashing",
                "chimney",
                "valley gutter",
                "fascia",
                "soffit",
                "hopper head",
                "skylight",
                "loft insulation",
                "loft hatch",
                "tarpaulin",
                "interlocking concrete",
            ]
        ):
            trade = TradeCode.ROOF.value
            trade_prob = 0.86
        elif any(
            kw in text_lower
            for kw in [
                "plaster",
                "skim",
                "ceiling board",
                "overboard",
                "angle bead",
                "artex",
                "tile backer",
                "splashback",
                "wall tile",
                "ceramic tile",
                "bellcast",
                "pebble-dash",
                "roughcast",
                "render",
                "coving",
                "screed",
                "self-levelling",
                "partition wall",
                "fire-stop",
            ]
        ):
            trade = TradeCode.PLAS.value
            trade_prob = 0.85
        elif "leak" in text_lower or "drip" in text_lower:
            trade = TradeCode.PLUM.value
            trade_prob = 0.84

        return {
            "engine": "typesafe-jev-simulator-v1",
            "answers": {
                "inappropriate_content_flag": {
                    "value": False,
                    "probability": 0.01,
                },
                "message_intent": {
                    "value": intent,
                    "probability": intent_prob,
                },
                "primary_trade": {
                    "value": trade,
                    "probability": trade_prob,
                },
                "awaabs_law_damp_hazard": {
                    "value": damp_flag,
                    "probability": damp_prob,
                },
                "repair_priority": {
                    "value": priority,
                    "probability": priority_prob,
                },
            },
        }

    @staticmethod
    def _score_candidate_sors(
        text_lower: str,
        candidate_sors: Dict[str, str],
    ) -> Optional[Dict[str, float]]:
        """Scores candidate SOR descriptions against complaint text tokens to support dynamic 20-code catalog expansion."""
        import re
        from app.domain.sor_catalog import get_sor_item

        stop_words = {
            "the", "and", "for", "with", "from", "that", "this", "have", "has", "been",
            "are", "was", "were", "into", "onto", "under", "over", "out", "our", "your",
            "my", "in", "on", "at", "to", "of", "is", "it", "or", "up", "by", "as", "an",
            "new", "old", "repair", "replace", "renew", "fix", "broken", "faulty", "damaged",
            "leaking", "leak", "water", "room", "flat", "house", "property", "please", "need",
        }
        query_tokens = {
            tok
            for tok in re.findall(r"[a-z0-9]{3,}", text_lower)
            if tok not in stop_words
        }
        if not query_tokens:
            return None

        scores: Dict[str, float] = {}
        for code, short_desc in candidate_sors.items():
            if code == "OTHER":
                continue
            item = get_sor_item(code)
            corpus_text = f"{short_desc} {item.full_specification if item else ''}".lower()
            corpus_tokens = set(re.findall(r"[a-z0-9]{3,}", corpus_text))
            matched_tokens = query_tokens.intersection(corpus_tokens)
            # Also reward exact substring matches of multi-character domain terms
            substr_bonus = sum(
                0.5 for tok in query_tokens if len(tok) >= 4 and tok in corpus_text
            )
            score = float(len(matched_tokens)) + substr_bonus
            if score > 0:
                scores[code] = score

        if not scores:
            return None

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_code, top_score = ranked[0]
        if top_score < 2.5:
            # Defect description does not sufficiently match any candidate in the current trade schedule
            return None

        top_prob = 0.86 if top_score >= 3.5 else 0.82

        dist: Dict[str, float] = {top_code: top_prob}
        non_other_codes = [c for c in candidate_sors if c != "OTHER" and c != top_code]
        if len(ranked) >= 2:
            second_code = ranked[1][0]
            dist[second_code] = 0.09
            remaining = [c for c in non_other_codes if c != second_code]
            if remaining:
                dist[remaining[0]] = 0.03
        elif non_other_codes:
            dist[non_other_codes[0]] = 0.10

        dist["OTHER"] = round(max(0.01, 1.0 - sum(dist.values())), 2)
        return dist

    def resolve_sor_code(
        self,
        complaint_text: str,
        trade: str,
        candidate_sors: Dict[str, str],
        synthetic_image_preset: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Simulates Pass 2 bounded M3NHF SOR selection with full candidate probability distribution."""
        text_lower = complaint_text.lower()
        preset = (synthetic_image_preset or "").lower()

        distribution: Optional[Dict[str, float]] = None

        # 1. Exact Preset & Golden Baseline deterministic rules
        if trade == TradeCode.PLUM.value:
            if "not sure if it is coming from the copper supply pipe" in text_lower or (
                "pooling" in text_lower and "push-fit" not in text_lower
            ):
                # Preset 2: Ambiguous SOR margin between 192001 (0.54) and 192005 (0.44)
                distribution = {
                    "192001": 0.54,
                    "192005": 0.44,
                    "194010": 0.01,
                    "195020": 0.00,
                    "OTHER": 0.01,
                }
            elif "cistern" in text_lower or "ball valve" in text_lower or preset == "cistern_valve":
                distribution = {
                    "194010": 0.86,
                    "192001": 0.07,
                    "192005": 0.04,
                    "195020": 0.01,
                    "OTHER": 0.02,
                }
            elif "push-fit" in text_lower or "waste" in text_lower or "trap" in text_lower:
                distribution = {
                    "192005": 0.84,
                    "192001": 0.11,
                    "194010": 0.02,
                    "195020": 0.01,
                    "OTHER": 0.02,
                }
            elif "burst" in text_lower:
                distribution = {
                    "195020": 0.89,
                    "192001": 0.08,
                    "192005": 0.01,
                    "194010": 0.01,
                    "OTHER": 0.01,
                }
            elif "supply pipe" in text_lower or "copper" in text_lower:
                distribution = {
                    "192001": 0.78,
                    "192005": 0.14,
                    "194010": 0.04,
                    "195020": 0.02,
                    "OTHER": 0.02,
                }

        elif trade == TradeCode.DAMP.value:
            if preset == "black_mould" or "black mould" in text_lower or "fungicidal" in text_lower:
                distribution = {"114001": 0.87, "114010": 0.08, "112005": 0.03, "OTHER": 0.02}
            elif "dpc" in text_lower or "rising damp" in text_lower or "chemical" in text_lower:
                distribution = {"112005": 0.85, "114001": 0.08, "112015": 0.04, "OTHER": 0.03}
            elif "repoint" in text_lower or ("brickwork" in text_lower and "cavity" not in text_lower):
                distribution = {"112015": 0.81, "114001": 0.12, "114010": 0.04, "OTHER": 0.03}
            elif "humidistat" in text_lower or ("extract fan" in text_lower and "duct" not in text_lower):
                distribution = {"114010": 0.83, "114001": 0.11, "112015": 0.03, "OTHER": 0.03}

        elif trade == TradeCode.ELEC.value:
            if "ceiling rose" in text_lower or "light fitting" in text_lower or preset == "ceiling_light_leak":
                distribution = {"211001": 0.91, "212015": 0.04, "214002": 0.02, "OTHER": 0.03}
            elif "smoke" in text_lower or ("alarm" in text_lower and "carbon" not in text_lower):
                distribution = {"214002": 0.88, "212015": 0.06, "211001": 0.03, "OTHER": 0.03}
            elif "socket" in text_lower and "cooker" not in text_lower:
                distribution = {"212015": 0.82, "211001": 0.09, "214002": 0.05, "OTHER": 0.04}

        elif trade == TradeCode.JOIN.value:
            if preset == "broken_hinge" or "cupboard door" in text_lower or "hinge" in text_lower or "hanging off" in text_lower:
                distribution = {"125011": 0.85, "121008": 0.09, "123020": 0.03, "OTHER": 0.03}
            elif ("fire door" in text_lower and "closer" not in text_lower) or "intumescent" in text_lower:
                distribution = {"121008": 0.84, "125011": 0.08, "123020": 0.05, "OTHER": 0.03}
            elif "handrail" in text_lower or "banister" in text_lower or "spindle" in text_lower:
                distribution = {"123020": 0.80, "121008": 0.11, "125011": 0.05, "OTHER": 0.04}

        elif trade == TradeCode.ROOF.value:
            if ("gutter" in text_lower or "downpipe" in text_lower) and "valley" not in text_lower and "hopper" not in text_lower and "shoe" not in text_lower:
                distribution = {"105012": 0.84, "101004": 0.12, "OTHER": 0.04}
            elif "interlocking" in text_lower or "concrete roof tile" in text_lower or "slipped tile" in text_lower:
                distribution = {"101004": 0.83, "105012": 0.13, "OTHER": 0.04}

        elif trade == TradeCode.PLAS.value:
            if "overboard" in text_lower or "bowed" in text_lower or "water-damaged plasterboard ceiling" in text_lower:
                distribution = {"162008": 0.82, "161002": 0.14, "OTHER": 0.04}
            elif "blown wall plaster" in text_lower or "hack off blown" in text_lower:
                distribution = {"161002": 0.81, "162008": 0.15, "OTHER": 0.04}

        # 2. Dynamic Candidate Scoring against active M3NHF_SOR_CATALOG[trade]
        if distribution is None:
            scored_dist = self._score_candidate_sors(text_lower, candidate_sors)
            if scored_dist is not None:
                distribution = scored_dist
            else:
                # No candidate SOR in the currently loaded schedule matched the complaint -> fallback to OTHER
                non_other = [c for c in candidate_sors if c != "OTHER"]
                distribution = {"OTHER": 0.78}
                if non_other:
                    share = round(0.22 / min(len(non_other), 3), 2)
                    for c in non_other[:3]:
                        distribution[c] = share

        # Filter to only keys present in candidate_sors if custom candidate dict was provided
        filtered_dist = {k: v for k, v in distribution.items() if k in candidate_sors}
        if not filtered_dist:
            first_key = next(iter(candidate_sors.keys()), "OTHER")
            filtered_dist = {first_key: 1.0}

        top_sor = max(filtered_dist.items(), key=lambda item: item[1])[0]
        top_prob = filtered_dist[top_sor]

        return {
            "engine": "typesafe-jev-simulator-v1",
            "answers": {
                "selected_sor": {
                    "value": top_sor,
                    "probability": top_prob,
                    "distribution": filtered_dist,
                }
            },
        }

