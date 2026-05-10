"""
app/dashboard.py
================
Streamlit interactive dashboard for the LatAm Similarity system.

Run:  streamlit run app/dashboard.py

Layout:
  Header → Left control panel → Primary chart area → Secondary panels → Pairwise contribution
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

# Ensure project root is on path
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

with open(_ROOT / "config.yaml") as f:
    CFG = yaml.safe_load(f)

# Import src modules at top level so Streamlit's file-watcher picks up changes
# and triggers a full reload when any src/*.py file is modified.
from src.similarity import composite_similarity_matrix, pairwise_contribution, build_weight_vector
from src.visualizations import (
    similarity_heatmap, scatter_embeddings, scatter_3d_pca,
    dendrogram_chart, radar_chart, top_n_bar, contribution_bar,
)

THEME = CFG["theme"]
COUNTRIES_CFG = CFG["countries"]
COUNTRY_NAMES = [c["name"] for c in COUNTRIES_CFG]
IND_CONFIG = {ind["id"]: ind for ind in CFG["indicators"]}
ISO2_BY_NAME = {c["name"]: c["iso2"] for c in COUNTRIES_CFG}

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LatAm Similarity Score",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', system-ui, sans-serif !important;
        background-color: {THEME["color_canvas"]};
        color: {THEME["color_text_primary"]};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {THEME["color_surface"]};
        border-right: 1px solid {THEME["color_border"]};
    }}
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {THEME["color_text_secondary"]};
        margin-bottom: 8px;
        margin-top: 20px;
    }}

    /* Cards */
    .latam-card {{
        background: {THEME["color_surface"]};
        border: 1px solid {THEME["color_border"]};
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
    }}
    .latam-card-title {{
        font-size: 14px;
        font-weight: 600;
        color: {THEME["color_text_primary"]};
        margin-bottom: 4px;
    }}
    .latam-card-subtitle {{
        font-size: 12px;
        color: {THEME["color_text_secondary"]};
        margin-bottom: 16px;
    }}

    /* Similarity score chip */
    .sim-chip-high {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        background: {THEME["color_success_dim"]};
        color: {THEME["color_success"]};
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 500;
    }}
    .sim-chip-mid {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        background: {THEME["color_accent_dim"]};
        color: {THEME["color_accent"]};
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 500;
    }}
    .sim-chip-low {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        background: {THEME["color_surface_raised"]};
        color: {THEME["color_text_secondary"]};
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 500;
    }}

    /* Header */
    .latam-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 0 20px 0;
        border-bottom: 1px solid {THEME["color_border"]};
        margin-bottom: 24px;
    }}
    .latam-header h1 {{
        font-size: 22px;
        font-weight: 700;
        color: {THEME["color_text_primary"]};
        margin: 0;
        letter-spacing: -0.02em;
    }}
    .latam-header .subtitle {{
        font-size: 13px;
        color: {THEME["color_text_secondary"]};
        margin-top: 2px;
    }}
    .latam-badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        background: {THEME["color_accent_dim"]};
        color: {THEME["color_accent"]};
        font-size: 11px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }}

    /* Override Streamlit selectbox / slider */
    .stSelectbox > div > div {{
        background-color: {THEME["color_canvas"]};
        border: 1px solid {THEME["color_border"]};
        border-radius: 6px;
        color: {THEME["color_text_primary"]};
    }}
    .stSlider .rc-slider-track {{ background-color: {THEME["color_accent"]}; }}
    .stSlider .rc-slider-handle {{ background-color: {THEME["color_accent"]}; border-color: {THEME["color_accent"]}; }}

    /* Plotly charts transparent outer background */
    .js-plotly-plot, .plotly {{
        border-radius: 4px;
    }}

    /* Data labels */
    .data-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 500;
        color: {THEME["color_text_primary"]};
    }}

    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Data loading (cached) ──────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_data():
    """Load processed CSVs. Returns (features_df, sim_df, embeddings_df) or Nones."""
    feat_path = _ROOT / CFG["paths"]["features_file"]
    sim_path = _ROOT / CFG["paths"]["similarity_matrix"]
    emb_path = _ROOT / CFG["paths"]["embeddings_file"]

    features_df = pd.read_csv(feat_path, index_col=0) if feat_path.exists() else None
    sim_df = pd.read_csv(sim_path, index_col=0) if sim_path.exists() else None
    embeddings_df = pd.read_csv(emb_path, index_col=0) if emb_path.exists() else None
    return features_df, sim_df, embeddings_df


def _data_missing_banner():
    st.error(
        "⚠️ **Processed data not found.** "
        "Run the pipeline first:\n\n"
        "```bash\npython -m src.pipeline\n```",
        icon="⚠️",
    )


def _sim_chip(score: float) -> str:
    if score >= 0.80:
        return f'<span class="sim-chip-high">{score:.3f}</span>'
    elif score >= 0.60:
        return f'<span class="sim-chip-mid">{score:.3f}</span>'
    else:
        return f'<span class="sim-chip-low">{score:.3f}</span>'


# ── Main App ──────────────────────────────────────────────────────────────────

def main():
    features_df, sim_df, embeddings_df = load_data()
    data_ready = features_df is not None and sim_df is not None and embeddings_df is not None

    # ── Header ──
    st.markdown(
        """
        <div class="latam-header">
          <div>
            <h1>🌎 LatAm Quality-of-Life Similarity</h1>
            <div class="subtitle">
              20 Latin American countries · 9 socioeconomic categories · composite similarity score
            </div>
          </div>
          <div>
            <span class="latam-badge">v1.0</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Controls")

        st.markdown("### Embedding Method")
        embed_method = st.radio(
            "Projection",
            options=["PCA", "t-SNE", "UMAP"],
            horizontal=False,
            label_visibility="collapsed",
        )

        st.markdown("### Category Weights")
        st.caption("Adjust relative importance of each category. Weights are normalized to sum to 100%.")

        default_weights = CFG.get("category_weights", {})
        categories = ["economy", "social", "education", "health",
                      "governance", "infrastructure", "democracy", "productivity"]
        weight_sliders: dict[str, float] = {}
        for cat in categories:
            default_val = default_weights.get(cat, 0.125)
            # Round to 2 decimal places so the value is reachable with step=0.01
            # (0.125 is not reachable; it rounds to 0.13)
            default_val_rounded = round(float(default_val), 2)
            w = st.slider(
                cat.title(),
                min_value=0.0,
                max_value=1.0,
                value=default_val_rounded,
                step=0.01,
                key=f"weight_{cat}",
            )
            weight_sliders[cat] = w
        # Normalize weights
        total_w = sum(weight_sliders.values())
        if total_w > 0:
            norm_weights = {k: v / total_w for k, v in weight_sliders.items()}
        else:
            norm_weights = {k: 1 / len(categories) for k in categories}

        if st.button("↺ Reset to equal weights", use_container_width=True):
            for cat in categories:
                # Use rounded value to match step=0.01 granularity
                st.session_state[f"weight_{cat}"] = round(1.0 / len(categories), 2)
            st.rerun()

        st.divider()
        st.markdown("### Country Selectors")
        selected_focus = st.selectbox(
            "Focus country (Top-N chart)",
            options=COUNTRY_NAMES,
            index=COUNTRY_NAMES.index("Mexico"),
        )
        radar_countries = st.multiselect(
            "Radar chart (up to 4 countries)",
            options=COUNTRY_NAMES,
            default=["Mexico", "Colombia", "Brazil", "Chile"],
            max_selections=4,
        )
        pair_a = st.selectbox("Pair A (contribution chart)", options=COUNTRY_NAMES,
                              index=COUNTRY_NAMES.index("Mexico"))
        pair_b = st.selectbox("Pair B (contribution chart)", options=COUNTRY_NAMES,
                              index=COUNTRY_NAMES.index("Venezuela"))

        show_3d = st.checkbox("Show 3D PCA view", value=False)

        st.divider()
        st.caption("Data sources: World Bank, UNDP, UNODC, TI, IEP, WJP, EIU, Freedom House, V-Dem, RSF, ILO, WIPO, WEF · See report.md for details.")

    # ── Main content ──────────────────────────────────────────────────────────
    if not data_ready:
        _data_missing_banner()
        st.markdown("""
        ---
        ### Getting Started

        1. Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```

        2. Run the full pipeline:
        ```bash
        python -m src.pipeline
        ```

        3. Launch this dashboard:
        ```bash
        streamlit run app/dashboard.py
        ```
        """)
        return

    # Recompute with custom weights if changed from defaults
    weights_changed = any(
        abs(norm_weights.get(cat, 0) - (default_weights.get(cat, 0.125))) > 0.005
        for cat in categories
    )

    @st.cache_data(ttl=60)
    def _recompute_sim(norm_weights_hash: str, features_hash: int) -> pd.DataFrame:
        import json
        weights = json.loads(norm_weights_hash)
        return composite_similarity_matrix(features_df, weights)

    if weights_changed:
        import json
        sim_display = _recompute_sim(json.dumps(norm_weights), hash(tuple(features_df.columns.tolist())))
    else:
        sim_display = sim_df

    # ── ROW 1: Heatmap (full width) ───────────────────────────────────────────
    st.markdown('<div class="latam-card">', unsafe_allow_html=True)
    st.markdown('<div class="latam-card-title">Pairwise Similarity Heatmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="latam-card-subtitle">Countries reordered by Ward hierarchical clustering · hover a cell to see the exact score</div>', unsafe_allow_html=True)
    fig_heatmap = similarity_heatmap(sim_display)
    st.plotly_chart(fig_heatmap, use_container_width=True, config={"displayModeBar": True})
    st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 2: Scatter + Dendrogram ───────────────────────────────────────────
    col_scatter, col_dendro = st.columns([3, 2], gap="medium")

    with col_scatter:
        st.markdown('<div class="latam-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="latam-card-title">Vector Representation — {embed_method}</div>', unsafe_allow_html=True)
        st.markdown('<div class="latam-card-subtitle">Each country is a point in high-dimensional indicator space, projected to 2D</div>', unsafe_allow_html=True)

        if show_3d and embed_method == "PCA":
            fig_scatter = scatter_3d_pca(embeddings_df, sim_display)
        else:
            fig_scatter = scatter_embeddings(embeddings_df, sim_display, method=embed_method.lower())

        st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": True})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_dendro:
        st.markdown('<div class="latam-card">', unsafe_allow_html=True)
        st.markdown('<div class="latam-card-title">Hierarchical Clustering Dendrogram</div>', unsafe_allow_html=True)
        st.markdown('<div class="latam-card-subtitle">Ward linkage · distance = 1 − similarity</div>', unsafe_allow_html=True)
        fig_dendro = dendrogram_chart(sim_display)
        st.plotly_chart(fig_dendro, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 3: Radar + Top-N ──────────────────────────────────────────────────
    col_radar, col_topn = st.columns([1, 1], gap="medium")

    with col_radar:
        st.markdown('<div class="latam-card">', unsafe_allow_html=True)
        st.markdown('<div class="latam-card-title">Category Score Radar</div>', unsafe_allow_html=True)
        if radar_countries:
            fig_radar = radar_chart(features_df, radar_countries)
            st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Select at least one country in the sidebar.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_topn:
        st.markdown('<div class="latam-card">', unsafe_allow_html=True)
        iso2_focus = ISO2_BY_NAME.get(selected_focus, "?")
        st.markdown(f'<div class="latam-card-title">Top/Bottom Similarity — {selected_focus} ({iso2_focus})</div>', unsafe_allow_html=True)
        st.markdown('<div class="latam-card-subtitle">5 most similar & 5 least similar peers</div>', unsafe_allow_html=True)
        fig_topn = top_n_bar(sim_display, selected_focus, n=5)
        st.plotly_chart(fig_topn, use_container_width=True, config={"displayModeBar": False})

        # Top-3 score chips
        if selected_focus in sim_display.index:
            peers = sim_display.loc[selected_focus].drop(selected_focus).sort_values(ascending=False).head(3)
            chips_html = " &nbsp; ".join([
                f'{p} {_sim_chip(v)}' for p, v in peers.items()
            ])
            st.markdown(f"<div style='font-size:12px; color:{THEME['color_text_secondary']}; margin-top:8px;'>Top-3: {chips_html}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 4: Pairwise Contribution ─────────────────────────────────────────
    st.markdown('<div class="latam-card">', unsafe_allow_html=True)
    iso2_a = ISO2_BY_NAME.get(pair_a, "?")
    iso2_b = ISO2_BY_NAME.get(pair_b, "?")
    st.markdown(
        f'<div class="latam-card-title">Indicator Contributions: {pair_a} ({iso2_a}) ↔ {pair_b} ({iso2_b})</div>',
        unsafe_allow_html=True,
    )

    if pair_a in sim_display.index and pair_b in sim_display.index and pair_a != pair_b:
        pair_score = sim_display.loc[pair_a, pair_b]
        st.markdown(
            f'<div class="latam-card-subtitle">Composite similarity score: {_sim_chip(pair_score)}</div>',
            unsafe_allow_html=True,
        )
        weights_vec = build_weight_vector(list(features_df.columns), norm_weights)
        contrib = pairwise_contribution(features_df, pair_a, pair_b, norm_weights)
        fig_contrib = contribution_bar(contrib, pair_a, pair_b, top_n=14)
        st.plotly_chart(fig_contrib, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Select two different countries in the sidebar.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Summary stats table ───────────────────────────────────────────────────
    with st.expander("📊 Raw Similarity Matrix", expanded=False):
        st.caption("Full N×N composite similarity matrix. Download CSV for further analysis.")
        st.dataframe(
            sim_display.round(3),
            use_container_width=True,
            height=400,
        )
        csv = sim_display.to_csv()
        st.download_button("⬇ Download similarity_matrix.csv", data=csv,
                           file_name="latam_similarity_matrix.csv", mime="text/csv")

    with st.expander("🔢 Feature Matrix (standardized)", expanded=False):
        st.caption("Z-score normalized, reverse-coded indicator matrix used in all computations.")
        st.dataframe(features_df.round(3), use_container_width=True, height=400)


if __name__ == "__main__":
    main()
