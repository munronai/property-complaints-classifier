"""
Unit & Integration Tests for Phase 4 Open-Data Pipeline, SOR Catalog Feed Refresh,
and Baseline / Sys Admin Schedule Reset.
"""
from __future__ import annotations

from pathlib import Path
from fastapi.testclient import TestClient

from app.config import settings
from app.data_pipeline.cli import main as cli_main
from app.data_pipeline.ombudsman_harvester import harvest_ombudsman_determinations
from app.data_pipeline.synthesizer import generate_stratified_dataset
from app.data_pipeline.taxonomy import (
    build_extended_m3nhf_sor_feed,
    get_feed_sors_for_trade,
)
from app.data_pipeline.tribunal_harvester import harvest_tribunal_seeds
from app.domain.enums import IntakeChannel, RoutingDestination, TradeCode
from app.domain.schemas import ComplaintIntakeRequest
from app.domain.sor_catalog import (
    BASE_M3NHF_SOR_CATALOG,
    M3NHF_SOR_CATALOG,
    get_catalog_summary,
    refresh_sor_catalog_for_trade,
    reset_sor_catalog_to_base,
)
from app.api.main import app
from app.storage.session_store import session_store


def test_extended_m3nhf_feed_has_20_codes_per_trade() -> None:
    """Verify every one of the 6 repair trades has 20 authentic M3NHF codes in the Phase 4 feed."""
    feed = build_extended_m3nhf_sor_feed()
    assert sum(len(items) for items in feed.values()) == 120
    for trade in ("PLUM", "DAMP", "ROOF", "JOIN", "ELEC", "PLAS"):
        trade_sors = get_feed_sors_for_trade(trade, max_codes=20)
        assert len(trade_sors) == 20
        subset_10 = get_feed_sors_for_trade(trade, max_codes=10)
        assert len(subset_10) == 10


def test_stratified_500_dataset_statistical_proportions() -> None:
    """Verify the 500-row stratified synthesizer matches Ombudsman intent & trade distributions."""
    dataset = generate_stratified_dataset(total_samples=500, seed=42)
    assert len(dataset) == 500

    intents = {}
    trades = {}
    for row in dataset:
        gt = row["ground_truth"]
        intent = gt["primary_intent"]
        intents[intent] = intents.get(intent, 0) + 1
        if intent == "REPAIR":
            tr = gt["trade"]
            trades[tr] = trades.get(tr, 0) + 1
            # Ensure narrative does not leak raw numeric SOR code
            assert gt["expected_sor_code"] not in row["complaint_text"]

    assert intents["REPAIR"] == 300
    assert intents["ASB"] == 90
    assert intents["ESCALATION"] == 70
    assert intents["RENT_SERVICE_CHARGE"] == 40
    assert set(trades.keys()) == {"PLUM", "DAMP", "JOIN", "ELEC", "ROOF", "PLAS"}
    assert sum(trades.values()) == 300


def test_harvesters_return_domain_seeds() -> None:
    """Verify Ombudsman and First-tier Tribunal harvesters filter by trade accurately."""
    ho_all = harvest_ombudsman_determinations(limit=10)
    assert len(ho_all) >= 6
    ho_damp = harvest_ombudsman_determinations(trade_filter="DAMP")
    assert all(r["trade"] == "DAMP" for r in ho_damp)

    trib_join = harvest_tribunal_seeds(trade_filter="JOIN")
    assert len(trib_join) >= 2
    assert all(r["trade"] == "JOIN" for r in trib_join)


def test_refresh_sor_catalog_eliminates_other_fallback_and_resets_to_base() -> None:
    """
    Verify that:
    1. With the 17-code Base Set, a complaint for an extended trade item (e.g. a broken uPVC
       window espagnolette lock 122004 in JOIN, or a seized radiator TRV valve 196012 in PLUM)
       resolves to 'OTHER' because that SOR is not in the base schedule.
    2. After importing up to 20 codes for that trade from the Phase 4 feed, the same complaint
       resolves directly to 122004 / 196012 and auto-dispatches to HMS.
    3. Both Reset to Baseline (session reset) and Sys Admin Reset (global reset) restore the
       M3NHF SOR catalog back to the 17-item Base Set.
    """
    reset_sor_catalog_to_base()
    base_summary = get_catalog_summary()
    assert base_summary["total_active_codes"] == 18
    assert base_summary["is_expanded"] is False
    assert len(M3NHF_SOR_CATALOG[TradeCode.JOIN]) == 3

    # Complaint for a broken window espagnolette lock (122004 - in Phase 4 feed, not in 3-code JOIN base set)
    espag_req = ComplaintIntakeRequest(
        complaint_text=(
            "The espagnolette lock mechanism inside the bedroom uPVC casement window handle is jammed "
            "and broken so the window won't latch shut."
        ),
        property_id="prop_oak_01",
        channel=IntakeChannel.DASHBOARD_UI,
        session_id="test_feed_session",
    )

    # 1. Before refreshing JOIN catalog -> resolves to OTHER -> SURVEYOR_DESK_REVIEW
    tkt_before = session_store.orchestrator.process_intake(espag_req)
    assert tkt_before.decision.assigned_trade == "JOIN"
    assert tkt_before.decision.assigned_sor == "OTHER"
    assert tkt_before.decision.destination == RoutingDestination.SURVEYOR_DESK_REVIEW

    # 2. Refresh JOIN catalog with up to 20 codes from the Phase 4 feed
    refresh_info = refresh_sor_catalog_for_trade("JOIN", max_codes=20)
    assert refresh_info["counts_by_trade"]["JOIN"] == 20
    assert len(M3NHF_SOR_CATALOG[TradeCode.JOIN]) == 20

    # Re-evaluate the exact same complaint -> now resolves to 122004 and AUTO_DISPATCH_HMS!
    tkt_after = session_store.orchestrator.process_intake(espag_req)
    assert tkt_after.decision.assigned_trade == "JOIN"
    assert tkt_after.decision.assigned_sor == "122004"
    assert tkt_after.decision.destination == RoutingDestination.AUTO_DISPATCH_HMS

    # 3. Test "Reset to Baseline" (session reset, reset_all=False) resets SOR catalog to Base Set (18 codes)
    session_reset_res = session_store.reset_workspace(
        session_id="test_feed_session",
        reset_all=False,
    )
    assert session_reset_res["status"] == "session_reset_complete"
    assert get_catalog_summary()["total_active_codes"] == 18
    assert len(M3NHF_SOR_CATALOG[TradeCode.JOIN]) == len(
        BASE_M3NHF_SOR_CATALOG[TradeCode.JOIN]
    )

    # 4. Expand ALL trades (120 codes), then test "Sys Admin Reset" (reset_all=True) resets SOR catalog to Base Set
    refresh_all = refresh_sor_catalog_for_trade("ALL", max_codes=20)
    assert refresh_all["total_active_codes"] == 120

    global_reset_res = session_store.reset_workspace(
        session_id="test_feed_session",
        reset_all=True,
        admin_key=settings.sandbox_admin_key,
    )
    assert global_reset_res["status"] == "global_reset_complete"
    assert get_catalog_summary()["total_active_codes"] == 18
    assert get_catalog_summary()["is_expanded"] is False


def test_catalog_refresh_and_reset_rest_endpoints(tmp_path: Path) -> None:
    """Verify FastAPI /api/v1/catalog/refresh, /api/v1/catalog/reset, and Phase 4 CLI."""
    client = TestClient(app)
    reset_sor_catalog_to_base()

    # Refresh PLUM to 15 codes via REST API
    resp = client.post(
        "/api/v1/catalog/refresh",
        json={"trade": "PLUM", "max_codes": 15, "session_id": "api_test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["counts_by_trade"]["PLUM"] == 15
    assert data["is_expanded"] is True

    # Reset via /api/v1/reset (session Reset to Baseline)
    rst = client.post(
        "/api/v1/reset",
        json={"session_id": "api_test", "all": False},
    )
    assert rst.status_code == 200
    assert get_catalog_summary()["total_active_codes"] == 18

    # Test CLI execution
    out_file = tmp_path / "synth_50.jsonl"
    rc = cli_main(["--samples", "50", "--output", str(out_file), "--reset-catalog"])
    assert rc == 0
    assert out_file.exists()
    lines = out_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 50
