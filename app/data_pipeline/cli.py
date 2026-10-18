"""
CLI Entrypoint for Phase 4 Open-Data Pipeline & SOR Catalog Feed Refresh.

Usage examples:
  python -m app.data_pipeline.cli --samples 500 --output data/synthetic_complaints_500.jsonl
  python -m app.data_pipeline.cli --refresh-trade PLUM --max-codes 20
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Optional

from app.data_pipeline.synthesizer import write_dataset_jsonl
from app.domain.sor_catalog import refresh_sor_catalog_for_trade, reset_sor_catalog_to_base


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 4 UK Social Housing Open-Data Pipeline & M3NHF SOR Feed CLI"
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=500,
        help="Number of stratified complaint records to synthesize (default: 500)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic dataset generation (default: 42)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/synthetic_complaints_500.jsonl",
        help="Output JSONL file path",
    )
    parser.add_argument(
        "--refresh-trade",
        type=str,
        default=None,
        help="Optional trade code (PLUM, DAMP, ROOF, JOIN, ELEC, PLAS, or ALL) to import up to --max-codes SOR codes into the catalog",
    )
    parser.add_argument(
        "--max-codes",
        type=int,
        default=20,
        help="Maximum SOR codes per trade to import from the Phase 4 feed (1..20, default: 20)",
    )
    parser.add_argument(
        "--reset-catalog",
        action="store_true",
        help="Reset active M3NHF SOR catalog back to the 17-item Base Set",
    )

    args = parser.parse_args(argv)

    if args.reset_catalog:
        reset_result = reset_sor_catalog_to_base()
        print(json.dumps({"action": "reset_catalog", **reset_result}, indent=2))

    if args.refresh_trade:
        refresh_result = refresh_sor_catalog_for_trade(
            trade=args.refresh_trade,
            max_codes=args.max_codes,
        )
        print(json.dumps({"action": "refresh_catalog", **refresh_result}, indent=2))

    summary = write_dataset_jsonl(
        output_path=Path(args.output),
        total_samples=args.samples,
        seed=args.seed,
    )
    print(json.dumps({"action": "synthesize_dataset", **summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
