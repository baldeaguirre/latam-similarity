# LatAm Similarity Score System

> Analytical system quantifying how similar Latin American countries are across socioeconomic and quality-of-life dimensions, surfaced through an interactive Streamlit dashboard.

![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Plotly](https://img.shields.io/badge/Plotly-5.22-purple)

## Quick Start

```bash
# 1. Clone and enter the project
cd latam-similarity

# 2. Install dependencies (Python 3.11+)
pip install -r requirements.txt

# 3. Run the full data pipeline (downloads WB data + computes similarity)
python -m src.pipeline

# 4. Launch the dashboard
streamlit run app/dashboard.py
```

## Architecture

```
latam-similarity/
├── DESIGN.md              ← Visual design system (single source of truth for UI tokens)
├── config.yaml            ← Country list, indicator catalog, weights, theme tokens
├── requirements.txt       ← Pinned Python dependencies
├── report.md              ← Methodology, findings, cluster narratives
├── data/
│   ├── raw/               ← Cached raw downloads (World Bank API + static CSVs)
│   └── processed/         ← countries_features.csv, similarity_matrix.csv, embeddings.csv
├── src/
│   ├── pipeline.py        ← CLI entry point  (python -m src.pipeline)
│   ├── data_collection.py ← Downloads/loads all indicators
│   ├── preprocessing.py   ← Missingness filter, KNN imputation, reverse-coding, z-score
│   ├── similarity.py      ← Cosine + Euclidean + Pearson → composite similarity matrix
│   ├── embeddings.py      ← PCA / t-SNE / UMAP projections
│   └── visualizations.py  ← All Plotly chart builders
├── app/
│   └── dashboard.py       ← Streamlit dashboard
├── tests/
│   └── test_core.py       ← 30 unit tests (preprocessing, similarity math, embeddings)
└── .streamlit/
    └── config.toml        ← Streamlit dark theme (tokens from DESIGN.md)
```

## Dashboard Features

| Panel | Chart Type | Description |
|-------|-----------|-------------|
| Heatmap | Plotly Heatmap | N×N similarity matrix, Ward-clustered, hover scores |
| Embeddings | Plotly Scatter | PCA / t-SNE / UMAP toggle; labels + top-3 peers on hover |
| Dendrogram | Plotly Figure Factory | Ward linkage hierarchical clustering |
| Radar | Plotly Scatterpolar | Category scores for ≤4 selected countries |
| Top-N | Plotly Bar | 5 most + 5 least similar peers for any country |
| Contributions | Plotly Bar | Per-indicator similarity contribution for any pair |

## CLI Pipeline

```bash
# Full pipeline
python -m src.pipeline

# Skip re-downloading (use cached data/raw/)
python -m src.pipeline --skip-collect

# Run a single step
python -m src.pipeline --step preprocess
python -m src.pipeline --step similarity
python -m src.pipeline --step embeddings
```

## Tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

All 30 tests pass.

## Countries (20)
Argentina, Bolivia, Brazil, Chile, Colombia, Costa Rica, Cuba, Dominican Republic, Ecuador, El Salvador, Guatemala, Haiti, Honduras, Mexico, Nicaragua, Panama, Paraguay, Peru, Uruguay, Venezuela.

## Categories (8, equal weight by default)
Economy · Social Development · Education · Health · Governance & Security · Infrastructure · Democracy & Political Freedom · Productivity & Competitiveness

Demographics (7 indicators) are held out as structural overlays — not included in similarity computation.

## Key Findings
- **Highest similarity:** Uruguay ↔ Costa Rica (0.889), Uruguay ↔ Chile (0.883)
- **Lowest similarity:** Venezuela ↔ Uruguay (0.401), Haiti ↔ Uruguay (0.449)
- **Mexico's profile:** Clusters most closely with Brazil (0.736) and Peru (0.705) as part of the "Middle-Income Reformers"; diverges most from Cuba (0.493) and Nicaragua (0.500)
- **PCA:** PC1 explains 47.6% of variance (development axis), PC2 explains 17.6% (democracy vs. governance axis)
- **Stable clusters:** High-development democracies (Uruguay/Chile/Costa Rica/Panama) and Northern Triangle (Honduras/Guatemala/El Salvador) are robust to ±20% weight perturbation

## Design System
See [`DESIGN.md`](DESIGN.md) — fully compliant with the [Stitch DESIGN.md format](https://stitch.withgoogle.com/docs/design-md/overview). Theme tokens flow from `DESIGN.md` → `config.yaml` → Python visualizations → Streamlit CSS. No hardcoded hex values in application code.

## Data Sources
| Source | Indicators |
|--------|-----------|
| World Bank API | GDP, life expectancy, health expenditure, electricity, internet, etc. |
| UNDP HDR 2023 | HDI, mean years of schooling |
| Transparency International | CPI 2023 |
| IEP | Global Peace Index 2023 |
| World Justice Project | Rule of Law Index 2023 |
| Economist Intelligence Unit | Democracy Index 2023 |
| Freedom House | Freedom in the World 2024 |
| V-Dem | Liberal Democracy Index 2023 |
| RSF | Press Freedom Index 2024 |
| ILO / Penn World Table | Labor productivity, output per worker |
| WIPO | Global Innovation Index 2023 |
| WEF | Global Competitiveness Index 2019 (final edition) |
| World Bank | Ease of Doing Business 2020 (final edition) |
| UN WPP | Median age 2023 |
| UNODC | Homicide rate 2022 |
