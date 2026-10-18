"""Domain enumerations for complaint intake, TypeSafe Jev classification, and routing."""

from enum import Enum


class TradeCode(str, Enum):
    """Primary M3NHF repair trade categories evaluated in Stage 1."""

    PLUM = "PLUM"  # Plumbing, internal leaks, radiators, cylinders, taps, waste drainage
    ROOF = "ROOF"  # Roofing, tiles, chimney flashing, gutters, fascia, downpipes
    PLAS = "PLAS"  # Plastering, water-damaged ceilings, drywall skimming, blown plaster
    DAMP = "DAMP"  # Mould eradication, anti-fungal treatment, condensation, DPC failure
    JOIN = "JOIN"  # Carpentry, doors, window frames, skirting, floorboards, kitchen units
    ELEC = "ELEC"  # Electrical sockets, consumer units, smoke alarms, light pendants
    OTHER = "OTHER"  # Out-of-scope or non-repair issue


class MessageIntent(str, Enum):
    """Stage 1 communication intent classification."""

    NEW_REPAIR_DEFECT = "NEW_REPAIR_DEFECT"
    COMPLETED_REPAIR_COMPLAINT = "COMPLETED_REPAIR_COMPLAINT"
    WIP_REPAIR_UPDATE = "WIP_REPAIR_UPDATE"
    CONTRACTOR_SCHEDULING = "CONTRACTOR_SCHEDULING"
    CONTRACTOR_PAYMENT_INQUIRY = "CONTRACTOR_PAYMENT_INQUIRY"
    GENERAL_HOUSING_QUERY = "GENERAL_HOUSING_QUERY"


class EscalationReason(str, Enum):
    """Gating and re-routing circuit breaker triggers."""

    INAPPROPRIATE_CONTENT_DETECTED = "INAPPROPRIATE_CONTENT_DETECTED"
    AWAABS_LAW_RISK = "AWAABS_LAW_RISK"
    EMERGENCY_ESCALATION = "EMERGENCY_ESCALATION"
    NON_REPAIR_FINANCE_QUERY = "NON_REPAIR_FINANCE_QUERY"
    REPAIR_UPDATE_OR_SCHEDULING = "REPAIR_UPDATE_OR_SCHEDULING"
    POST_REPAIR_QUALITY_COMPLAINT = "POST_REPAIR_QUALITY_COMPLAINT"
    LOW_TRADE_CONFIDENCE = "LOW_TRADE_CONFIDENCE"
    LOW_SOR_CONFIDENCE = "LOW_SOR_CONFIDENCE"
    AMBIGUOUS_SOR_MARGIN = "AMBIGUOUS_SOR_MARGIN"
    OUT_OF_SCHEDULE_SCOPE = "OUT_OF_SCHEDULE_SCOPE"


class RoutingDestination(str, Enum):
    """Final operational destination determined by TriageEscalationGuard."""

    DISCARDED_INAPPROPRIATE_CONTENT = "DISCARDED_INAPPROPRIATE_CONTENT"
    AUTO_DISPATCH_HMS = "AUTO_DISPATCH_HMS"
    SURVEYOR_DESK_REVIEW = "SURVEYOR_DESK_REVIEW"
    QUALITY_RECALL_SURVEYOR_REVIEW = "QUALITY_RECALL_SURVEYOR_REVIEW"
    CUSTOMER_SERVICE_WIP_DESK = "CUSTOMER_SERVICE_WIP_DESK"
    CONTRACTOR_FINANCE_DESK = "CONTRACTOR_FINANCE_DESK"
    DISREPAIR_LEGAL_TEAM = "DISREPAIR_LEGAL_TEAM"
    OUT_OF_HOURS_DUTY_OFFICER = "OUT_OF_HOURS_DUTY_OFFICER"


class IntakeChannel(str, Enum):
    """Supported resident and contractor communication channels."""

    DASHBOARD_UI = "DASHBOARD_UI"
    WHATSAPP = "WHATSAPP"
    REST_API = "REST_API"
    MCP_AGENT = "MCP_AGENT"
    OPEN_DATA_POLLER = "OPEN_DATA_POLLER"


class EngineMode(str, Enum):
    """Dual execution modes for the Jev Triage Engine."""

    SIMULATED = "SIMULATED"
    LIVE = "LIVE"


class PortfolioType(str, Enum):
    """Property portfolio classification."""

    SOCIAL_HOUSING = "SOCIAL_HOUSING"
    COMMERCIAL_PROPERTY = "COMMERCIAL_PROPERTY"


class TicketStatus(str, Enum):
    """Lifecycle state of a triaged complaint ticket."""

    AUTO_DISPATCHED = "AUTO_DISPATCHED"
    PENDING_SURVEYOR_REVIEW = "PENDING_SURVEYOR_REVIEW"
    PENDING_RECALL_INSPECTION = "PENDING_RECALL_INSPECTION"
    REROUTED_WIP_DESK = "REROUTED_WIP_DESK"
    REROUTED_FINANCE_DESK = "REROUTED_FINANCE_DESK"
    ESCALATED_LEGAL_AWAABS = "ESCALATED_LEGAL_AWAABS"
    ESCALATED_EMERGENCY_OOH = "ESCALATED_EMERGENCY_OOH"
    DISCARDED_MODERATION = "DISCARDED_MODERATION"
    SURVEYOR_APPROVED = "SURVEYOR_APPROVED"
    SURVEYOR_OVERRIDDEN = "SURVEYOR_OVERRIDDEN"
