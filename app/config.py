"""Centralized configuration and default policy thresholds."""

from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class AppSettings:
    """Application settings resolved from environment variables with safe defaults."""

    app_name: str = "Social Housing & Property Complaint Classifier Sandbox"
    environment: str = os.environ.get("SANDBOX_ENV", "development")
    typesafe_api_key: str = os.environ.get("TYPESAFE_API_KEY", "")
    typesafe_api_url: str = os.environ.get(
        "TYPESAFE_API_URL", "https://api.typesafe.ai/v1/systemone"
    )
    sandbox_admin_key: str = os.environ.get(
        "SANDBOX_ADMIN_KEY", "sor-admin-secret-2026"
    )
    default_engine_mode: str = os.environ.get("DEFAULT_ENGINE_MODE", "SIMULATED")

    # Default TriageEscalationGuard Policy Thresholds
    min_trade_confidence: float = float(os.environ.get("MIN_TRADE_CONFIDENCE", "0.70"))
    min_sor_confidence: float = float(os.environ.get("MIN_SOR_CONFIDENCE", "0.65"))
    min_probability_margin: float = float(
        os.environ.get("MIN_PROBABILITY_MARGIN", "0.15")
    )
    damp_hazard_threshold: float = float(
        os.environ.get("DAMP_HAZARD_THRESHOLD", "0.40")
    )
    inappropriate_content_threshold: float = float(
        os.environ.get("INAPPROPRIATE_CONTENT_THRESHOLD", "0.50")
    )

    # Session TTL (48 hours in seconds)
    session_ttl_seconds: int = int(
        os.environ.get("SESSION_TTL_SECONDS", str(48 * 3600))
    )


settings = AppSettings()
