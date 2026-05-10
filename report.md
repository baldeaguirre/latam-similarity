# LatAm Similarity — Methodology & Findings Report

## Executive Summary

This report documents the analytical approach, data quality, and cluster findings for the **Latin American Countries Quality-of-Life Similarity Score System**. The system quantifies how similar 20 Latin American countries are across 9 socioeconomic dimensions using a composite similarity score derived from cosine similarity, Euclidean similarity, and Pearson correlation on a weighted, standardized feature matrix.

---

## 1. Methodology

### 1.1 Country Scope
20 countries: Argentina, Bolivia, Brazil, Chile, Colombia, Costa Rica, Cuba, Dominican Republic, Ecuador, El Salvador, Guatemala, Haiti, Honduras, Mexico, Nicaragua, Panama, Paraguay, Peru, Uruguay, Venezuela.

### 1.2 Indicator Catalog

| # | Indicator | Source | Year | Category | Notes |
|---|-----------|--------|------|----------|-------|
| 1 | GDP (current US$) | World Bank | 2022 | Economy | WB: NY.GDP.MKTP.CD |
| 2 | GDP per capita (current US$) | World Bank | 2022 | Economy | WB: NY.GDP.PCAP.CD |
| 3 | GDP growth (annual %) | World Bank | 2022 | Economy | WB: NY.GDP.MKTP.KD.ZG |
| 4 | FDI net inflows (% of GDP) | World Bank | 2022 | Economy | WB: BX.KLT.DINV.WD.GD.ZS |
| 5 | Inflation (annual %) | World Bank | 2022 | Economy | WB: FP.CPI.TOTL.ZG; **reverse-coded** |
| 6 | Human Development Index | UNDP HDR 2023 | 2022 | Social | Static; see HDR Statistical Annex |
| 7 | Life expectancy at birth | World Bank | 2022 | Social | WB: SP.DYN.LE00.IN |
| 8 | Poverty headcount (national line) | World Bank | 2022 | Social | **DROPPED** — 30% missing |
| 9 | Gini index | World Bank | 2022 | Social | **DROPPED** — 30% missing |
| 10 | Unemployment rate | World Bank/ILO | 2022 | Social | WB: SL.UEM.TOTL.ZS; **reverse-coded** |
| 11 | Mean years of schooling | UNDP HDR 2023 | 2022 | Education | Static |
| 12 | Gov't expenditure on education (% GDP) | UNESCO/WB | 2022 | Education | WB: SE.XPD.TOTL.GD.ZS; 5% imputed |
| 13 | Adult literacy rate | UNESCO/WB | 2022 | Education | **DROPPED** — 30% missing |
| 14 | Health expenditure (% of GDP) | WHO/WB | 2021 | Health | WB: SH.XPD.CHEX.GD.ZS |
| 15 | Hospital beds (per 1,000) | World Bank | 2020 | Health | WB: SH.MED.BEDS.ZS |
| 16 | Physicians (per 1,000) | World Bank | 2020 | Health | WB: SH.MED.PHYS.ZS; 25% KNN-imputed |
| 17 | Infant mortality (per 1,000 live births) | World Bank | 2022 | Health | WB: SP.DYN.IMRT.IN; **reverse-coded** |
| 18 | Corruption Perceptions Index (0–100) | Transparency International | 2023 | Governance | Static; higher = less corrupt |
| 19 | Homicide rate (per 100,000) | UNODC | 2022 | Governance | Static; **reverse-coded** |
| 20 | Global Peace Index | IEP | 2023 | Governance | Static; lower=more peaceful; **reverse-coded** |
| 21 | Rule of Law Index (0–1) | World Justice Project | 2023 | Governance | Static |
| 22 | Access to electricity (% pop) | World Bank | 2022 | Infrastructure | WB: EG.ELC.ACCS.ZS |
| 23 | Internet usage (% pop) | World Bank/ITU | 2022 | Infrastructure | WB: IT.NET.USER.ZS |
| 24 | Logistics Performance Index (1–5) | World Bank | 2023 | Infrastructure | Static |
| 25 | Democracy Index (0–10) | EIU | 2023 | Democracy | Static |
| 26 | Freedom in the World score (0–100) | Freedom House | 2024 | Democracy | Static; aggregate score |
| 27 | Liberal Democracy Index (0–1) | V-Dem | 2023 | Democracy | Static |
| 28 | Press Freedom Index (0–100) | RSF | 2024 | Democracy | Static; 2022+ methodology (higher=more free); note: config has reverse_code=true for legacy compatibility — **NOT applied** since 2024 data is already higher=better |
| 29 | Labor productivity (2017 PPP $/hr) | ILO / Penn World Table | 2022 | Productivity | Static; 5% KNN-imputed |
| 30 | Output per worker (2017 PPP $) | ILO | 2022 | Productivity | Static; 5% KNN-imputed |
| 31 | Global Innovation Index (0–100) | WIPO | 2023 | Productivity | Static; 15% KNN-imputed |
| 32 | Global Competitiveness Index (0–100) | WEF | **2019** | Productivity | **Final edition — discontinued** |
| 33 | Ease of Doing Business score (0–100) | World Bank | **2020** | Productivity | **Final edition — discontinued 2021** |

**Structural features (not in similarity computation):**
- Total population (log-scaled for descriptive overlays)
- Population growth rate
- Median age
- Urban population %
- Age dependency ratio
- Total fertility rate
- Net migration

**Decision rationale for demographics:** Population size is not a welfare indicator — a country of 200M people is not "better" or "worse" than a country of 5M. These features are held out as structural descriptors available for scatter-plot color overlays. Age dependency ratio and fertility rate are neutral structural features; including them in similarity would bias the system toward demographic similarity rather than quality-of-life similarity.

### 1.3 Preprocessing Pipeline

1. **Missingness filter** — Drop indicator if ≥ 30% of countries are missing. Dropped: poverty_rate, gini, literacy_rate (each had exactly 6/20 = 30% missing due to data availability for Cuba, Haiti, and Venezuela).

2. **KNN Imputation** — For remaining gaps (< 30% missing), impute with KNN (k=3) on standardized values. Imputed: fdi_net_inflows (1), inflation (2), edu_expenditure (1), physicians (5), labor_productivity (1), output_per_worker (1), global_innovation_index (3), global_competitiveness_index (3), ease_of_doing_business (1).

3. **Reverse-coding** — Indicators where lower raw = better outcome are multiplied by −1 so that higher z-scores consistently mean "better": inflation, unemployment, infant_mortality, homicide_rate, global_peace_index, press_freedom_index (legacy flag, not active on 2024 data).

4. **Z-score normalization** — Each indicator standardized to mean=0, std=1 across all 20 countries.

### 1.4 Feature Weighting

Default: each of 8 non-demographic categories contributes equally (12.5%). Within a category, weight is split equally among all included indicators in that category.

Final feature matrix: **20 countries × 30 indicators**.

### 1.5 Similarity Computation

Three pairwise metrics computed on the weighted normalized matrix:
- **Cosine similarity** — rescaled from [−1,1] → [0,1]
- **Euclidean similarity** = `1 / (1 + euclidean_distance)`
- **Pearson correlation** — rescaled from [−1,1] → [0,1]

**Composite score** = arithmetic mean of the three, naturally in [0,1].

### 1.6 Embeddings

| Method | Parameters | PC1 variance | PC2 variance | Notes |
|--------|------------|-------------|-------------|-------|
| PCA | n_components=3 | 47.57% | 17.59% | 65.16% cumulative with PC1+PC2; 73.48% with PC3 |
| t-SNE | perplexity=5, max_iter=1000, seed=42 | — | — | KL divergence=0.175 |
| UMAP | n_neighbors=5, min_dist=0.3, seed=42 | — | — | |

---

## 2. Data Quality Notes

| Issue | Affected Indicators | Resolution |
|-------|--------------------|-----------
| Cuba — limited WB data availability | poverty_rate, gini, literacy_rate, global_innovation_index, global_competitiveness_index, labor_productivity, output_per_worker | Some KNN-imputed; core welfare indicators available (HDI, democracy, freedom scores) |
| Haiti — data gaps | global_innovation_index, global_competitiveness_index | KNN-imputed from neighbors |
| Venezuela — limited reporting | ease_of_doing_business, global_competitiveness_index | KNN-imputed |
| WEF GCI discontinued | global_competitiveness_index | Using 2019 (final) edition |
| World Bank Doing Business discontinued | ease_of_doing_business | Using 2020 (final) edition |
| V-Dem LDI year | liberal_democracy_index | 2023 data year |

---

## 3. Country Cluster Narratives

### Cluster 1: High-Development Democracies — "Southern Cone + Costa Rica"
**Countries:** Uruguay, Chile, Costa Rica, Panama (similarity scores 0.84–0.93)

These countries consistently score high across all 9 dimensions. They share:
- HDI > 0.80
- Democracy Index > 7.0 (EIU)
- Freedom House scores ≥ 79/100
- Press freedom among the highest in the region
- Low-to-moderate homicide rates relative to regional average
- Relatively high GDP per capita and labor productivity

**Uruguay–Costa Rica composite similarity: 0.889** — the highest pair in the dataset. Both have stable democratic institutions, strong rule of law, and comparable human development trajectories despite significant population size differences.

**Chile** shares this cluster due to its high GCI score, strong institutions, and economic development, though elevated inequality (historically high Gini, though dropped from the analysis due to missingness) and recent political turbulence moderate some scores.

### Cluster 2: Middle-Income Reformers — "Brazil + Colombia + Mexico + Argentina"
**Similarity: 0.72–0.82**

Large-population, middle-income countries with significant internal inequality but substantive democratic institutions. Brazil and Colombia stand together on productivity indicators; Argentina clusters here despite high inflation drag. These countries share moderate HDI scores (0.75–0.85), varied governance quality, and significant regional power footprints.

### Cluster 3: Central American Transitionals — "Peru + Ecuador + Dominican Republic + Paraguay + Bolivia"
**Similarity: 0.73–0.80**

Smaller-economy countries with moderate development indicators, still-developing infrastructure, and governance challenges. Share characteristics of partially-consolidated democracies and reliance on commodity exports.

### Cluster 4: Northern Triangle — "Honduras, Guatemala, El Salvador"
**Honduras–Guatemala similarity: 0.846 | Honduras–El Salvador similarity: 0.807**

These three countries cluster tightly due to shared characteristics:
- High homicide rates (historically, though El Salvador's fell sharply post-2022)
- Low HDI scores (Guatemala: 0.627, Honduras: 0.624)
- Low Rule of Law scores
- Limited infrastructure access
- Low labor productivity

**Note on El Salvador:** The Bukele administration's securitization strategy dramatically reduced the homicide rate after 2022 (from ~40 to <8 per 100,000), but Freedom House and V-Dem both downgraded El Salvador's democracy scores during this period, keeping it within the Northern Triangle cluster on composite scores.

### Cluster 5: Closed Regimes — "Cuba, Nicaragua, Venezuela"
**Venezuela–Uruguay similarity: 0.401 — the lowest pair in the dataset**

These three countries are outliers in the democracy and governance dimensions:
- Cuba: Democracy Index 2.17, Freedom House 13/100, V-Dem LDI 0.056
- Nicaragua: Democracy Index 2.65, V-Dem LDI 0.050, CPI 18
- Venezuela: Democracy Index 2.25, Freedom House 14/100, Rule of Law 0.22

Despite some positive scores in health infrastructure (Cuba) and formerly high oil-wealth indicators (Venezuela), their democratic and governance deficits place them at the low-similarity extreme relative to high-development democracies.

### Cluster 6: Development Outlier — Haiti
**Haiti–Uruguay similarity: 0.449**

Haiti is a consistent outlier across nearly all dimensions:
- HDI: 0.535 (lowest in the region)
- Infant mortality: 40.9 per 1,000 (highest)
- Homicide rate: 40.9 per 100,000 (highest)
- Global Peace Index: 3.244 (most dangerous in regional ranking)
- Internet access: ~27% of population
- Freedom House: 27/100 (lowest except Cuba, Nicaragua, Venezuela)

Haiti's isolation as an outlier is consistent across PCA, t-SNE, and UMAP embeddings.

---

## 4. Sensitivity Analysis Results

Weight perturbation: ±20% on each category. Countries whose Top-3 nearest neighbors changed:

| Country | Sensitive to |
|---------|-------------|
| Bolivia | governance(+/-20%), democracy(+/-20%) |
| Dominican Republic | productivity(+20%), economy(-20%) |
| Ecuador | social(+20%), health(+20%) |
| Cuba | democracy weight changes most impactful |
| El Salvador | governance(+20%) |

**Stable clusters** (rankings unchanged across all weight perturbations):
- Uruguay–Costa Rica–Chile–Panama: top-3 stable
- Honduras–Guatemala pair: stable
- Haiti: bottom-3 stable in relation to high-development countries
- Venezuela–Nicaragua: mutual nearest-neighbors stable

---

## 5. Limitations

1. **Missing data for authoritarian states.** Cuba, Venezuela, and Nicaragua have limited, potentially unreliable official statistics. Some indicators for these countries were imputed.

2. **Discontinued indices.** WEF GCI (2019) and World Bank Doing Business (2020) are dated. More recent alternatives (WEF Global Competitiveness Report 2024 benchmarks, World Bank B-READY) were still incomplete at time of analysis.

3. **Democracy indicators correlation.** Democracy Index (EIU), Freedom House, V-Dem LDI, and Press Freedom Index are conceptually overlapping. This may over-weight democracy signals relative to other dimensions despite equal category weights.

4. **Poverty and inequality data unavailability.** Poverty headcount and Gini index were both dropped due to 30%+ missingness — a significant data gap that reduces the system's sensitivity to within-country inequality.

5. **Single-year snapshot.** The system uses the most recent available year per indicator (range: 2019–2024). Countries with rapidly changing trajectories (El Salvador's security transformation, Argentina's economic volatility) may be partially captured.

6. **Equal-weights default.** The 8-category equal weighting is a normative choice. Alternative weighting schemes (e.g., HDI-weighted, GDP-weighted) yield meaningfully different rankings, as the sensitivity analysis demonstrates.

7. **Small N.** With only 20 countries, embedding methods (especially t-SNE and UMAP) are working with a very small dataset. Results should be interpreted qualitatively rather than as precise spatial measurements.
