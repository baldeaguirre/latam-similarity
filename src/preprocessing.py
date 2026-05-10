"""
src/preprocessing.py
====================
Cleans, imputes, reverse-codes, and normalizes the raw indicator matrix.

Steps:
  1. Log missingness per indicator
  2. Drop indicators with ≥30% missing
  3. KNN-impute remaining gaps (k=3)
  4. Reverse-code negative indicators (higher = better)
  5. Z-score normalize
  6. Save to data/processed/countries_features.csv

Run standalone: python -m src.preprocessing
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

_ROOT = Path(__file__).parent.parent
with open(_ROOT / "config.yaml") as f:
    CFG = yaml.safe_load(f)

PROCESSED_DIR = _ROOT / CFG["paths"]["processed_data"]
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

MISSINGNESS_THRESHOLD = CFG["preprocessing"]["missingness_threshold"]
KNN_K = CFG["preprocessing"]["knn_impute_k"]

# Build lookup: indicator_id -> config dict
IND_CONFIG = {ind["id"]: ind for ind in CFG["indicators"]}

COUNTRY_NAMES = [c["name"] for c in CFG["countries"]]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def preprocess(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Parameters
    ----------
    raw_df : DataFrame  (countries × indicators, raw values)

    Returns
    -------
    features_df   : normalized feature matrix (similarity-relevant indicators only)
    structural_df : structural/demographic features (not in similarity computation)
    report        : dict with missingness log and dropped indicators
    """
    report: dict = {
        "missingness": {},
        "dropped": [],
        "reverse_coded": [],
        "structural_held_out": [],
        "imputed": [],
    }

    # ------------------------------------------------------------------
    # 1. Separate structural / non-similarity columns
    # ------------------------------------------------------------------
    similarity_cols = [
        ind_id for ind_id, cfg in IND_CONFIG.items()
        if not cfg.get("structural", False) and cfg.get("include_in_similarity", True)
        and ind_id in raw_df.columns
    ]
    structural_cols = [
        ind_id for ind_id, cfg in IND_CONFIG.items()
        if cfg.get("structural", False) and ind_id in raw_df.columns
    ]
    report["structural_held_out"] = structural_cols

    sim_df = raw_df[similarity_cols].copy()
    struct_df = raw_df[structural_cols].copy() if structural_cols else pd.DataFrame(index=raw_df.index)

    # ------------------------------------------------------------------
    # 2. Missingness check — drop if ≥ threshold
    # ------------------------------------------------------------------
    n_countries = len(sim_df)
    cols_to_drop = []
    for col in sim_df.columns:
        n_missing = sim_df[col].isna().sum()
        pct_missing = n_missing / n_countries
        report["missingness"][col] = {
            "n_missing": int(n_missing),
            "pct_missing": round(float(pct_missing), 4),
            "status": "dropped" if pct_missing >= MISSINGNESS_THRESHOLD else "kept",
        }
        if pct_missing >= MISSINGNESS_THRESHOLD:
            cols_to_drop.append(col)
            log.warning("Dropping %s — %.0f%% missing", col, pct_missing * 100)

    report["dropped"] = cols_to_drop
    sim_df = sim_df.drop(columns=cols_to_drop)

    kept_cols = list(sim_df.columns)
    log.info("Kept %d indicators after missingness filter (dropped %d)", len(kept_cols), len(cols_to_drop))

    # ------------------------------------------------------------------
    # 3. KNN Imputation on remaining gaps
    # ------------------------------------------------------------------
    imputed_cols = [col for col in kept_cols if sim_df[col].isna().any()]
    report["imputed"] = imputed_cols
    if imputed_cols:
        log.info("KNN imputing %d columns: %s", len(imputed_cols), imputed_cols)
        imputer = KNNImputer(n_neighbors=KNN_K)
        # Imputer works on arrays; preserve index/columns
        sim_arr = imputer.fit_transform(sim_df.values.astype(float))
        sim_df = pd.DataFrame(sim_arr, index=sim_df.index, columns=sim_df.columns)

    # Handle structural columns too (simple median imputation — not used in similarity)
    if not struct_df.empty:
        struct_df = struct_df.apply(lambda col: col.fillna(col.median()))

    # ------------------------------------------------------------------
    # 4. Reverse-code negative indicators (higher = better)
    # ------------------------------------------------------------------
    for col in sim_df.columns:
        cfg = IND_CONFIG.get(col, {})
        if cfg.get("reverse_code", False):
            sim_df[col] = -sim_df[col]
            report["reverse_coded"].append(col)
            log.info("Reverse-coded: %s", col)

    # ------------------------------------------------------------------
    # 5. Log-scale population for structural overlay
    # ------------------------------------------------------------------
    if "population_total" in struct_df.columns:
        struct_df["population_log"] = np.log1p(struct_df["population_total"])

    # ------------------------------------------------------------------
    # 6. Z-score normalization
    # ------------------------------------------------------------------
    scaler = StandardScaler()
    scaled_arr = scaler.fit_transform(sim_df.values.astype(float))
    features_df = pd.DataFrame(scaled_arr, index=sim_df.index, columns=sim_df.columns)

    log.info("Preprocessing complete. Feature matrix: %s", features_df.shape)
    return features_df, struct_df, report


def run() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load raw CSV → preprocess → save processed CSVs. Returns (features_df, structural_df)."""
    raw_path = _ROOT / CFG["paths"]["raw_data"] / "all_indicators_raw.csv"
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw data not found at {raw_path}. Run data_collection first."
        )

    raw_df = pd.read_csv(raw_path, index_col=0)
    raw_df.index = raw_df.index.str.strip()

    features_df, struct_df, report = preprocess(raw_df)

    # Save
    feat_path = _ROOT / CFG["paths"]["features_file"]
    feat_path.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_csv(feat_path)
    log.info("Saved features to %s", feat_path)

    struct_path = PROCESSED_DIR / "structural_features.csv"
    struct_df.to_csv(struct_path)
    log.info("Saved structural features to %s", struct_path)

    # Save missingness report
    import json
    report_path = PROCESSED_DIR / "preprocessing_report.json"
    with open(report_path, "w") as fp:
        json.dump(report, fp, indent=2)
    log.info("Preprocessing report saved to %s", report_path)

    # Print summary
    print("\n=== Missingness Report ===")
    for col, info in report["missingness"].items():
        pct = info["pct_missing"] * 100
        status = info["status"]
        print(f"  {col:40s} {pct:5.1f}% missing  [{status}]")
    print(f"\nDropped: {report['dropped']}")
    print(f"Reverse-coded: {report['reverse_coded']}")
    print(f"Structural (held out): {report['structural_held_out']}")
    print(f"Imputed: {report['imputed']}")

    return features_df, struct_df


if __name__ == "__main__":
    run()
