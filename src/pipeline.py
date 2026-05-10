"""
src/pipeline.py
===============
CLI entry point. Runs the full pipeline:
  data_collection → preprocessing → similarity → embeddings

Usage:
  python -m src.pipeline                  # full run
  python -m src.pipeline --skip-collect   # skip re-downloading data
  python -m src.pipeline --step collect   # only run data collection
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

_ROOT = Path(__file__).parent.parent
with open(_ROOT / "config.yaml") as f:
    CFG = yaml.safe_load(f)


def _step_collect() -> None:
    log.info("=" * 60)
    log.info("STEP 1 — Data Collection")
    log.info("=" * 60)
    from src.data_collection import collect_all
    raw_dir = _ROOT / CFG["paths"]["raw_data"]
    raw_dir.mkdir(parents=True, exist_ok=True)
    df = collect_all()
    out = raw_dir / "all_indicators_raw.csv"
    df.to_csv(out)
    log.info("Raw data saved: %s  (%d countries × %d indicators)", out, *df.shape)


def _step_preprocess() -> None:
    log.info("=" * 60)
    log.info("STEP 2 — Preprocessing")
    log.info("=" * 60)
    from src.preprocessing import run
    run()


def _step_similarity() -> None:
    log.info("=" * 60)
    log.info("STEP 3 — Similarity Computation")
    log.info("=" * 60)
    from src.similarity import run
    run()


def _step_embeddings() -> None:
    log.info("=" * 60)
    log.info("STEP 4 — Embeddings")
    log.info("=" * 60)
    from src.embeddings import run
    run()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LatAm Similarity Pipeline — runs all steps end-to-end"
    )
    parser.add_argument(
        "--step",
        choices=["collect", "preprocess", "similarity", "embeddings", "all"],
        default="all",
        help="Which pipeline step to run (default: all)",
    )
    parser.add_argument(
        "--skip-collect",
        action="store_true",
        help="Skip data collection (use cached raw data)",
    )
    args = parser.parse_args()

    step = args.step
    skip_collect = args.skip_collect

    steps_map = {
        "collect": [_step_collect],
        "preprocess": [_step_preprocess],
        "similarity": [_step_similarity],
        "embeddings": [_step_embeddings],
        "all": [
            _step_collect if not skip_collect else None,
            _step_preprocess,
            _step_similarity,
            _step_embeddings,
        ],
    }

    pipeline = [s for s in steps_map[step] if s is not None]

    log.info("Running pipeline: %s", [f.__name__ for f in pipeline])

    for fn in pipeline:
        try:
            fn()
        except Exception as e:
            log.error("Pipeline step %s failed: %s", fn.__name__, e)
            sys.exit(1)

    log.info("Pipeline complete. Processed files are in: %s", _ROOT / CFG["paths"]["processed_data"])
    log.info("Launch dashboard with:  streamlit run app/dashboard.py")


if __name__ == "__main__":
    main()
