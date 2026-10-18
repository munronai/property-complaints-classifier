"""
Phase 4: Test Data Generation & Open-Data Pipeline.

Provides:
- taxonomy: Ombudsman intent/repair distributions and 120-code extended M3NHF SOR feed
- ombudsman_harvester: UK Housing Ombudsman determination scraper & anonymized case feed
- tribunal_harvester: First-tier Tribunal (Property Chamber) case harvester & defect patterns
- reddit_normalizer: Colloquial UK tenant narrative normalizer (slang -> domain defect mapping)
- synthesizer: Stratified dataset generator (e.g. 500 ground-truth complaints across trades)
- cli: Command-line entrypoint for generating datasets and refreshing SOR catalogs
"""
from app.data_pipeline.taxonomy import (
    OMBUDSMAN_INTENT_DISTRIBUTION,
    REPAIR_TRADE_DISTRIBUTION,
    ADDITIONAL_M3NHF_SOR_BY_TRADE,
    build_extended_m3nhf_sor_feed,
    get_feed_sors_for_trade,
)

__all__ = [
    "OMBUDSMAN_INTENT_DISTRIBUTION",
    "REPAIR_TRADE_DISTRIBUTION",
    "ADDITIONAL_M3NHF_SOR_BY_TRADE",
    "build_extended_m3nhf_sor_feed",
    "get_feed_sors_for_trade",
]
