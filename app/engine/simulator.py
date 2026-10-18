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
        elif preset == "ceiling_light_leak" or (
            "light fitting" in text_lower or "ceiling rose" in text_lower or "socket" in text_lower or "smoke alarm" in text_lower
        ):
            trade = TradeCode.ELEC.value
            trade_prob = 0.89
        elif preset == "black_mould" or ("black mould" in text_lower and "pipe" not in text_lower):
            trade = TradeCode.DAMP.value
            trade_prob = 0.91
        elif preset == "broken_hinge" or any(
            kw in text_lower
            for kw in ["hinge", "cupboard door", "fire door", "handrail", "banister", "door is hanging off"]
        ):
            trade = TradeCode.JOIN.value
            # Notice how having an image boosts confidence on vague text ("metal thing snapped")
            trade_prob = 0.87 if (has_image or preset == "broken_hinge") else 0.62
        elif preset in ("cistern_valve", "sink_leak") or any(
            kw in text_lower
            for kw in ["cistern", "ball valve", "siphon", "sink", "pipe", "waste trap", "leak", "plumber", "toilet"]
        ):
            trade = TradeCode.PLUM.value
            trade_prob = 0.88
        elif any(
            kw in text_lower for kw in ["roof", "tile", "gutter", "downpipe", "flashing"]
        ):
            trade = TradeCode.ROOF.value
            trade_prob = 0.86
        elif any(
            kw in text_lower for kw in ["plaster", "skim", "ceiling board"]
        ):
            trade = TradeCode.PLAS.value
            trade_prob = 0.83

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

        distribution: Dict[str, float] = {code: 0.02 for code in candidate_sors}

        if trade == TradeCode.PLUM.value:
            if "not sure if it is coming from the copper supply pipe" in text_lower or (
                "pooling" in text_lower and "push-fit" not in text_lower
            ):
                # Preset 2: Ambiguous SOR margin between 112001 (0.54) and 112005 (0.44)
                distribution = {
                    "112001": 0.54,
                    "112005": 0.44,
                    "114010": 0.01,
                    "115020": 0.00,
                    "OTHER": 0.01,
                }
            elif "cistern" in text_lower or "ball valve" in text_lower or preset == "cistern_valve":
                distribution = {
                    "114010": 0.86,
                    "112001": 0.07,
                    "112005": 0.04,
                    "115020": 0.01,
                    "OTHER": 0.02,
                }
            elif "push-fit" in text_lower or "waste" in text_lower or "trap" in text_lower:
                distribution = {
                    "112005": 0.84,
                    "112001": 0.11,
                    "114010": 0.02,
                    "115020": 0.01,
                    "OTHER": 0.02,
                }
            elif "burst" in text_lower:
                distribution = {
                    "115020": 0.89,
                    "112001": 0.08,
                    "112005": 0.01,
                    "114010": 0.01,
                    "OTHER": 0.01,
                }
            else:
                distribution = {
                    "112001": 0.78,
                    "112005": 0.14,
                    "114010": 0.04,
                    "115020": 0.02,
                    "OTHER": 0.02,
                }

        elif trade == TradeCode.DAMP.value:
            if "repoint" in text_lower or "brickwork" in text_lower:
                distribution = {"242005": 0.81, "241001": 0.12, "241010": 0.04, "OTHER": 0.03}
            elif "fan" in text_lower or "humidistat" in text_lower:
                distribution = {"241010": 0.83, "241001": 0.11, "242005": 0.03, "OTHER": 0.03}
            else:
                distribution = {"241001": 0.87, "241010": 0.08, "242005": 0.03, "OTHER": 0.02}

        elif trade == TradeCode.ELEC.value:
            if "ceiling rose" in text_lower or "light fitting" in text_lower or preset == "ceiling_light_leak":
                distribution = {"611001": 0.91, "612015": 0.04, "614002": 0.02, "OTHER": 0.03}
            elif "smoke" in text_lower or "alarm" in text_lower:
                distribution = {"614002": 0.88, "612015": 0.06, "611001": 0.03, "OTHER": 0.03}
            else:
                distribution = {"612015": 0.82, "611001": 0.09, "614002": 0.05, "OTHER": 0.04}

        elif trade == TradeCode.JOIN.value:
            if preset == "broken_hinge" or "kitchen" in text_lower or "hinge" in text_lower or "hanging off" in text_lower:
                distribution = {"415011": 0.85, "411008": 0.09, "413020": 0.03, "OTHER": 0.03}
            elif "fire door" in text_lower or "intumescent" in text_lower:
                distribution = {"411008": 0.84, "415011": 0.08, "413020": 0.05, "OTHER": 0.03}
            else:
                distribution = {"413020": 0.80, "411008": 0.11, "415011": 0.05, "OTHER": 0.04}

        elif trade == TradeCode.ROOF.value:
            if "gutter" in text_lower or "downpipe" in text_lower:
                distribution = {"315012": 0.84, "311004": 0.12, "OTHER": 0.04}
            else:
                distribution = {"311004": 0.83, "315012": 0.13, "OTHER": 0.04}

        elif trade == TradeCode.PLAS.value:
            if "ceiling" in text_lower or "overboard" in text_lower:
                distribution = {"512008": 0.82, "511002": 0.14, "OTHER": 0.04}
            else:
                distribution = {"511002": 0.81, "512008": 0.15, "OTHER": 0.04}

        else:
            distribution = {"OTHER": 0.92}

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
