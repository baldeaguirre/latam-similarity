"""
src/visualizations.py
=====================
All Plotly chart builders for the LatAm similarity dashboard.
Reads theme tokens from config.yaml. No hardcoded hex values.

Charts:
  1. similarity_heatmap()        — N×N clustered heatmap
  2. scatter_embeddings()        — 2D scatter (PCA/t-SNE/UMAP toggle)
  3. scatter_3d_pca()            — 3D PCA scatter
  4. dendrogram_chart()          — Ward hierarchical clustering
  5. radar_chart()               — Category scores for ≤4 countries
  6. top_n_bar()                 — Most/least similar peers for a country
  7. contribution_bar()          — Indicator contributions for a country pair
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
import yaml
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import squareform

_ROOT = Path(__file__).parent.parent
with open(_ROOT / "config.yaml") as f:
    CFG = yaml.safe_load(f)

THEME = CFG["theme"]
COUNTRIES = {c["iso2"]: c["name"] for c in CFG["countries"]}
ISO2_BY_NAME = {c["name"]: c["iso2"] for c in CFG["countries"]}
IND_CONFIG = {ind["id"]: ind for ind in CFG["indicators"]}

# ---------------------------------------------------------------------------
# Design tokens (from config.yaml / DESIGN.md)
# ---------------------------------------------------------------------------
CANVAS = THEME["color_canvas"]
SURFACE = THEME["color_surface"]
SURFACE_RAISED = THEME["color_surface_raised"]
BORDER = THEME["color_border"]
BORDER_SUBTLE = THEME["color_border_subtle"]
TEXT_PRIMARY = THEME["color_text_primary"]
TEXT_SECONDARY = THEME["color_text_secondary"]
ACCENT = THEME["color_accent"]
SUCCESS = THEME["color_success"]
DANGER = THEME["color_danger"]
FONT_BODY = THEME["font_body"]
FONT_MONO = THEME["font_mono"]

CAT_PALETTE = THEME["categorical_palette"]
COUNTRY_COLORS = [CAT_PALETTE.get(ISO2_BY_NAME.get(c["name"], ""), ACCENT) for c in CFG["countries"]]

# Sequential colorscale (blue → amber)
SEQ_COLORSCALE = [
    [0.00, "#0D1117"], [0.14, "#0F2A4A"], [0.28, "#133E6E"],
    [0.43, "#1A5C96"], [0.57, "#2E7DB8"], [0.71, "#6FA8CE"],
    [0.86, "#F5C842"], [1.00, "#F59E0B"],
]

# Diverging colorscale (red → teal)
DIV_COLORSCALE = [
    [0.00, "#7F1D1D"], [0.125, "#B91C1C"], [0.25, "#DC2626"],
    [0.375, "#FCA5A5"], [0.50, "#21262D"], [0.625, "#6EE7B7"],
    [0.75, "#059669"], [0.875, "#065F46"], [1.00, "#022C22"],
]


# ---------------------------------------------------------------------------
# Base layout helper
# ---------------------------------------------------------------------------

def _base_layout(title: str = "", height: int = 500) -> dict:
    return dict(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE_RAISED,
        font=dict(family=f"{FONT_BODY}, system-ui, sans-serif", color=TEXT_PRIMARY, size=13),
        title=dict(
            text=title,
            font=dict(size=14, color=TEXT_PRIMARY, family=FONT_BODY),
            x=0, xanchor="left", pad=dict(l=4),
        ),
        height=height,
        margin=dict(l=60, r=20, t=50, b=60),
        hoverlabel=dict(
            bgcolor=SURFACE_RAISED,
            bordercolor=BORDER,
            font=dict(size=12, color=TEXT_PRIMARY, family=FONT_MONO),
        ),
        legend=dict(
            bgcolor=SURFACE,
            bordercolor=BORDER,
            borderwidth=1,
            font=dict(size=12, color=TEXT_PRIMARY),
        ),
    )


def _axis_style(title_text: str = "") -> dict:
    return dict(
        gridcolor=BORDER_SUBTLE,
        linecolor=BORDER,
        tickcolor=BORDER,
        tickfont=dict(size=11, color=TEXT_SECONDARY, family=FONT_MONO),
        title=dict(text=title_text, font=dict(size=12, color=TEXT_SECONDARY)),
        zerolinecolor=BORDER,
    )


# ---------------------------------------------------------------------------
# 1. Similarity Heatmap
# ---------------------------------------------------------------------------

def similarity_heatmap(sim_df: pd.DataFrame) -> go.Figure:
    """N×N clustered similarity heatmap."""
    countries = list(sim_df.index)

    # Hierarchical clustering for row/column reordering
    dist_mat = 1.0 - sim_df.values
    np.fill_diagonal(dist_mat, 0)
    condensed = squareform(np.clip(dist_mat, 0, None))
    Z = linkage(condensed, method="ward")
    order = leaves_list(Z)

    reordered = sim_df.iloc[order, :].iloc[:, order]
    labels = [countries[i] for i in order]
    iso2_labels = [ISO2_BY_NAME.get(c, c) for c in labels]

    hover_text = []
    for i, ca in enumerate(labels):
        row = []
        for j, cb in enumerate(labels):
            score = reordered.iloc[i, j]
            row.append(f"<b>{ca}</b> ↔ <b>{cb}</b><br>Similarity: {score:.3f}")
        hover_text.append(row)

    fig = go.Figure(go.Heatmap(
        z=reordered.values,
        x=iso2_labels,
        y=iso2_labels,
        colorscale=SEQ_COLORSCALE,
        zmin=0, zmax=1,
        text=hover_text,
        hovertemplate="%{text}<extra></extra>",
        colorbar=dict(
            title=dict(text="Similarity", font=dict(size=12, color=TEXT_SECONDARY)),
            tickfont=dict(size=11, color=TEXT_SECONDARY, family=FONT_MONO),
            bgcolor=SURFACE,
            bordercolor=BORDER,
        ),
    ))

    layout = _base_layout("Pairwise Similarity Heatmap (Ward-clustered)", height=560)
    layout["xaxis"] = dict(
        tickfont=dict(size=11, color=TEXT_SECONDARY, family=FONT_MONO),
        linecolor=BORDER, tickcolor=BORDER,
        title=dict(text="", font=dict(size=11)),
    )
    layout["yaxis"] = dict(
        tickfont=dict(size=11, color=TEXT_SECONDARY, family=FONT_MONO),
        linecolor=BORDER, tickcolor=BORDER,
        title=dict(text="", font=dict(size=11)),
    )
    layout["annotations"] = [dict(
        text="Source: latam-similarity composite score (cosine + Euclidean + Pearson) | Ordered by Ward hierarchical clustering",
        x=0, y=-0.12, xref="paper", yref="paper",
        font=dict(size=10, color=TEXT_SECONDARY), showarrow=False, xanchor="left",
    )]
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# 2. Scatter Embedding (2D)
# ---------------------------------------------------------------------------

def scatter_embeddings(
    embeddings_df: pd.DataFrame,
    sim_df: pd.DataFrame,
    method: str = "pca",
    features_df: pd.DataFrame | None = None,
) -> go.Figure:
    """
    2D scatter plot for PCA / t-SNE / UMAP.
    method: 'pca' | 'tsne' | 't-sne' | 't-SNE' | 'umap' — any casing/hyphenation accepted.
    """
    # Normalize method name → CSV column prefix
    # e.g. "t-SNE", "t-sne", "tsne" all → "tsne"  (matches embeddings CSV columns)
    _METHOD_KEY = {
        "pca":   "pca",
        "tsne":  "tsne",
        "t-sne": "tsne",
        "umap":  "umap",
    }
    method_key = _METHOD_KEY.get(method.lower(), "pca")

    x_col = f"{method_key}_x"
    y_col = f"{method_key}_y"

    # Safety fallback (should never trigger after normalization)
    if x_col not in embeddings_df.columns:
        x_col, y_col = "pca_x", "pca_y"
        method_key = "pca"

    countries = list(embeddings_df.index)
    axis_labels = {
        "pca":  ("PC1", "PC2"),
        "tsne": ("t-SNE 1", "t-SNE 2"),
        "umap": ("UMAP 1", "UMAP 2"),
    }
    xlabel, ylabel = axis_labels.get(method_key, ("X", "Y"))

    traces = []
    for i, country in enumerate(countries):
        iso2 = ISO2_BY_NAME.get(country, country[:2])
        color = CAT_PALETTE.get(iso2, ACCENT)
        x = embeddings_df.loc[country, x_col]
        y = embeddings_df.loc[country, y_col]

        # Top-3 most similar peers (for hover)
        if sim_df is not None and country in sim_df.index:
            peers = sim_df.loc[country].drop(country).sort_values(ascending=False).head(3)
            peers_str = "<br>".join([f"  {p}: {v:.3f}" for p, v in peers.items()])
        else:
            peers_str = "N/A"

        hover = (
            f"<b>{country}</b> ({iso2})<br>"
            f"<br><b>Top-3 Most Similar:</b><br>{peers_str}"
        )

        traces.append(go.Scatter(
            x=[x], y=[y],
            mode="markers+text",
            marker=dict(size=14, color=color, line=dict(width=1.5, color=SURFACE_RAISED)),
            text=[iso2],
            textposition="top center",
            textfont=dict(size=11, color=color, family=FONT_MONO),
            name=country,
            hovertemplate=hover + "<extra></extra>",
            legendgroup=country,
        ))

    fig = go.Figure(traces)

    method_title = {"pca": "PCA", "tsne": "t-SNE", "umap": "UMAP"}.get(method_key, method_key.upper())
    layout = _base_layout(f"Country Vector Embeddings — {method_title}", height=520)
    layout["xaxis"] = _axis_style(xlabel)
    layout["yaxis"] = _axis_style(ylabel)
    layout["showlegend"] = True
    layout["annotations"] = [dict(
        text=f"Projection: {method_title} | Each point = one country | Hover for top-3 peers",
        x=0, y=-0.12, xref="paper", yref="paper",
        font=dict(size=10, color=TEXT_SECONDARY), showarrow=False, xanchor="left",
    )]
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# 3. 3D PCA Scatter
# ---------------------------------------------------------------------------

def scatter_3d_pca(embeddings_df: pd.DataFrame, sim_df: pd.DataFrame) -> go.Figure:
    """3D PCA scatter plot."""
    countries = list(embeddings_df.index)
    traces = []
    for country in countries:
        iso2 = ISO2_BY_NAME.get(country, country[:2])
        color = CAT_PALETTE.get(iso2, ACCENT)

        if sim_df is not None and country in sim_df.index:
            peers = sim_df.loc[country].drop(country).sort_values(ascending=False).head(3)
            peers_str = "<br>".join([f"  {p}: {v:.3f}" for p, v in peers.items()])
        else:
            peers_str = "N/A"

        hover = f"<b>{country}</b> ({iso2})<br><br><b>Top-3:</b><br>{peers_str}"

        traces.append(go.Scatter3d(
            x=[embeddings_df.loc[country, "pca_x"]],
            y=[embeddings_df.loc[country, "pca_y"]],
            z=[embeddings_df.loc[country, "pca_z"]],
            mode="markers+text",
            marker=dict(size=8, color=color, opacity=0.9, line=dict(width=1, color=SURFACE)),
            text=[iso2],
            textfont=dict(size=10, color=color, family=FONT_MONO),
            name=country,
            hovertemplate=hover + "<extra></extra>",
        ))

    fig = go.Figure(traces)
    fig.update_layout(
        paper_bgcolor=SURFACE,
        font=dict(family=FONT_BODY, color=TEXT_PRIMARY, size=12),
        title=dict(text="3D PCA — Country Feature Space", font=dict(size=14, color=TEXT_PRIMARY), x=0),
        height=560,
        margin=dict(l=0, r=0, t=50, b=0),
        scene=dict(
            xaxis=dict(title="PC1", backgroundcolor=SURFACE_RAISED, gridcolor=BORDER_SUBTLE, color=TEXT_SECONDARY),
            yaxis=dict(title="PC2", backgroundcolor=SURFACE_RAISED, gridcolor=BORDER_SUBTLE, color=TEXT_SECONDARY),
            zaxis=dict(title="PC3", backgroundcolor=SURFACE_RAISED, gridcolor=BORDER_SUBTLE, color=TEXT_SECONDARY),
            bgcolor=CANVAS,
        ),
        legend=dict(bgcolor=SURFACE, bordercolor=BORDER, borderwidth=1, font=dict(size=11, color=TEXT_PRIMARY)),
    )
    return fig


# ---------------------------------------------------------------------------
# 4. Dendrogram
# ---------------------------------------------------------------------------

def dendrogram_chart(sim_df: pd.DataFrame) -> go.Figure:
    """Ward-linkage hierarchical clustering dendrogram."""
    countries = list(sim_df.index)
    dist_mat = 1.0 - sim_df.values
    np.fill_diagonal(dist_mat, 0)
    condensed = squareform(np.clip(dist_mat, 0, None))

    labels = [ISO2_BY_NAME.get(c, c) for c in countries]

    fig = ff.create_dendrogram(
        dist_mat,
        orientation="bottom",
        labels=labels,
        colorscale=[ACCENT, SUCCESS, "#56B4E9", "#CC79A7", "#009E73"],
        linkagefun=lambda x: linkage(x, method="ward"),
    )

    fig.update_layout(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE_RAISED,
        font=dict(family=FONT_BODY, color=TEXT_PRIMARY, size=12),
        title=dict(
            text="Hierarchical Clustering Dendrogram (Ward Linkage)",
            font=dict(size=14, color=TEXT_PRIMARY), x=0,
        ),
        height=480,
        margin=dict(l=60, r=20, t=50, b=80),
        xaxis=dict(tickfont=dict(size=11, color=TEXT_SECONDARY, family=FONT_MONO), linecolor=BORDER),
        yaxis=dict(
            title=dict(text="Distance (1 − similarity)", font=dict(size=12, color=TEXT_SECONDARY)),
            tickfont=dict(size=11, color=TEXT_SECONDARY, family=FONT_MONO),
            gridcolor=BORDER_SUBTLE, linecolor=BORDER,
        ),
        annotations=[dict(
            text="Method: Ward linkage | Distance = 1 − composite similarity score",
            x=0, y=-0.15, xref="paper", yref="paper",
            font=dict(size=10, color=TEXT_SECONDARY), showarrow=False, xanchor="left",
        )],
    )
    return fig


# ---------------------------------------------------------------------------
# 5. Radar Chart
# ---------------------------------------------------------------------------

def radar_chart(
    features_df: pd.DataFrame,
    selected_countries: list[str],
) -> go.Figure:
    """
    Radar chart overlaying normalized category scores for up to 4 countries.
    """
    ind_config = IND_CONFIG
    categories_order = ["economy", "social", "education", "health",
                        "governance", "infrastructure", "democracy", "productivity"]

    # Compute mean z-score per category per country (higher = better after reverse-coding)
    cat_scores: dict[str, dict[str, float]] = {}
    for country in selected_countries:
        if country not in features_df.index:
            continue
        scores = {}
        for cat in categories_order:
            cols = [c for c in features_df.columns
                    if ind_config.get(c, {}).get("category") == cat]
            if cols:
                scores[cat] = float(features_df.loc[country, cols].mean())
            else:
                scores[cat] = 0.0
        cat_scores[country] = scores

    # Normalize to [0, 1] within each category across all countries in features_df
    cat_min_max: dict[str, tuple[float, float]] = {}
    for cat in categories_order:
        cols = [c for c in features_df.columns if ind_config.get(c, {}).get("category") == cat]
        if cols:
            all_vals = features_df[cols].mean(axis=1)
            cat_min_max[cat] = (float(all_vals.min()), float(all_vals.max()))
        else:
            cat_min_max[cat] = (0.0, 1.0)

    def normalize(val: float, cat: str) -> float:
        lo, hi = cat_min_max[cat]
        if hi == lo:
            return 0.5
        return (val - lo) / (hi - lo)

    theta_labels = [c.replace("_", " ").title() for c in categories_order]
    theta_labels_closed = theta_labels + [theta_labels[0]]  # close the polygon

    traces = []
    for country in selected_countries:
        if country not in cat_scores:
            continue
        iso2 = ISO2_BY_NAME.get(country, country[:2])
        color = CAT_PALETTE.get(iso2, ACCENT)
        values = [normalize(cat_scores[country][cat], cat) for cat in categories_order]
        values_closed = values + [values[0]]

        traces.append(go.Scatterpolar(
            r=values_closed,
            theta=theta_labels_closed,
            fill="toself",
            fillcolor=_hex_to_rgba(color, 0.15),
            line=dict(color=color, width=2),
            name=f"{country} ({iso2})",
            hovertemplate=f"<b>{country}</b><br>%{{theta}}: %{{r:.2f}}<extra></extra>",
        ))

    fig = go.Figure(traces)
    fig.update_layout(
        paper_bgcolor=SURFACE,
        font=dict(family=FONT_BODY, color=TEXT_PRIMARY, size=12),
        title=dict(
            text="Category Score Radar (normalized 0–1)",
            font=dict(size=14, color=TEXT_PRIMARY), x=0,
        ),
        height=480,
        polar=dict(
            bgcolor=SURFACE_RAISED,
            radialaxis=dict(
                visible=True, range=[0, 1],
                tickfont=dict(size=10, color=TEXT_SECONDARY, family=FONT_MONO),
                gridcolor=BORDER,
                linecolor=BORDER,
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color=TEXT_SECONDARY),
                linecolor=BORDER,
                gridcolor=BORDER,
            ),
        ),
        legend=dict(bgcolor=SURFACE, bordercolor=BORDER, borderwidth=1),
        margin=dict(l=60, r=60, t=60, b=60),
    )
    return fig


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ---------------------------------------------------------------------------
# 6. Top-N Similarity Bar Chart
# ---------------------------------------------------------------------------

def top_n_bar(sim_df: pd.DataFrame, selected_country: str, n: int = 5) -> go.Figure:
    """
    Bar chart showing the n most-similar and n least-similar peers for a country.
    """
    if selected_country not in sim_df.index:
        return go.Figure()

    row = sim_df.loc[selected_country].drop(selected_country).sort_values(ascending=False)
    top = row.head(n)
    bottom = row.tail(n).sort_values(ascending=True)

    # Build chart
    combined = pd.concat([top, bottom])
    colors = []
    for score in combined.values:
        if score >= 0.80:
            colors.append(SUCCESS)
        elif score >= 0.60:
            colors.append(ACCENT)
        else:
            colors.append(DANGER)

    iso2_labels = [ISO2_BY_NAME.get(c, c) for c in combined.index]

    fig = go.Figure(go.Bar(
        x=combined.values,
        y=iso2_labels,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.3f}" for v in combined.values],
        textposition="outside",
        textfont=dict(size=11, color=TEXT_SECONDARY, family=FONT_MONO),
        hovertemplate="<b>%{y}</b><br>Similarity: %{x:.3f}<extra></extra>",
    ))

    # Add separator line between top and bottom sections
    iso2_selected = ISO2_BY_NAME.get(selected_country, selected_country[:2])
    layout = _base_layout(
        f"Most & Least Similar to {selected_country} ({iso2_selected})",
        height=420,
    )
    layout["xaxis"] = _axis_style("Composite Similarity Score")
    layout["xaxis"]["range"] = [0, 1.1]
    layout["yaxis"] = dict(tickfont=dict(size=11, color=TEXT_SECONDARY, family=FONT_MONO),
                           linecolor=BORDER, tickcolor=BORDER)
    layout["annotations"] = [
        dict(text="▲ Most similar", x=0.98, y=n - 0.5, xref="paper", yref="y",
             font=dict(size=10, color=SUCCESS), showarrow=False, xanchor="right"),
        dict(text="▼ Least similar", x=0.98, y=n + 0.5, xref="paper", yref="y",
             font=dict(size=10, color=DANGER), showarrow=False, xanchor="right"),
        dict(
            text="Source: Composite score = mean(cosine, Euclidean, Pearson) similarities",
            x=0, y=-0.14, xref="paper", yref="paper",
            font=dict(size=10, color=TEXT_SECONDARY), showarrow=False, xanchor="left",
        ),
    ]
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# 7. Pairwise Contribution Bar Chart
# ---------------------------------------------------------------------------

def contribution_bar(
    contribution_series: pd.Series,
    country_a: str,
    country_b: str,
    top_n: int = 15,
) -> go.Figure:
    """
    Horizontal bar chart of each indicator's contribution to the similarity
    between country_a and country_b. Shows top_n most impactful indicators.
    """
    series = contribution_series.sort_values()  # most negative (divergent) first
    # Show most impactful: both extremes
    half = top_n // 2
    display = pd.concat([series.head(half), series.tail(half)])
    display = display[~display.index.duplicated()]

    colors = [SUCCESS if v >= 0 else DANGER for v in display.values]
    ind_labels = [IND_CONFIG.get(c, {}).get("name", c)[:35] for c in display.index]
    cat_labels = [IND_CONFIG.get(c, {}).get("category", "").title() for c in display.index]
    hover_texts = [
        f"<b>{IND_CONFIG.get(c, {}).get('name', c)}</b><br>"
        f"Category: {IND_CONFIG.get(c, {}).get('category', '')}<br>"
        f"Contribution: {v:.4f}"
        for c, v in zip(display.index, display.values)
    ]

    fig = go.Figure(go.Bar(
        x=display.values,
        y=ind_labels,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.4f}" for v in display.values],
        textposition="outside",
        textfont=dict(size=10, color=TEXT_SECONDARY, family=FONT_MONO),
        hovertext=hover_texts,
        hovertemplate="%{hovertext}<extra></extra>",
    ))

    iso2_a = ISO2_BY_NAME.get(country_a, country_a[:2])
    iso2_b = ISO2_BY_NAME.get(country_b, country_b[:2])
    layout = _base_layout(
        f"Indicator Contributions: {country_a} ({iso2_a}) ↔ {country_b} ({iso2_b})",
        height=480,
    )
    layout["xaxis"] = _axis_style("Weighted Contribution (− = divergent, + = similar)")
    layout["xaxis"]["zeroline"] = True
    layout["xaxis"]["zerolinecolor"] = BORDER
    layout["xaxis"]["zerolinewidth"] = 1
    layout["yaxis"] = dict(
        tickfont=dict(size=10, color=TEXT_SECONDARY),
        linecolor=BORDER,
        automargin=True,
    )
    layout["annotations"] = [dict(
        text="Positive = countries agree on this indicator  |  Negative = countries diverge",
        x=0, y=-0.12, xref="paper", yref="paper",
        font=dict(size=10, color=TEXT_SECONDARY), showarrow=False, xanchor="left",
    )]
    layout["margin"]["l"] = 240  # wide left margin for long indicator names
    fig.update_layout(**layout)
    return fig
