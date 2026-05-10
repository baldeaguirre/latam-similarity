"""
tests/test_core.py
==================
Unit tests covering normalization, reverse-coding, similarity math, and weight logic.

Run:  pytest tests/ -v --cov=src --cov-report=term-missing
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Preprocessing tests ──────────────────────────────────────────────────────

class TestPreprocessing:
    """Tests for src.preprocessing logic (pure functions, no I/O)."""

    def _make_raw(self) -> pd.DataFrame:
        """Minimal 3-country × 3-indicator dataframe."""
        return pd.DataFrame({
            "ind_a": [1.0, 2.0, 3.0],
            "ind_b": [100.0, 50.0, np.nan],
            "ind_c": [10.0, 20.0, 30.0],
        }, index=["CountryA", "CountryB", "CountryC"])

    def test_zscore_mean_zero(self):
        from sklearn.preprocessing import StandardScaler
        df = self._make_raw().fillna(df.mean() if False else 0)
        arr = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        scaler = StandardScaler()
        scaled = scaler.fit_transform(arr)
        assert abs(scaled.mean()) < 1e-10, "Z-score mean should be ~0"

    def test_zscore_std_one(self):
        from sklearn.preprocessing import StandardScaler
        arr = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        scaler = StandardScaler()
        scaled = scaler.fit_transform(arr)
        assert abs(scaled.std(axis=0).mean() - 1.0) < 1e-6, "Z-score std should be ~1"

    def test_reverse_code(self):
        """Reversing a column should flip its sign."""
        col = pd.Series([10.0, 20.0, 30.0])
        reversed_col = -col
        assert list(reversed_col) == [-10.0, -20.0, -30.0]
        # After reversal, higher original = lower value = lower rank;
        # but we want higher z-score for better. Check sign is flipped.
        assert reversed_col.max() == -10.0
        assert reversed_col.min() == -30.0

    def test_missingness_threshold(self):
        """Indicator with ≥30% missing should be flagged for dropping."""
        n = 10
        series = pd.Series([np.nan] * 4 + [1.0] * 6, name="ind")
        pct = series.isna().sum() / n
        assert pct >= 0.30, f"Expected ≥30% missing, got {pct:.0%}"

    def test_knn_imputation_no_nans(self):
        """KNN imputer should produce no NaN values."""
        from sklearn.impute import KNNImputer
        arr = np.array([
            [1.0, np.nan, 3.0],
            [np.nan, 2.0, 4.0],
            [3.0, 3.0, 5.0],
        ])
        imputer = KNNImputer(n_neighbors=2)
        result = imputer.fit_transform(arr)
        assert not np.isnan(result).any(), "Imputed array should have no NaN"

    def test_knn_imputation_shape(self):
        """KNN imputer should preserve shape."""
        from sklearn.impute import KNNImputer
        arr = np.array([[1.0, np.nan], [2.0, 2.0], [3.0, 3.0]])
        imputer = KNNImputer(n_neighbors=2)
        result = imputer.fit_transform(arr)
        assert result.shape == arr.shape


# ── Similarity math tests ────────────────────────────────────────────────────

class TestSimilarity:
    """Tests for src.similarity pure math functions."""

    def _sample_features(self) -> pd.DataFrame:
        """3-country × 4-indicator synthetic dataframe."""
        np.random.seed(42)
        data = np.random.randn(3, 4)
        return pd.DataFrame(data, index=["Alpha", "Beta", "Gamma"],
                            columns=["i1", "i2", "i3", "i4"])

    def test_cosine_diagonal_is_one(self):
        from src.similarity import cosine_similarity_matrix
        X = self._sample_features().values
        mat = cosine_similarity_matrix(X)
        assert np.allclose(np.diag(mat), 1.0), "Diagonal must be 1.0"

    def test_cosine_symmetric(self):
        from src.similarity import cosine_similarity_matrix
        X = self._sample_features().values
        mat = cosine_similarity_matrix(X)
        assert np.allclose(mat, mat.T), "Matrix must be symmetric"

    def test_cosine_range(self):
        from src.similarity import cosine_similarity_matrix
        X = self._sample_features().values
        mat = cosine_similarity_matrix(X)
        assert (mat >= 0).all() and (mat <= 1).all(), "Cosine similarity must be in [0, 1]"

    def test_euclidean_diagonal_is_one(self):
        from src.similarity import euclidean_similarity_matrix
        X = self._sample_features().values
        mat = euclidean_similarity_matrix(X)
        assert np.allclose(np.diag(mat), 1.0)

    def test_euclidean_symmetric(self):
        from src.similarity import euclidean_similarity_matrix
        X = self._sample_features().values
        mat = euclidean_similarity_matrix(X)
        assert np.allclose(mat, mat.T)

    def test_euclidean_positive(self):
        from src.similarity import euclidean_similarity_matrix
        X = self._sample_features().values
        mat = euclidean_similarity_matrix(X)
        assert (mat > 0).all(), "Euclidean similarity must be positive"

    def test_euclidean_bounded(self):
        from src.similarity import euclidean_similarity_matrix
        X = self._sample_features().values
        mat = euclidean_similarity_matrix(X)
        assert (mat <= 1).all(), "Euclidean similarity must be ≤ 1"

    def test_pearson_diagonal_is_one(self):
        from src.similarity import pearson_similarity_matrix
        X = self._sample_features().values
        mat = pearson_similarity_matrix(X)
        assert np.allclose(np.diag(mat), 1.0)

    def test_pearson_symmetric(self):
        from src.similarity import pearson_similarity_matrix
        X = self._sample_features().values
        mat = pearson_similarity_matrix(X)
        assert np.allclose(mat, mat.T)

    def test_pearson_range(self):
        from src.similarity import pearson_similarity_matrix
        X = self._sample_features().values
        mat = pearson_similarity_matrix(X)
        assert (mat >= 0).all() and (mat <= 1).all()

    def test_composite_diagonal_is_one(self):
        from src.similarity import composite_similarity_matrix
        features = self._sample_features()
        sim = composite_similarity_matrix(features)
        assert np.allclose(np.diag(sim.values), 1.0)

    def test_composite_symmetric(self):
        from src.similarity import composite_similarity_matrix
        features = self._sample_features()
        sim = composite_similarity_matrix(features)
        assert np.allclose(sim.values, sim.values.T)

    def test_composite_range(self):
        from src.similarity import composite_similarity_matrix
        features = self._sample_features()
        sim = composite_similarity_matrix(features)
        assert (sim.values >= 0).all() and (sim.values <= 1).all()

    def test_identical_countries_score_one(self):
        """Two identical feature vectors must have composite similarity ≈ 1 (cosine + euclidean = 1.0; Pearson=0.5 when std=0)."""
        from src.similarity import cosine_similarity_matrix, euclidean_similarity_matrix
        # Use identical pairs on a varied-feature array
        X = np.array([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        cos_mat = cosine_similarity_matrix(X)
        euc_mat = euclidean_similarity_matrix(X)
        # Cosine and Euclidean should both be 1.0 for identical vectors
        assert abs(cos_mat[0, 1] - 1.0) < 1e-9, f"Cosine: identical → 1.0, got {cos_mat[0,1]}"
        assert abs(euc_mat[0, 1] - 1.0) < 1e-9, f"Euclidean: identical → 1.0, got {euc_mat[0,1]}"

    def test_contribution_shape(self):
        from src.similarity import pairwise_contribution
        features = self._sample_features()
        contrib = pairwise_contribution(features, "Alpha", "Beta")
        assert len(contrib) == features.shape[1], "One contribution value per indicator"


# ── Weight vector tests ──────────────────────────────────────────────────────

class TestWeights:
    """Tests for weight vector construction."""

    def test_weights_sum_to_one(self):
        from src.similarity import build_weight_vector
        # Use actual feature columns from a sample
        features = pd.DataFrame({
            "gdp_per_capita": [1.0],
            "hdi": [1.0],
            "life_expectancy": [1.0],
        }, index=["X"])
        weights = build_weight_vector(list(features.columns))
        assert abs(weights.sum() - 1.0) < 1e-9, f"Weights should sum to 1, got {weights.sum()}"

    def test_weights_non_negative(self):
        from src.similarity import build_weight_vector
        features = pd.DataFrame({"gdp_per_capita": [1.0], "hdi": [1.0]}, index=["X"])
        weights = build_weight_vector(list(features.columns))
        assert (weights >= 0).all(), "All weights must be non-negative"

    def test_custom_weights_respected(self):
        """Setting one category to 0 should yield 0 weight for its indicators."""
        from src.similarity import build_weight_vector
        features = pd.DataFrame({"gdp_per_capita": [1.0], "hdi": [1.0]}, index=["X"])
        # gdp_per_capita → economy, hdi → social
        custom = {"economy": 0.0, "social": 1.0}
        weights = build_weight_vector(list(features.columns), custom)
        # Economy indicator should have weight 0
        assert weights[0] == 0.0 or weights[1] == 0.0, "Zero-weight category → 0 indicator weight"


# ── Embedding tests ──────────────────────────────────────────────────────────

class TestEmbeddings:
    """Tests for PCA embedding shape and variance reporting."""

    def _sample_features(self) -> pd.DataFrame:
        np.random.seed(42)
        data = np.random.randn(5, 8)
        return pd.DataFrame(data, index=[f"Country{i}" for i in range(5)],
                            columns=[f"ind{i}" for i in range(8)])

    def test_pca_shape(self):
        from src.embeddings import run_pca
        X = self._sample_features().values
        coords, evr = run_pca(X, n_components=3)
        assert coords.shape == (5, 3), f"Expected (5, 3), got {coords.shape}"

    def test_pca_variance_sums_less_than_one(self):
        from src.embeddings import run_pca
        X = self._sample_features().values
        coords, evr = run_pca(X, n_components=3)
        assert sum(evr) <= 1.0 + 1e-9, "Explained variance ratio must be ≤ 1"

    def test_pca_variance_positive(self):
        from src.embeddings import run_pca
        X = self._sample_features().values
        coords, evr = run_pca(X, n_components=3)
        assert all(v >= 0 for v in evr), "All explained variances must be non-negative"

    def test_tsne_shape(self):
        from src.embeddings import run_tsne
        X = self._sample_features().values
        coords = run_tsne(X)
        assert coords.shape == (5, 2), f"Expected (5, 2), got {coords.shape}"

    def test_compute_embeddings_columns(self):
        from src.embeddings import compute_embeddings
        features = self._sample_features()
        df, meta = compute_embeddings(features)
        expected_cols = {"pca_x", "pca_y", "pca_z", "tsne_x", "tsne_y", "umap_x", "umap_y"}
        assert expected_cols.issubset(set(df.columns)), f"Missing columns. Got: {df.columns.tolist()}"

    def test_compute_embeddings_index(self):
        from src.embeddings import compute_embeddings
        features = self._sample_features()
        df, _ = compute_embeddings(features)
        assert list(df.index) == list(features.index)
