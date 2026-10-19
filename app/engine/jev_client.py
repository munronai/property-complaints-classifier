"""Live TypeSafe Jev Multimodal Decision Engine client."""

import os
from typing import Any, Dict, Optional, Tuple
import uuid
import requests

from app.config import settings
from app.domain.schemas import ImageTelemetry
from app.domain.sor_catalog import (
    MESSAGE_INTENT_CRITERIA,
    REPAIR_PRIORITY_SCORE_CRITERIA,
    TRADE_CRITERIA,
)
from app.engine.image_normalizer import prepare_image_for_jev


class JevRepairsTriageEngine:
    """Multi-stage TypeSafe Jev decision engine supporting multimodal text + image evaluation."""

    API_URL = settings.typesafe_api_url

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        raw_key = (
            api_key
            if api_key is not None
            else os.environ.get("TYPESAFE_API_KEY", settings.typesafe_api_key)
        )
        self.api_key = str(raw_key).strip().strip('"').strip("'") if raw_key else ""
        if not self.api_key:
            raise ValueError("TypeSafe API Key must be set for Live Jev mode.")
        if api_url:
            self.API_URL = api_url

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "TypeSafe-Danger-Zone-Images": "true",
            }
        )

    def _prepare_image(self, image_source: Any) -> Tuple[str, str, ImageTelemetry]:
        """Normalizes image orientation (EXIF), RGB mode, and <=1568px longest edge."""
        return prepare_image_for_jev(image_source)

    @staticmethod
    def build_stage1_schema() -> Dict[str, Any]:
        """Builds the structured Stage 1 TypeSafe Jev question schema conforming to /v1/systemone."""
        return {
            "inappropriate_content_flag": {
                "type": "noul",
                "instructions": (
                    "Does the attached image or text contain explicit, rude, graphic, offensive, "
                    "or abusive content inappropriate for a housing repairs system?"
                ),
                "criteria": {
                    "true": "Contains explicit, offensive, abusive, or inappropriate content",
                    "false": "Standard resident complaint or description of property disrepair",
                },
            },
            "message_intent": {
                "type": "choice",
                "instructions": (
                    "Determine whether this message is reporting a new physical defect, complaining "
                    "about the workmanship of a completed repair job, chasing a work-in-progress (WIP) "
                    "repair update, scheduling a contractor slot, or chasing contractor invoice payment."
                ),
                "criteria": MESSAGE_INTENT_CRITERIA,
            },
            "primary_trade": {
                "type": "choice",
                "instructions": (
                    "Identify the primary trade required to inspect and repair the reported defect "
                    "based on description and visual evidence."
                ),
                "criteria": TRADE_CRITERIA,
            },
            "awaabs_law_damp_hazard": {
                "type": "noul",
                "instructions": (
                    "Does the report indicate or depict visible black mould, heavy damp ingress, "
                    "or a health hazard under Awaab's Law standards?"
                ),
                "criteria": {
                    "true": "Depicts or describes visible black mould, heavy damp, or asthma/respiratory health hazard",
                    "false": "No visible mould or severe damp hazard reported",
                },
            },
            "repair_priority": {
                "type": "score",
                "instructions": (
                    "Determine the response SLA priority level based on immediate danger, total loss of amenity, "
                    "or routine degradation."
                ),
                "criteria": REPAIR_PRIORITY_SCORE_CRITERIA,
            },
        }

    @staticmethod
    def build_stage2_schema(candidate_sors: Dict[str, str]) -> Dict[str, Any]:
        """Builds the structured Stage 2 TypeSafe Jev M3NHF SOR selection schema."""
        return {
            "selected_sor": {
                "type": "choice",
                "instructions": (
                    "Select the most accurate M3NHF Schedule of Rates (SOR) code that remedies "
                    "this specific defect."
                ),
                "criteria": candidate_sors,
            }
        }

    @staticmethod
    def _normalize_stage1_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes official TypeSafe AI /v1/systemone answers into pipeline structure."""
        raw_answers = data.get("answers", data.get("results", data))

        # 1. Inappropriate Content (noul: 0..1 probability)
        inapp_raw = raw_answers.get("inappropriate_content_flag", {})
        if isinstance(inapp_raw, dict):
            inapp_prob = float(
                inapp_raw.get("noul", inapp_raw.get("probability", inapp_raw.get("true_prob", 0.0)))
            )
            inapp_val = bool(inapp_raw.get("value", inapp_prob >= 0.50))
        elif isinstance(inapp_raw, (int, float)):
            inapp_prob = float(inapp_raw)
            inapp_val = inapp_prob >= 0.50
        else:
            inapp_prob = 0.0
            inapp_val = False

        # 2. Message Intent (choice)
        intent_raw = raw_answers.get("message_intent", {})
        if isinstance(intent_raw, dict):
            intent_val = str(
                intent_raw.get(
                    "choice",
                    intent_raw.get("top_choice", intent_raw.get("value", "NEW_REPAIR_DEFECT")),
                )
            )
            intent_dist = intent_raw.get("distribution", intent_raw.get("probabilities", {}))
            intent_prob = float(intent_dist.get(intent_val, intent_raw.get("probability", 0.90)))
        else:
            intent_val = str(intent_raw)
            intent_dist = {intent_val: 1.0}
            intent_prob = 1.0

        # 3. Primary Trade (choice)
        trade_raw = raw_answers.get("primary_trade", {})
        if isinstance(trade_raw, dict):
            trade_val = str(
                trade_raw.get(
                    "choice",
                    trade_raw.get("top_choice", trade_raw.get("value", "OTHER")),
                )
            )
            trade_dist = trade_raw.get("distribution", trade_raw.get("probabilities", {}))
            trade_prob = float(trade_dist.get(trade_val, trade_raw.get("probability", 0.85)))
        else:
            trade_val = str(trade_raw)
            trade_dist = {trade_val: 1.0}
            trade_prob = 1.0

        # 4. Awaab's Law Damp Risk (noul: 0..1 probability)
        damp_raw = raw_answers.get("awaabs_law_damp_hazard", {})
        if isinstance(damp_raw, dict):
            damp_prob = float(
                damp_raw.get("noul", damp_raw.get("probability", damp_raw.get("true_prob", 0.0)))
            )
            damp_val = bool(damp_raw.get("value", damp_prob >= 0.40))
        elif isinstance(damp_raw, (int, float)):
            damp_prob = float(damp_raw)
            damp_val = damp_prob >= 0.40
        else:
            damp_prob = 0.0
            damp_val = False

        # 5. Repair Priority (score: 0..2)
        prio_raw = raw_answers.get("repair_priority", {})
        if isinstance(prio_raw, dict) and "score" in prio_raw:
            raw_score = float(prio_raw["score"])
            level_idx = max(0, min(2, int(round(raw_score))))
            prio_val = str(level_idx + 1)  # "1", "2", "3"
            prio_prob = round(max(0.60, min(0.99, 1.0 - abs(raw_score - level_idx) * 0.2)), 4)
        elif isinstance(prio_raw, dict):
            prio_val = str(prio_raw.get("value", "1"))
            prio_prob = float(prio_raw.get("probability", 0.80))
            raw_score = float(int(prio_val) - 1) if prio_val.isdigit() else 0.0
        else:
            prio_val = str(prio_raw)
            prio_prob = 0.80
            raw_score = 0.0

        return {
            "engine": "typesafe-jev-live",
            "answers": {
                "inappropriate_content_flag": {
                    "value": inapp_val,
                    "probability": inapp_prob,
                    "noul": inapp_prob,
                },
                "message_intent": {
                    "value": intent_val,
                    "choice": intent_val,
                    "probability": intent_prob,
                    "distribution": intent_dist,
                },
                "primary_trade": {
                    "value": trade_val,
                    "choice": trade_val,
                    "probability": trade_prob,
                    "distribution": trade_dist,
                },
                "awaabs_law_damp_hazard": {
                    "value": damp_val,
                    "probability": damp_prob,
                    "noul": damp_prob,
                },
                "repair_priority": {
                    "value": prio_val,
                    "probability": prio_prob,
                    "score": raw_score,
                },
            },
            "raw_response": data,
        }

    @staticmethod
    def _normalize_stage2_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes official TypeSafe AI /v1/systemone Stage 2 answers into pipeline structure."""
        raw_answers = data.get("answers", data.get("results", data))
        sor_raw = raw_answers.get("selected_sor", {})

        if isinstance(sor_raw, dict):
            sor_val = str(
                sor_raw.get(
                    "choice",
                    sor_raw.get("top_choice", sor_raw.get("value", "OTHER")),
                )
            )
            sor_dist = sor_raw.get("distribution", sor_raw.get("probabilities", {}))
            if sor_dist and sor_val in sor_dist:
                sor_prob = float(sor_dist[sor_val])
            else:
                sor_prob = float(sor_raw.get("probability", 0.85))
                if not sor_dist:
                    sor_dist = {sor_val: sor_prob}
        else:
            sor_val = str(sor_raw)
            sor_prob = 0.85
            sor_dist = {sor_val: 0.85}

        return {
            "engine": "typesafe-jev-live",
            "answers": {
                "selected_sor": {
                    "value": sor_val,
                    "choice": sor_val,
                    "probability": sor_prob,
                    "distribution": sor_dist,
                }
            },
            "raw_response": data,
        }

    def triage_complaint(
        self,
        complaint_text: str,
        image_source: Optional[Any] = None,
        existing_job_ref: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Pass 1: Executes multimodal classification for content safety, intent, trade, urgency, and Awaab's Law risk."""
        assets: Dict[str, Any] = {}
        state: Dict[str, Any] = {"resident_description": complaint_text}
        if existing_job_ref:
            state["existing_job_reference"] = existing_job_ref

        if image_source is not None:
            asset_ref = f"asset-{uuid.uuid4().hex[:8]}"
            b64_data, fmt, _ = self._prepare_image(image_source)
            format_clean = "png" if "png" in str(fmt).lower() else "jpeg"
            assets[asset_ref] = {
                "data_base64": b64_data,
                "format": format_clean,
            }
            state["attached_evidence"] = asset_ref

        payload: Dict[str, Any] = {
            "model": os.getenv("TYPESAFE_MODEL", "jev-latest"),
            "state": state,
            "questions": self.build_stage1_schema(),
        }
        if assets:
            payload["assets"] = assets

        try:
            response = self.session.post(self.API_URL, json=payload, timeout=20)
            if response.status_code != 200:
                raise RuntimeError(
                    f"TypeSafe AI Jev API error ({response.status_code}) at {self.API_URL}: {response.text}"
                )
            data = response.json()
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                f"Failed to reach live TypeSafe AI Jev API at {self.API_URL}: {exc}"
            ) from exc

        return self._normalize_stage1_response(data)

    def resolve_sor_code(
        self,
        complaint_text: str,
        trade: str,
        candidate_sors: Dict[str, str],
        image_source: Optional[Any] = None,
        existing_job_ref: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Pass 2: Selects the specific M3NHF SOR code from a trade-bounded candidate set."""
        assets: Dict[str, Any] = {}
        state: Dict[str, Any] = {
            "resident_description": complaint_text,
            "identified_trade": trade,
        }
        if existing_job_ref:
            state["existing_job_reference"] = existing_job_ref

        if image_source is not None:
            asset_ref = f"asset-{uuid.uuid4().hex[:8]}"
            b64_data, fmt, _ = self._prepare_image(image_source)
            format_clean = "png" if "png" in str(fmt).lower() else "jpeg"
            assets[asset_ref] = {
                "data_base64": b64_data,
                "format": format_clean,
            }
            state["attached_evidence"] = asset_ref

        payload: Dict[str, Any] = {
            "model": os.getenv("TYPESAFE_MODEL", "jev-latest"),
            "state": state,
            "questions": self.build_stage2_schema(candidate_sors),
        }
        if assets:
            payload["assets"] = assets

        try:
            response = self.session.post(self.API_URL, json=payload, timeout=20)
            if response.status_code != 200:
                raise RuntimeError(
                    f"TypeSafe AI Jev API error ({response.status_code}) at {self.API_URL}: {response.text}"
                )
            data = response.json()
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                f"Failed to reach live TypeSafe AI Jev API at {self.API_URL}: {exc}"
            ) from exc

        return self._normalize_stage2_response(data)
