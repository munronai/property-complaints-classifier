"""Live TypeSafe Jev Multimodal Decision Engine client."""

import os
import uuid
from typing import Any, Dict, Optional, Tuple
import requests

from app.config import settings
from app.domain.schemas import ImageTelemetry
from app.domain.sor_catalog import (
    MESSAGE_INTENT_CRITERIA,
    REPAIR_PRIORITY_LEVELS,
    TRADE_CRITERIA,
)
from app.engine.image_normalizer import prepare_image_for_jev


class JevRepairsTriageEngine:
    """Multi-stage TypeSafe Jev decision engine supporting multimodal text + image evaluation."""

    API_URL = settings.typesafe_api_url

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = api_key if api_key is not None else os.environ.get("TYPESAFE_API_KEY", settings.typesafe_api_key)
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
        """Builds the structured Stage 1 TypeSafe Jev question schema."""
        return {
            "inappropriate_content_flag": {
                "type": "noul",
                "instructions": (
                    "Does the attached image or text contain explicit, rude, graphic, offensive, "
                    "or abusive content inappropriate for a housing repairs system?"
                ),
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
            },
            "repair_priority": {
                "type": "score",
                "instructions": (
                    "Determine the response SLA level based on immediate danger, total loss of amenity, "
                    "or routine degradation."
                ),
                "levels": REPAIR_PRIORITY_LEVELS,
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
            b64_data, mime, _ = self._prepare_image(image_source)
            assets[asset_ref] = {
                "data_base64": b64_data,
                "format": mime,
            }
            state["attached_evidence"] = asset_ref

        payload: Dict[str, Any] = {
            "state": state,
            "questions": self.build_stage1_schema(),
        }
        if assets:
            payload["assets"] = assets

        response = self.session.post(self.API_URL, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()

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
            b64_data, mime, _ = self._prepare_image(image_source)
            assets[asset_ref] = {
                "data_base64": b64_data,
                "format": mime,
            }
            state["attached_evidence"] = asset_ref

        payload: Dict[str, Any] = {
            "state": state,
            "questions": self.build_stage2_schema(candidate_sors),
        }
        if assets:
            payload["assets"] = assets

        response = self.session.post(self.API_URL, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
