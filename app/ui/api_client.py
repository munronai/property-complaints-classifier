"""Non-blocking API client with automatic local in-process fallback and structured error capture."""

from dataclasses import asdict
import os
from typing import Any, Dict, List, Optional
import httpx
import streamlit as st

from app.config import settings
from app.domain.enums import EngineMode, IntakeChannel
from app.domain.presets import SCENARIO_PRESETS, get_preset_by_id
from app.domain.schemas import (
    ComplaintIntakeRequest,
    GatingThresholds,
)
from app.domain.sor_catalog import (
    M3NHF_SOR_CATALOG,
    MESSAGE_INTENT_CRITERIA,
    REPAIR_PRIORITY_LEVELS,
    TRADE_CRITERIA,
    get_catalog_summary,
    refresh_sor_catalog_for_trade,
    reset_sor_catalog_to_base,
)
from app.engine.image_normalizer import SYNTHETIC_IMAGE_CATALOG
from app.storage.session_store import PermissionDeniedError, session_store


class SandboxAPIClient:
    """Wraps REST calls in try/except, surfaces errors in st.session_state['last_api_error'], and supports standalone mode."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (
            base_url
            or os.environ.get("SANDBOX_API_BASE", "http://127.0.0.1:8000/api/v1")
        ).rstrip("/")

    @staticmethod
    def _record_error(message: str) -> None:
        try:
            st.session_state["last_api_error"] = message
        except Exception:
            pass

    @staticmethod
    def clear_error() -> None:
        try:
            st.session_state["last_api_error"] = None
        except Exception:
            pass

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """Executes an HTTP request to FastAPI; returns None if offline so caller can fall back or surface error."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            with httpx.Client(timeout=6.0) as client:
                resp = client.request(method, url, params=params, json=json_body)
                if resp.status_code >= 400:
                    try:
                        detail = resp.json().get("detail", resp.text)
                    except Exception:
                        detail = resp.text
                    self._record_error(f"API Error ({resp.status_code}) on {path}: {detail}")
                    return {"_api_error": True, "status_code": resp.status_code, "detail": detail}
                return resp.json()
        except httpx.RequestError:
            # FastAPI backend is not running on port 8000; fall back transparently to in-process session_store
            return None
        except Exception as exc:
            self._record_error(f"Unexpected network error on {path}: {exc}")
            return None

    def get_health(self) -> Dict[str, Any]:
        res = self._request("GET", "/health")
        if res and not isinstance(res, dict):
            return {}
        if res and not res.get("_api_error"):
            res["connection_mode"] = "FASTAPI_REST"
            return res
        return {
            "status": "ok",
            "service": settings.app_name,
            "connection_mode": "IN_PROCESS_DIRECT",
            "live_jev_configured": bool(settings.typesafe_api_key),
            "default_engine_mode": settings.default_engine_mode,
        }

    def get_telemetry(self, session_id: str) -> Dict[str, Any]:
        res = self._request("GET", "/telemetry", params={"session": session_id})
        if isinstance(res, dict) and not res.get("_api_error"):
            return res
        return session_store.compute_telemetry(session_id=session_id)

    def get_properties(self, session_id: str) -> List[Dict[str, Any]]:
        res = self._request("GET", "/properties", params={"session": session_id})
        if isinstance(res, list):
            return res
        return [p.model_dump() for p in session_store.get_properties(session_id=session_id)]

    def get_catalog(self) -> Dict[str, Any]:
        res = self._request("GET", "/catalog")
        if isinstance(res, dict) and not res.get("_api_error"):
            return res
        return {
            "trade_criteria": TRADE_CRITERIA,
            "message_intent_criteria": MESSAGE_INTENT_CRITERIA,
            "repair_priority_levels": REPAIR_PRIORITY_LEVELS,
            "m3nhf_catalog": {
                trade.value: [asdict(item) for item in items]
                for trade, items in M3NHF_SOR_CATALOG.items()
            },
            "catalog_summary": get_catalog_summary(),
            "synthetic_images": SYNTHETIC_IMAGE_CATALOG,
        }

    def refresh_sor_catalog(
        self,
        trade: str,
        max_codes: int = 20,
        session_id: str = "default",
    ) -> Optional[Dict[str, Any]]:
        """Imports up to `max_codes` (up to 20) SOR codes for `trade` from the Phase 4 feed."""
        body = {
            "trade": trade,
            "max_codes": max_codes,
            "session_id": session_id,
        }
        res = self._request("POST", "/catalog/refresh", json_body=body)
        if isinstance(res, dict):
            if res.get("_api_error"):
                return None
            # Also synchronize in-process catalog in case Streamlit reads M3NHF_SOR_CATALOG directly
            try:
                refresh_sor_catalog_for_trade(trade=trade, max_codes=max_codes)
            except Exception:
                pass
            return res
        try:
            return refresh_sor_catalog_for_trade(trade=trade, max_codes=max_codes)
        except Exception as exc:
            self._record_error(f"SOR catalog refresh failed: {exc}")
            return None

    def reset_sor_catalog(self) -> Optional[Dict[str, Any]]:
        """Resets the active M3NHF SOR catalog to the 17-code Base Set."""
        res = self._request("POST", "/catalog/reset")
        if isinstance(res, dict):
            if res.get("_api_error"):
                return None
            try:
                reset_sor_catalog_to_base()
            except Exception:
                pass
            return res
        try:
            return reset_sor_catalog_to_base()
        except Exception as exc:
            self._record_error(f"SOR catalog reset failed: {exc}")
            return None

    def get_presets(self) -> List[Dict[str, Any]]:
        res = self._request("GET", "/presets")
        if isinstance(res, list):
            return res
        return [p.model_dump() for p in SCENARIO_PRESETS]

    def get_tickets(
        self,
        session_id: str,
        property_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"session": session_id}
        if property_id:
            params["property_id"] = property_id
        res = self._request("GET", "/tickets", params=params)
        if isinstance(res, list):
            return res
        return [
            t.model_dump()
            for t in session_store.get_tickets(session_id=session_id, property_id=property_id)
        ]

    def submit_complaint(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Enforce mutual exclusion: uploaded photo removes synthetic defect preset
        clean_payload = dict(payload)
        if clean_payload.get("image_base64"):
            clean_payload["synthetic_image_preset"] = None

        res = self._request("POST", "/complaints/triage", json_body=clean_payload)
        if isinstance(res, dict):
            if res.get("_api_error"):
                return None
            return res
        try:
            req = ComplaintIntakeRequest(**clean_payload)
            tkt = session_store.orchestrator.process_intake(req, thresholds=req.thresholds)
            saved = session_store.add_ticket(tkt, session_id=req.session_id)
            return saved.model_dump()
        except Exception as exc:
            self._record_error(f"Triage evaluation failed: {exc}")
            return None

    def submit_whatsapp_webhook(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Enforce mutual exclusion: uploaded media removes synthetic defect preset
        clean_payload = dict(payload)
        if clean_payload.get("media_base64"):
            clean_payload["synthetic_image_preset"] = None

        res = self._request("POST", "/webhooks/whatsapp", json_body=clean_payload)
        if isinstance(res, dict):
            if res.get("_api_error"):
                return None
            return res
        try:
            req = ComplaintIntakeRequest(
                complaint_text=clean_payload["message_body"],
                property_id=clean_payload.get("property_id", "prop_oak_01"),
                channel=IntakeChannel.WHATSAPP,
                engine_mode=EngineMode(clean_payload.get("engine_mode", "SIMULATED")),
                session_id=clean_payload.get("session_id", "default"),
                image_base64=clean_payload.get("media_base64"),
                synthetic_image_preset=clean_payload.get("synthetic_image_preset"),
                existing_job_ref=clean_payload.get("existing_job_ref"),
                thresholds=(
                    GatingThresholds(**clean_payload["thresholds"])
                    if clean_payload.get("thresholds")
                    else None
                ),
            )
            tkt = session_store.orchestrator.process_intake(req, thresholds=req.thresholds)
            saved = session_store.add_ticket(tkt, session_id=req.session_id)
            return saved.model_dump()
        except Exception as exc:
            self._record_error(f"WhatsApp webhook simulation failed: {exc}")
            return None

    def trigger_preset(
        self,
        preset_id: str,
        session_id: str,
        engine_mode: str = "SIMULATED",
        thresholds: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        body = {
            "preset_id": preset_id,
            "session_id": session_id,
            "engine_mode": engine_mode,
            "thresholds": thresholds,
        }
        res = self._request("POST", "/simulate", json_body=body)
        if isinstance(res, dict):
            if res.get("_api_error"):
                return None
            return res
        try:
            preset = get_preset_by_id(preset_id)
            req = ComplaintIntakeRequest(
                complaint_text=preset.complaint_text,
                property_id=preset.property_id,
                channel=preset.channel,
                engine_mode=EngineMode(engine_mode),
                session_id=session_id,
                synthetic_image_preset=preset.synthetic_image_preset,
                existing_job_ref=preset.existing_job_ref,
                thresholds=GatingThresholds(**thresholds) if thresholds else None,
            )
            tkt = session_store.orchestrator.process_intake(req, thresholds=req.thresholds)
            saved = session_store.add_ticket(tkt, session_id=session_id)
            return saved.model_dump()
        except Exception as exc:
            self._record_error(f"Scenario simulation failed: {exc}")
            return None

    def approve_or_override_ticket(
        self,
        ticket_id: str,
        session_id: str,
        override_sor: Optional[str] = None,
        surveyor_notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        body = {
            "session_id": session_id,
            "override_sor": override_sor,
            "surveyor_notes": surveyor_notes,
        }
        res = self._request("POST", f"/tickets/{ticket_id}/approve", json_body=body)
        if isinstance(res, dict):
            if res.get("_api_error"):
                return None
            return res
        try:
            updated = session_store.approve_or_override_ticket(
                ticket_id=ticket_id,
                session_id=session_id,
                override_sor=override_sor,
                surveyor_notes=surveyor_notes,
            )
            return updated.model_dump()
        except Exception as exc:
            self._record_error(f"Ticket override failed: {exc}")
            return None

    def reset_workspace(
        self,
        session_id: str,
        reset_all: bool = False,
        admin_key: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        body = {
            "session_id": session_id,
            "all": reset_all,
            "admin_key": admin_key,
        }
        res = self._request("POST", "/reset", json_body=body)
        if isinstance(res, dict):
            if res.get("_api_error"):
                return None
            return res
        try:
            return session_store.reset_workspace(
                session_id=session_id,
                reset_all=reset_all,
                admin_key=admin_key,
            )
        except PermissionDeniedError as exc:
            self._record_error(str(exc))
            return None


api_client = SandboxAPIClient()
