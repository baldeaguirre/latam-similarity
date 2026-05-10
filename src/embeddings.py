"""
src/embeddings.py
=================
Projects the weighted feature matrix into 2D/3D using PCA, t-SNE, and UMAP.
All stochastic methods seeded with random_state=42.

Saves: data/processed/embeddings.csv

Run standalone: python -m src.embeddings
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.decomposition import PCA

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

_ROOT = Path(__file__).parent.parent
with open(_ROOT / "config.yaml") as f:
    CFG = yaml.safe_load(f)

EMBED_CFG = CFG["embeddings"]
RANDOM_STATE = EMBED_CFG["random_state"]


def run_pca(X: np.ndarray, n_components: int = 3) -> tuple[np.ndarray, list[float]]:
    """
    Run PCA. Returns (coordinates, explained_variance_ratio).
    coordinates shape: (n_samples, n_components)
    """
    pca = PCA(n_components=n_components, random_state=RANDOM_STATE)
    coords = pca.fit_transform(X)
    evr = list(pca.explained_variance_ratio_)
    log.info("PCA explained variance: %s", [f"{v:.2%}" for v in evr])
    return coords, evr


def run_tsne(X: np.ndarray, n_components: int = 2) -> np.ndarray:
    """Run t-SNE with config parameters."""
    from sklearn.manifold import TSNE
    tsne_cfg = EMBED_CFG["tsne"]
    # Perplexity must be < n_samples; clamp for small test inputs
    perplexity = min(tsne_cfg["perplexity"], X.shape[0] - 1)
    tsne = TSNE(
        n_components=n_components,
        perplexity=perplexity,
        max_iter=tsne_cfg["n_iter"],
        random_state=RANDOM_STATE,
        learning_rate="auto",
        init="pca",
    )
    coords = tsne.fit_transform(X)
    log.info("t-SNE completed. KL divergence: %.4f", tsne.kl_divergence_)
    return coords


def run_umap(X: np.ndarray, n_components: int = 2) -> np.ndarray:
    """Run UMAP with config parameters."""
    try:
        import umap
    except ImportError:
        log.error("umap-learn not installed. Skipping UMAP. Run: pip install umap-learn")
        return np.zeros((X.shape[0], n_components))

    umap_cfg = EMBED_CFG["umap"]
    reducer = umap.UMAP(
        n_neighbors=umap_cfg["n_neighbors"],
        min_dist=umap_cfg["min_dist"],
        n_components=n_components,
        random_state=RANDOM_STATE,
    )
    coords = reducer.fit_transform(X)
    log.info("UMAP completed.")
    return coords


def compute_embeddings(
    features_df: pd.DataFrame,
    weights: np.ndarray | None = None,
) -> tuple[pd.DataFrame, dict]:
    """
    Compute all embeddings from features_df.

    Parameters
    ----------
    features_df : normalized feature matrix (countries × indicators)
    weights     : optional weight vector to apply before embedding

    Returns
    -------
    embeddings_df : DataFrame with columns:
                    [pca_x, pca_y, pca_z, tsne_x, tsne_y, umap_x, umap_y]
    meta          : dict with PCA explained variance
    """
    countries = list(features_df.index)
    X = features_df.values.astype(float)

    if weights is not None:
        X_weighted = X * weights
    else:
        X_weighted = X

    pca_n = EMBED_CFG["pca"]["n_components"]  # 3
    pca_coords, evr = run_pca(X_weighted, n_components=pca_n)
    tsne_coords = run_tsne(X_weighted)
    umap_coords = run_umap(X_weighted)

    df = pd.DataFrame({
        "country": countries,
        "pca_x": pca_coords[:, 0],
        "pca_y": pca_coords[:, 1],
        "pca_z": pca_coords[:, 2] if pca_n >= 3 else np.zeros(len(countries)),
        "tsne_x": tsne_coords[:, 0],
        "tsne_y": tsne_coords[:, 1],
        "umap_x": umap_coords[:, 0],
        "umap_y": umap_coords[:, 1],
    }).set_index("country")

    meta = {
        "pca_explained_variance": evr,
        "pca_cumulative_variance": list(np.cumsum(evr)),
    }

    return df, meta


def run() -> pd.DataFrame:
    """Load features + weights → compute embeddings → save."""
    feat_path = _ROOT / CFG["paths"]["features_file"]
    if not feat_path.exists():
        raise FileNotFoundError(f"Features not found: {feat_path}. Run preprocessing first.")

    features_df = pd.read_csv(feat_path, index_col=0)

    # Load category weights and build weight vector
    from src.similarity import build_weight_vector
    weights = build_weight_vector(list(features_df.columns))

    embeddings_df, meta = compute_embeddings(features_df, weights)

    out_path = _ROOT / CFG["paths"]["embeddings_file"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    embeddings_df.to_csv(out_path)
    log.info("Saved embeddings to %s", out_path)

    log.info("PCA explained variance per component:")
    for i, v in enumerate(meta["pca_explained_variance"]):
        log.info("  PC%d: %.2f%%  (cumulative: %.2f%%)", i + 1, v * 100, meta["pca_cumulative_variance"][i] * 100)

    return embeddings_df


if __name__ == "__main__":
    run()
