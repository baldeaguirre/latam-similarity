# DESIGN.md — LatAm Quality-of-Life Similarity Dashboard
> Design system for the Latin American Countries Quality-of-Life Similarity Score System.
> Inspired by data-dense dashboards: Sentry, ClickHouse, Linear, Cohere.
> Single source of truth — every token here is mirrored in `config.yaml` under `theme:`.

---

## 1. Visual Theme & Atmosphere

**Mode:** Dark-only. A permanently dark canvas keeps chart contrast high and reduces visual fatigue during prolonged data exploration. No light-mode toggle is offered in v1.

**Philosophy:** Analytically serious, data-rich, calm. Every pixel either carries information or provides necessary breathing room. The aesthetic is closer to a trading terminal or observatory dashboard than a marketing site. Inspired by Sentry's data-dense darkness, ClickHouse's yellow-on-dark technical energy, and Linear's surgical precision.

**Mood keywords:** Slate-indigo night sky · academic rigor · quiet urgency · geographic warmth

**Signature moves:**
- Deep navy-charcoal background (not pure black) prevents eye strain on long sessions.
- A single warm amber accent (`#F59E0B`) echoes Latin American sun motifs without cliché.
- All chart areas sit on a surface one shade lighter than canvas, creating depth without heavy borders.
- Subtle 1 px borders on cards — never shadows as the primary elevation signal on dark themes.

---

## 2. Color Palette & Roles

### Base Palette

| Token                  | Hex       | Role |
|------------------------|-----------|------|
| `--color-canvas`       | `#0D1117` | Page background — deepest layer |
| `--color-surface`      | `#161B22` | Card / panel background |
| `--color-surface-raised` | `#1C2330` | Elevated card, chart area background |
| `--color-border`       | `#30363D` | All card and input borders |
| `--color-border-subtle`| `#21262D` | Dividers, row separators |
| `--color-text-primary` | `#E6EDF3` | Headings, primary labels |
| `--color-text-secondary`| `#8B949E` | Sub-labels, axis ticks, metadata |
| `--color-text-muted`   | `#484F58` | Placeholder text, disabled states |
| `--color-accent`       | `#F59E0B` | Primary CTA, selected state, highlight rings |
| `--color-accent-dim`   | `#78350F` | Accent background fill (badge, chip bg) |
| `--color-accent-hover` | `#FBBF24` | Accent on hover |
| `--color-success`      | `#22C55E` | Positive delta, good score indicators |
| `--color-success-dim`  | `#14532D` | Success background fill |
| `--color-warning`      | `#F59E0B` | Same as accent; context determines semantics |
| `--color-danger`       | `#EF4444` | Error states, negative indicators |
| `--color-danger-dim`   | `#7F1D1D` | Danger background fill |
| `--color-info`         | `#3B82F6` | Informational callouts |
| `--color-info-dim`     | `#1E3A5F` | Info background fill |

### Sequential Scale — Similarity Heatmap & Density Overlays
8-stop perceptually uniform scale from low (cool) to high (warm).
Never use rainbow. This is a single-hue-shifted scale (blue → amber).

| Stop | Hex       | Label |
|------|-----------|-------|
| seq-0 | `#0D1117` | 0.0 (canvas, transparent) |
| seq-1 | `#0F2A4A` | 0.14 |
| seq-2 | `#133E6E` | 0.28 |
| seq-3 | `#1A5C96` | 0.43 |
| seq-4 | `#2E7DB8` | 0.57 |
| seq-5 | `#6FA8CE` | 0.71 |
| seq-6 | `#F5C842` | 0.86 |
| seq-7 | `#F59E0B` | 1.0 (accent) |

Plotly colorscale name: `latam_seq` (defined in `src/visualizations.py`).

### Diverging Scale — Indicator Contribution & Weight-Sensitivity Plots
8-stop anchored at zero (center = canvas color). Negative = red-brown, Positive = teal-green.

| Stop | Hex       | Label |
|------|-----------|-------|
| div-0 | `#7F1D1D` | −1.0 |
| div-1 | `#B91C1C` | −0.71 |
| div-2 | `#DC2626` | −0.43 |
| div-3 | `#FCA5A5` | −0.14 |
| div-mid | `#21262D` | 0.0 (neutral) |
| div-5 | `#6EE7B7` | +0.14 |
| div-6 | `#059669` | +0.43 |
| div-7 | `#065F46` | +0.71 |
| div-8 | `#022C22` | +1.0 |

Plotly colorscale name: `latam_div`.

### Categorical Palette — Country Markers (≥20 colors, colorblind-safe)
Based on the **Okabe-Ito** 8-color palette extended with ColorBrewer Set3 and verified against deuteranopia and protanopia using the WCAG relative luminance method and the Brettel-Viénot-Mollon simulation model.

Deuteranopia/protanopia verification: each pair of adjacent colors was checked to have a simulated ΔE₂₀₀₀ > 10 in the CVD-simulated Lab space using the Coblis simulator convention.

| Index | Country       | ISO2 | Hex       |
|-------|---------------|------|-----------|
| 0  | Argentina        | AR   | `#E69F00` |
| 1  | Bolivia          | BO   | `#56B4E9` |
| 2  | Brazil           | BR   | `#009E73` |
| 3  | Chile            | CL   | `#F0E442` |
| 4  | Colombia         | CO   | `#0072B2` |
| 5  | Costa Rica       | CR   | `#D55E00` |
| 6  | Cuba             | CU   | `#CC79A7` |
| 7  | Dominican Rep.   | DO   | `#7FBC41` |
| 8  | Ecuador          | EC   | `#FDB863` |
| 9  | El Salvador      | SV   | `#AE017E` |
| 10 | Guatemala        | GT   | `#67A9CF` |
| 11 | Haiti            | HT   | `#EF8A62` |
| 12 | Honduras         | HN   | `#998EC3` |
| 13 | Mexico           | MX   | `#01665E` |
| 14 | Nicaragua        | NI   | `#C7E9B4` |
| 15 | Panama           | PA   | `#F1A340` |
| 16 | Paraguay         | PY   | `#762A83` |
| 17 | Peru             | PE   | `#1B7837` |
| 18 | Uruguay          | UY   | `#74ADD1` |
| 19 | Venezuela        | VE   | `#D73027` |

---

## 3. Typography Rules

**Fonts (Google Fonts):**
- **Heading:** `Roboto` (700, 600) — humanist, clean at all sizes; familiar Material Design feel
- **Body / UI:** `Roboto` (400, 500) — same family, unified system
- **Monospace / data:** `JetBrains Mono` (400, 500) — for numbers, codes, tooltips, CSV values

**Import:**
```
https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap
```

**Type Scale:**

| Level       | Size   | Weight | Line-height | Letter-spacing | Usage |
|-------------|--------|--------|-------------|----------------|-------|
| H1          | 24 px  | 700    | 1.2         | -0.02 em       | Dashboard title |
| H2          | 18 px  | 600    | 1.3         | -0.01 em       | Panel / section headers |
| H3          | 14 px  | 600    | 1.4         | 0              | Card titles, chart titles |
| body        | 14 px  | 400    | 1.6         | 0              | Prose, descriptions |
| small       | 12 px  | 400    | 1.5         | 0              | Meta, footnotes |
| caption     | 11 px  | 400    | 1.4         | 0.02 em        | Axis labels, chart captions |
| data-label  | 13 px  | 500    | 1.0         | 0.01 em        | KPI values, score chips — JetBrains Mono |
| tooltip     | 12 px  | 400    | 1.5         | 0              | Hover tooltips — JetBrains Mono for values |

**Rules:**
- No chart text below 12 px.
- Data values (scores, percentages, years) always rendered in `JetBrains Mono`.
- Category labels in sentence case, not ALL CAPS.

---

## 4. Component Stylings

### Buttons

| State    | Background         | Text              | Border |
|----------|--------------------|-------------------|--------|
| Default  | `--color-surface-raised` | `--color-text-primary` | `--color-border` 1 px |
| Hover    | `--color-accent-dim` | `--color-accent-hover` | `--color-accent` 1 px |
| Active   | `--color-accent`   | `#0D1117`          | none |
| Focus    | same as hover      | same              | `--color-accent` 2 px outline offset 2 px |
| Disabled | `--color-surface`  | `--color-text-muted` | `--color-border-subtle` |

Border-radius: `6 px`. Padding: `6 px 14 px`. Font: 13 px / 500.

### Cards / Panels
- Background: `--color-surface`
- Border: 1 px `--color-border`
- Border-radius: `8 px`
- Padding: `20 px`
- No box-shadow (dark theme uses border+surface elevation)

### Inputs & Dropdowns
- Background: `--color-canvas`
- Border: 1 px `--color-border`
- Border-radius: `6 px`
- Text: `--color-text-primary`
- Placeholder: `--color-text-muted`
- Focus ring: `--color-accent` 2 px outline

### Sliders (Weight Adjustment)
- Track: `--color-border` 4 px height
- Fill: `--color-accent`
- Thumb: 14 px circle, `--color-accent`, hover scale 1.15
- Label above: H3 style; value beside thumb: `data-label` style

### Tabs (PCA / t-SNE / UMAP toggle)
- Container background: `--color-surface`
- Inactive tab: text `--color-text-secondary`, no underline
- Active tab: text `--color-accent`, bottom border 2 px `--color-accent`
- Tab height: 36 px, padding 0 16 px

### Tooltips
- Background: `#1C2330` (surface-raised)
- Border: 1 px `--color-border`
- Border-radius: `6 px`
- Padding: `10 px 14 px`
- Arrow: 6 px solid triangle, same background
- Max-width: 280 px

### Country-Selector Dropdown
- Multi-select capable (up to 4 for radar chart)
- Each selected country shown as a pill chip:
  - Background: country's categorical color at 20% opacity
  - Border: 1 px categorical color
  - Text: categorical color (lighter shade)
  - Remove × icon on right
- Dropdown list items show flag emoji + country name

### Weight-Adjustment Slider
- One slider per category (9 total), in a collapsible sidebar section
- Real-time recalculation with 300 ms debounce
- Shows current weight % beside each slider in `data-label` style
- "Reset to equal weights" button at bottom of section

### Chart-Type Toggle (PCA / t-SNE / UMAP)
- 3-button segmented control above the scatter chart
- Selected button: `--color-accent` background, `#0D1117` text
- Unselected: `--color-surface-raised` background

### Similarity-Score Chip
- Pill shape, border-radius 999 px
- Score ≥ 0.80: success-dim bg, success text
- Score 0.60–0.79: accent-dim bg, accent text
- Score < 0.60: surface-raised bg, text-secondary

### Indicator-Category Badge
- Small pill, 10 px font, 4 px 8 px padding
- One badge color per category (use first 9 categorical palette entries)

---

## 5. Layout Principles

**Spacing scale (8 px base):**
`4 px · 8 px · 12 px · 16 px · 24 px · 32 px · 48 px · 64 px · 96 px`

**Grid:** 12-column, 24 px gutters, max content width `1440 px`.

**Dashboard layout:**

```
┌─────────────────────────────────────────────────────────┐
│ HEADER (64 px tall, sticky)                             │
│  Logo · Title · Last-updated chip · GitHub link         │
├──────────────┬──────────────────────────────────────────┤
│ LEFT PANEL   │ PRIMARY CHART AREA                       │
│ (300 px)     │ (flex-grow, min 600 px)                  │
│              │                                          │
│ • Country    │  [Heatmap | Scatter | Dendrogram tabs]   │
│   selector   │                                          │
│ • Category   │  Chart renders here                      │
│   weight     │  (min-height 480 px)                     │
│   sliders    │                                          │
│ • Embed      ├──────────────────────────────────────────┤
│   method     │ SECONDARY PANELS (2-col grid, 50/50)     │
│   toggle     │  [Radar chart] │ [Top-N similarity]      │
│              │                │                          │
│              ├────────────────┴─────────────────────────┤
│              │ PAIRWISE CONTRIBUTION (full width)        │
└──────────────┴──────────────────────────────────────────┘
```

**Panel padding:** `20 px` interior, `16 px` gap between panels.
**Whitespace philosophy:** Charts fill available space. Text panels have max-width `680 px` for readable line lengths. Every chart has a clearly labeled header and 12 px padding around the plot area.

---

## 6. Depth & Elevation

| Layer          | Surface Token              | Border              | Shadow |
|----------------|----------------------------|---------------------|--------|
| Canvas         | `--color-canvas` `#0D1117` | none                | none   |
| Card / Panel   | `--color-surface` `#161B22` | 1 px `--color-border` | none  |
| Chart area     | `--color-surface-raised` `#1C2330` | 1 px `--color-border-subtle` | none |
| Modal overlay  | `--color-surface` + 95% opacity | 1 px `--color-border` | `0 24px 64px rgba(0,0,0,0.6)` |
| Popover/Tooltip| `#1C2330`                  | 1 px `--color-border` | `0 8px 24px rgba(0,0,0,0.4)` |

On dark themes, elevation is communicated via **background lightness stepping**, not shadows. Shadows are reserved only for floating elements (modals, tooltips) that must appear above all content.

---

## 7. Do's and Don'ts

### ✅ Do's
- Use `--color-accent` (`#F59E0B`) for exactly one primary action per panel.
- Label every chart axis, even if the label seems obvious.
- Keep chart text ≥ 12 px at all zoom levels.
- Use the sequential scale for any heatmap showing magnitude.
- Use the diverging scale for any chart showing deviation from a neutral center.
- Use the categorical palette for country markers — assign by ISO2 order, never by rank.
- Round similarity scores to 3 decimal places in tooltips.
- Provide a fallback text table for every chart (accessible alternative).
- Use `JetBrains Mono` for all numeric data displays.
- Include a data source + year footnote on every chart.

### ❌ Don'ts
- **Never use a rainbow (HSV) colorscale** for sequential heatmaps — it misleads magnitude perception.
- **Never use red/green for country comparison** — reserved for diverging (negative/positive) and status only.
- **Don't encode > 1 visual variable** for the same data dimension (e.g., don't vary both size and color to show similarity).
- **No chartjunk** — no decorative gridlines, 3D bars, or gradient fills on bar charts.
- **Don't label** every individual data point on dense scatter plots — use hover-only for country codes, with permanent labels only for the top/bottom 3 outliers.
- **Don't truncate axis labels** — rotate to 45° or use short codes instead.
- **Never use opacity < 40%** for text, even for secondary labels.
- **Don't mix font families** outside the defined stack.

---

## 8. Responsive Behavior

| Breakpoint | Width      | Strategy |
|------------|------------|----------|
| Mobile     | < 640 px   | Single column; charts collapsed to top-N text lists; sliders in bottom sheet |
| Tablet     | 640–1023 px| Left panel becomes a top drawer (toggle button); primary chart full width; secondary panels stack vertically |
| Desktop    | 1024–1439 px| Full 3-column layout as designed |
| Wide       | ≥ 1440 px  | Max-width cap at 1440 px, centered |

**Touch targets:** Minimum 44 × 44 px for all interactive elements (sliders, tabs, buttons).

**Heatmap below 768 px:**
- Fall back to a sorted top-N similarity list (text-based), with similarity chips.
- Show a "View full heatmap" button that opens a horizontally-scrollable container.

**Scatter plot below 768 px:**
- Render at 100% viewport width, 300 px tall.
- Disable 3D PCA view on mobile (performance).
- Marker labels hidden by default; tap to reveal tooltip.

**Dendrogram below 1024 px:**
- Rotate to horizontal orientation (countries on Y-axis).
- If still overflows, show as a collapsible indented list of clusters.

---

## 9. Agent Prompt Guide

### Quick-Reference Token Table

| Purpose                    | Token / Value |
|----------------------------|---------------|
| Page background            | `#0D1117` |
| Card background            | `#161B22` |
| Chart plot area            | `#1C2330` |
| Primary text               | `#E6EDF3` |
| Secondary text             | `#8B949E` |
| Accent / selected          | `#F59E0B` |
| Border                     | `#30363D` |
| Success                    | `#22C55E` |
| Danger                     | `#EF4444` |
| Heading font               | `Inter 700` |
| Body font                  | `Inter 400` |
| Data / mono font           | `JetBrains Mono 400` |
| Border radius (card)       | `8 px` |
| Border radius (button/input)| `6 px` |
| Base spacing unit          | `8 px` |

### Ready-to-Paste Prompts for Future Agents

**Add a new chart panel:**
> "Add a new chart panel matching the existing card style. Use background `#161B22`, border `1px solid #30363D`, border-radius `8px`, padding `20px`. The chart plot area should use `#1C2330` as its background. Title in Inter 600 14px `#E6EDF3`. Axis labels 11px `#8B949E`. Accent color for highlighted series: `#F59E0B`."

**Add a new KPI metric chip:**
> "Add a similarity score chip: pill shape border-radius 999px, background `#78350F`, text `#FBBF24`, font `JetBrains Mono 500 13px`. For scores above 0.8, use background `#14532D` and text `#22C55E`."

**Add a country dropdown:**
> "Add a country multi-select. Input background `#0D1117`, border `1px solid #30363D`, border-radius `6px`, text `#E6EDF3`. Selected countries shown as pills with the categorical color at 20% opacity background and full categorical color border and text. Max 4 selections. Use the ISO2-ordered categorical palette from DESIGN.md."

**Style a data table:**
> "Data table: header row background `#1C2330`, header text Inter 600 12px `#8B949E` uppercase. Data rows alternate between `#161B22` and `#0D1117`. Row hover: `#1C2330`. Numeric cells right-aligned, JetBrains Mono 13px `#E6EDF3`. All borders `1px solid #21262D`."

---

## 10. Plotly / Streamlit Theming (Project-Specific Addendum)

### Plotly Layout Template (Python dict)

```python
LATAM_PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "#161B22",
        "plot_bgcolor": "#1C2330",
        "font": {
            "family": "Inter, system-ui, sans-serif",
            "color": "#E6EDF3",
            "size": 13,
        },
        "title": {
            "font": {"size": 14, "color": "#E6EDF3", "family": "Inter"},
            "x": 0,
            "xanchor": "left",
            "pad": {"l": 4},
        },
        "xaxis": {
            "gridcolor": "#21262D",
            "linecolor": "#30363D",
            "tickcolor": "#30363D",
            "tickfont": {"size": 11, "color": "#8B949E", "family": "JetBrains Mono"},
            "title": {"font": {"size": 12, "color": "#8B949E"}},
            "zerolinecolor": "#30363D",
        },
        "yaxis": {
            "gridcolor": "#21262D",
            "linecolor": "#30363D",
            "tickcolor": "#30363D",
            "tickfont": {"size": 11, "color": "#8B949E", "family": "JetBrains Mono"},
            "title": {"font": {"size": 12, "color": "#8B949E"}},
            "zerolinecolor": "#30363D",
        },
        "legend": {
            "bgcolor": "#161B22",
            "bordercolor": "#30363D",
            "borderwidth": 1,
            "font": {"size": 12, "color": "#E6EDF3"},
        },
        "colorway": [
            "#E69F00","#56B4E9","#009E73","#F0E442","#0072B2",
            "#D55E00","#CC79A7","#7FBC41","#FDB863","#AE017E",
            "#67A9CF","#EF8A62","#998EC3","#01665E","#C7E9B4",
            "#F1A340","#762A83","#1B7837","#74ADD1","#D73027",
        ],
        "hoverlabel": {
            "bgcolor": "#1C2330",
            "bordercolor": "#30363D",
            "font": {"size": 12, "color": "#E6EDF3", "family": "JetBrains Mono"},
        },
        "margin": {"l": 60, "r": 20, "t": 50, "b": 60},
    }
}

LATAM_SEQ_COLORSCALE = [
    [0.00, "#0D1117"], [0.14, "#0F2A4A"], [0.28, "#133E6E"],
    [0.43, "#1A5C96"], [0.57, "#2E7DB8"], [0.71, "#6FA8CE"],
    [0.86, "#F5C842"], [1.00, "#F59E0B"],
]

LATAM_DIV_COLORSCALE = [
    [0.00, "#7F1D1D"], [0.125, "#B91C1C"], [0.25, "#DC2626"],
    [0.375, "#FCA5A5"], [0.50, "#21262D"], [0.625, "#6EE7B7"],
    [0.75, "#059669"], [0.875, "#065F46"], [1.00, "#022C22"],
]
```

### Streamlit `config.toml` Theme Block

```toml
[theme]
base = "dark"
primaryColor = "#F59E0B"
backgroundColor = "#0D1117"
secondaryBackgroundColor = "#161B22"
textColor = "#E6EDF3"
font = "sans serif"
```

Place this file at `.streamlit/config.toml` in the project root.

### Token Propagation Contract

Every token defined in this file MUST appear in `config.yaml` under the `theme:` key using the same names (snake_case). Example:

```yaml
theme:
  color_canvas: "#0D1117"
  color_surface: "#161B22"
  color_surface_raised: "#1C2330"
  color_border: "#30363D"
  color_border_subtle: "#21262D"
  color_text_primary: "#E6EDF3"
  color_text_secondary: "#8B949E"
  color_text_muted: "#484F58"
  color_accent: "#F59E0B"
  color_accent_dim: "#78350F"
  color_accent_hover: "#FBBF24"
  color_success: "#22C55E"
  color_success_dim: "#14532D"
  color_danger: "#EF4444"
  color_danger_dim: "#7F1D1D"
  color_info: "#3B82F6"
  color_info_dim: "#1E3A5F"
  font_heading: "Inter"
  font_body: "Inter"
  font_mono: "JetBrains Mono"
```

Any agent modifying colors must update DESIGN.md **and** `config.yaml` together. The Plotly template in `src/visualizations.py` reads from `config.yaml` at runtime — no hardcoded hex values in Python files.
