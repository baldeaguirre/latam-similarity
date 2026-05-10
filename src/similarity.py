"""
src/similarity.py
=================
Computes pairwise similarity between countries using three metrics:
  - Cosine similarity
  - Euclidean similarity  = 1 / (1 + euclidean_distance)
  - Pearson correlation

Composite score = mean of the three, rescaled to [0, 1].

Also applies category weighting from config.yaml.

Run standalone: python -m src.similarity
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.spatial.distance import cosine, euclidean
from scipy.stats import pearsonr

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

_ROOT = Path(__file__).parent.parent
with open(_ROOT / "config.yaml") as f:
    CFG = yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Category weighting
# ---------------------------------------------------------------------------

def build_weight_vector(feature_cols: list[str], category_weights: dict[str, float] | None = None) -> np.ndarray:
    """
    Build a weight vector aligned with feature_cols.
    Each category's total weight is distributed equally among its indicators.
    category_weights defaults to config.yaml values if not provided.
    """
    if category_weights is None:
        category_weights = CFG.get("category_weights", {})

    ind_config = {ind["id"]: ind for ind in CFG["indicators"]}

    # Count indicators per category (in feature_cols only)
    cat_counts: dict[str, int] = {}
    for col in feature_cols:
        cat = ind_config.get(col, {}).get("category", "unknown")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    weights = np.ones(len(feature_cols))
    for i, col in enumerate(feature_cols):
        cat = ind_config.get(col, {}).get("category", "unknown")
        cat_weight = category_weights.get(cat, 0.0)
        n_in_cat = cat_counts.get(cat, 1)
        weights[i] = cat_weight / n_in_cat

    # Normalize weights to sum to 1.0
    total = weights.sum()
    if total > 0:
        weights = weights / total

    return weights


# ---------------------------------------------------------------------------
# Pairwise metrics
# ---------------------------------------------------------------------------

def cosine_similarity_matrix(weighted_X: np.ndarray) -> np.ndarray:
    """N×N cosine similarity matrix. Returns values in [0, 1]."""
    n = weighted_X.shape[0]
    mat = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                mat[i, j] = 1.0
            elif i < j:
                norm_i = np.linalg.norm(weighted_X[i])
                norm_j = np.linalg.norm(weighted_X[j])
                if norm_i == 0 or norm_j == 0:
                    # Zero-norm vectors: treat as identical (similarity = 1)
                    sim_scaled = 1.0
                else:
                    dist = cosine(weighted_X[i], weighted_X[j])
                    if np.isnan(dist):
                        dist = 0.0  # identical vectors edge case
                    sim = 1.0 - dist  # cosine similarity in [-1, 1]
                    sim_scaled = (sim + 1.0) / 2.0  # rescale to [0, 1]
                mat[i, j] = sim_scaled
                mat[j, i] = sim_scaled
    return mat


def euclidean_similarity_matrix(weighted_X: np.ndarray) -> np.ndarray:
    """N×N Euclidean similarity = 1 / (1 + distance)."""
    n = weighted_X.shape[0]
    mat = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                mat[i, j] = 1.0
            elif i < j:
                dist = euclidean(weighted_X[i], weighted_X[j])
                sim = 1.0 / (1.0 + dist)
                mat[i, j] = sim
                mat[j, i] = sim
    return mat


def pearson_similarity_matrix(weighted_X: np.ndarray) -> np.ndarray:
    """N×N Pearson correlation matrix rescaled to [0, 1]."""
    n = weighted_X.shape[0]
    mat = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                mat[i, j] = 1.0
            elif i < j:
                if np.std(weighted_X[i]) == 0 or np.std(weighted_X[j]) == 0:
                    r = 0.0
                else:
                    r, _ = pearsonr(weighted_X[i], weighted_X[j])
                # Rescale from [-1, 1] to [0, 1]
                sim = (r + 1.0) / 2.0
                mat[i, j] = sim
                mat[j, i] = sim
    return mat


def composite_similarity_matrix(
    features_df: pd.DataFrame,
    category_weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """
    Compute composite similarity matrix from features_df.

    Returns a DataFrame with countries as both index and columns.
    """
    countries = list(features_df.index)
    cols = list(features_df.columns)
    X = features_df.values.astype(float)

    # Apply weights
    weights = build_weight_vector(cols, category_weights)
    log.info("Category weight vector (first 5): %s", weights[:5].round(4))
    weighted_X = X * weights  # broadcast: each column scaled by its weight

    # Compute three matrices
    log.info("Computing cosine similarity...")
    cos_mat = cosine_similarity_matrix(weighted_X)

    log.info("Computing Euclidean similarity...")
    euc_mat = euclidean_similarity_matrix(weighted_X)

    log.info("Computing Pearson similarity...")
    pear_mat = pearson_similarity_matrix(weighted_X)

    # Composite = mean of three
    composite = (cos_mat + euc_mat + pear_mat) / 3.0

    # Verify diagonal is 1.0 (sanity check)
    assert np.allclose(np.diag(composite), 1.0), "Diagonal should be 1.0"

    result = pd.DataFrame(composite, index=countries, columns=countries)
    log.info("Composite similarity matrix shape: %s", result.shape)
    return result


def pairwise_contribution(
    features_df: pd.DataFrame,
    country_a: str,
    country_b: str,
    category_weights: dict[str, float] | None = None,
) -> pd.Series:
    """
    For a specific country pair, compute each indicator's contribution to (dis)similarity.
    Returns a Series (index=indicator_id) with signed contribution values.
    Positive = these countries are similar on this indicator.
    Negative = these countries differ on this indicator.
    """
    cols = list(features_df.columns)
    weights = build_weight_vector(cols, category_weights)

    a = features_df.loc[country_a].values.astype(float)
    b = features_df.loc[country_b].values.astype(float)

    # Contribution: negative absolute weighted difference for each feature
    # (higher = more similar on that feature)
    contributions = -np.abs(a - b) * weights
    return pd.Series(contributions, index=cols, name=f"{country_a} vs {country_b}")


def sensitivity_analysis(
    features_df: pd.DataFrame,
    delta: float = 0.20,
    top_n: int = 3,
) -> dict:
    """
    Vary each category weight by ±delta (relative) and check which
    top-N nearest-neighbor rankings change.

    Returns dict mapping country -> list of categories that caused ranking changes.
    """
    base_weights = dict(CFG.get("category_weights", {}))
    base_sim = composite_similarity_matrix(features_df, base_weights)
    countries = list(features_df.index)

    # Base top-N neighbors for each country
    def get_top_n(sim_df: pd.DataFrame, n: int) -> dict[str, list[str]]:
        result = {}
        for country in sim_df.index:
            row = sim_df.loc[country].drop(country).sort_values(ascending=False)
            result[country] = list(row.index[:n])
        return result

    base_topn = get_top_n(base_sim, top_n)
    sensitivity_results: dict[str, list[str]] = {c: [] for c in countries}

    categories = [k for k, v in base_weights.items() if v > 0]
    for cat in categories:
        for direction in [+delta, -delta]:
            modified_weights = dict(base_weights)
            modified_weights[cat] = max(0.0, base_weights[cat] * (1 + direction))
            # Renormalize
            total = sum(modified_weights.values())
            if total > 0:
                modified_weights = {k: v / total for k, v in modified_weights.items()}

            mod_sim = composite_similarity_matrix(features_df, modified_weights)
            mod_topn = get_top_n(mod_sim, top_n)

            for country in countries:
                if set(base_topn[country]) != set(mod_topn[country]):
                    tag = f"{cat}({'+' if direction > 0 else '-'}{int(delta*100)}%)"
                    if tag not in sensitivity_results[country]:
                        sensitivity_results[country].append(tag)

    return sensitivity_results


# ---------------------------------------------------------------------------
# Standalone run
# ---------------------------------------------------------------------------

def run(category_weights: dict[str, float] | None = None) -> pd.DataFrame:
    feat_path = _ROOT / CFG["paths"]["features_file"]
    if not feat_path.exists():
        raise FileNotFoundError(f"Features file not found: {feat_path}. Run preprocessing first.")

    features_df = pd.read_csv(feat_path, index_col=0)
    sim_df = composite_similarity_matrix(features_df, category_weights)

    out_path = _ROOT / CFG["paths"]["similarity_matrix"]
    sim_df.to_csv(out_path)
    log.info("Saved similarity matrix to %s", out_path)

    # Quick sanity check
    _sanity_check(sim_df)

    return sim_df


def _sanity_check(sim_df: pd.DataFrame) -> None:
    """Log expected cluster relationships as a sanity check."""
    log.info("=== Sanity Check: Expected Relationships ===")
    checks = [
        ("Uruguay", "Chile", "Expected HIGH (both high-development democracies)"),
        ("Uruguay", "Costa Rica", "Expected HIGH (democracy + development cluster)"),
        ("Honduras", "Guatemala", "Expected HIGH (Northern Triangle cluster)"),
        ("Honduras", "El Salvador", "Expected HIGH (Northern Triangle cluster)"),
        ("Haiti", "Uruguay", "Expected LOW (extreme development divergence)"),
        ("Venezuela", "Uruguay", "Expected LOW (democracy divergence)"),
    ]
    countries = list(sim_df.index)
    for a, b, label in checks:
        if a in countries and b in countries:
            score = sim_df.loc[a, b]
            log.info("  %s vs %s = %.3f  [%s]", a, b, score, label)


if __name__ == "__main__":
    run()
