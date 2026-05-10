"""
src/data_collection.py
======================
Downloads all indicators from their respective sources and caches
raw data under data/raw/. All I/O is isolated here.

Run standalone:  python -m src.data_collection
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

import pandas as pd
import requests
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).parent.parent
_CFG_PATH = _ROOT / "config.yaml"

with open(_CFG_PATH) as f:
    CFG = yaml.safe_load(f)

RAW_DIR = _ROOT / CFG["paths"]["raw_data"]
RAW_DIR.mkdir(parents=True, exist_ok=True)

COUNTRIES = CFG["countries"]
COUNTRY_NAMES = [c["name"] for c in COUNTRIES]
WB_CODES = {c["name"]: c["wb_code"] for c in COUNTRIES}
ISO2_MAP = {c["name"]: c["iso2"] for c in COUNTRIES}

# ---------------------------------------------------------------------------
# World Bank helpers
# ---------------------------------------------------------------------------
WB_BASE = "https://api.worldbank.org/v2/country/{codes}/indicator/{indicator}"
WB_PARAMS = "?format=json&mrv=5&per_page=500"


def _wb_codes_str() -> str:
    return ";".join(c["wb_code"] for c in COUNTRIES)


def fetch_world_bank(wb_indicator: str, year_hint: int) -> pd.Series:
    """Return a Series (index=country name) for the most recent value ≤ year_hint."""
    cache_file = RAW_DIR / f"wb_{wb_indicator.replace('.', '_')}.json"
    if cache_file.exists():
        log.info("WB cache hit: %s", wb_indicator)
        raw = json.loads(cache_file.read_text())
    else:
        url = WB_BASE.format(codes=_wb_codes_str(), indicator=wb_indicator) + WB_PARAMS
        log.info("WB download: %s", url)
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        raw = resp.json()
        cache_file.write_text(json.dumps(raw, ensure_ascii=False, indent=2))
        time.sleep(0.3)  # be polite

    # Parse response: raw[1] is list of records
    if len(raw) < 2 or not raw[1]:
        log.warning("No data returned for %s", wb_indicator)
        return pd.Series(dtype=float, name=wb_indicator)

    records = raw[1]
    # Build {country_name: value} using most recent non-null ≤ year_hint
    iso3_to_name = {c["iso3"]: c["name"] for c in COUNTRIES}
    data: dict[str, float] = {}
    seen: dict[str, int] = {}  # country -> best year so far

    for rec in records:
        iso3 = rec.get("countryiso3code", "")
        if iso3 not in iso3_to_name:
            continue
        country = iso3_to_name[iso3]
        try:
            yr = int(rec["date"])
        except (ValueError, TypeError):
            continue
        if yr > year_hint:
            continue
        value = rec.get("value")
        if value is None:
            continue
        if country not in seen or yr > seen[country]:
            data[country] = float(value)
            seen[country] = yr

    series = pd.Series(data, name=wb_indicator, dtype=float)
    # Reindex to canonical country order
    series = series.reindex(COUNTRY_NAMES)
    return series


# ---------------------------------------------------------------------------
# Manual / CSV data (indices without an API)
# These are embedded as dicts with the most recent reliable year's values.
# Sources are cited in report.md and config.yaml.
# ---------------------------------------------------------------------------

def _load_hdi() -> pd.Series:
    """UNDP Human Development Report 2023/2024 (data year 2022)."""
    cache = RAW_DIR / "hdi_2022.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["hdi"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 0.849, "Bolivia": 0.698, "Brazil": 0.760,
        "Chile": 0.860, "Colombia": 0.752, "Costa Rica": 0.806,
        "Cuba": 0.764, "Dominican Republic": 0.767, "Ecuador": 0.765,
        "El Salvador": 0.675, "Guatemala": 0.627, "Haiti": 0.535,
        "Honduras": 0.624, "Mexico": 0.781, "Nicaragua": 0.667,
        "Panama": 0.819, "Paraguay": 0.717, "Peru": 0.762,
        "Uruguay": 0.830, "Venezuela": 0.699,
    }
    s = pd.Series(data, name="hdi").reindex(COUNTRY_NAMES)
    pd.DataFrame({"hdi": s}).to_csv(cache)
    return s


def _load_mean_years_schooling() -> pd.Series:
    """UNDP HDR 2023 Statistical Annex, mean years of schooling 2022."""
    cache = RAW_DIR / "mean_years_schooling_2022.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["mean_years_schooling"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 11.3, "Bolivia": 9.8, "Brazil": 8.0,
        "Chile": 10.6, "Colombia": 8.9, "Costa Rica": 9.0,
        "Cuba": 12.0, "Dominican Republic": 8.2, "Ecuador": 9.6,
        "El Salvador": 7.2, "Guatemala": 6.5, "Haiti": 5.6,
        "Honduras": 6.6, "Mexico": 9.0, "Nicaragua": 7.2,
        "Panama": 10.2, "Paraguay": 8.8, "Peru": 10.0,
        "Uruguay": 9.3, "Venezuela": 10.3,
    }
    s = pd.Series(data, name="mean_years_schooling").reindex(COUNTRY_NAMES)
    pd.DataFrame({"mean_years_schooling": s}).to_csv(cache)
    return s


def _load_cpi() -> pd.Series:
    """Transparency International CPI 2023 (scale 0-100, higher=less corrupt)."""
    cache = RAW_DIR / "cpi_2023.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["cpi"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 37, "Bolivia": 31, "Brazil": 36,
        "Chile": 66, "Colombia": 39, "Costa Rica": 54,
        "Cuba": 44, "Dominican Republic": 30, "Ecuador": 36,
        "El Salvador": 31, "Guatemala": 24, "Haiti": 17,
        "Honduras": 23, "Mexico": 31, "Nicaragua": 18,
        "Panama": 34, "Paraguay": 26, "Peru": 38,
        "Uruguay": 73, "Venezuela": 13,
    }
    s = pd.Series(data, name="cpi", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"cpi": s}).to_csv(cache)
    return s


def _load_homicide_rate() -> pd.Series:
    """UNODC Global Study on Homicide, homicides per 100,000 (2022 or latest)."""
    cache = RAW_DIR / "homicide_rate_2022.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["homicide_rate"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 5.5, "Bolivia": 3.9, "Brazil": 23.3,
        "Chile": 4.6, "Colombia": 25.3, "Costa Rica": 12.1,
        "Cuba": 4.7, "Dominican Republic": 12.4, "Ecuador": 25.9,
        "El Salvador": 7.8, "Guatemala": 17.3, "Haiti": 40.9,
        "Honduras": 35.8, "Mexico": 28.2, "Nicaragua": 7.2,
        "Panama": 14.4, "Paraguay": 17.6, "Peru": 8.3,
        "Uruguay": 11.4, "Venezuela": 40.3,
    }
    s = pd.Series(data, name="homicide_rate", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"homicide_rate": s}).to_csv(cache)
    return s


def _load_global_peace_index() -> pd.Series:
    """IEP Global Peace Index 2023 (lower score = more peaceful; reversed in preprocessing)."""
    cache = RAW_DIR / "gpi_2023.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["global_peace_index"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 1.744, "Bolivia": 1.992, "Brazil": 2.034,
        "Chile": 1.782, "Colombia": 2.566, "Costa Rica": 1.615,
        "Cuba": 1.833, "Dominican Republic": 2.023, "Ecuador": 2.312,
        "El Salvador": 2.122, "Guatemala": 2.377, "Haiti": 3.244,
        "Honduras": 2.463, "Mexico": 2.626, "Nicaragua": 2.205,
        "Panama": 1.807, "Paraguay": 2.052, "Peru": 2.200,
        "Uruguay": 1.557, "Venezuela": 2.924,
    }
    s = pd.Series(data, name="global_peace_index", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"global_peace_index": s}).to_csv(cache)
    return s


def _load_rule_of_law() -> pd.Series:
    """World Justice Project Rule of Law Index 2023 (0-1, higher=better)."""
    cache = RAW_DIR / "rol_2023.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["rule_of_law"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 0.47, "Bolivia": 0.38, "Brazil": 0.49,
        "Chile": 0.63, "Colombia": 0.45, "Costa Rica": 0.62,
        "Cuba": 0.36, "Dominican Republic": 0.42, "Ecuador": 0.44,
        "El Salvador": 0.41, "Guatemala": 0.38, "Haiti": 0.25,
        "Honduras": 0.36, "Mexico": 0.42, "Nicaragua": 0.28,
        "Panama": 0.49, "Paraguay": 0.40, "Peru": 0.45,
        "Uruguay": 0.67, "Venezuela": 0.22,
    }
    s = pd.Series(data, name="rule_of_law", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"rule_of_law": s}).to_csv(cache)
    return s


def _load_logistics_performance() -> pd.Series:
    """World Bank Logistics Performance Index 2023 (1-5 scale)."""
    cache = RAW_DIR / "lpi_2023.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["logistics_performance"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 2.90, "Bolivia": 2.43, "Brazil": 3.21,
        "Chile": 3.32, "Colombia": 2.87, "Costa Rica": 2.83,
        "Cuba": 2.50, "Dominican Republic": 2.61, "Ecuador": 2.72,
        "El Salvador": 2.59, "Guatemala": 2.68, "Haiti": 2.16,
        "Honduras": 2.41, "Mexico": 3.02, "Nicaragua": 2.48,
        "Panama": 3.30, "Paraguay": 2.75, "Peru": 2.76,
        "Uruguay": 2.87, "Venezuela": 2.18,
    }
    s = pd.Series(data, name="logistics_performance", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"logistics_performance": s}).to_csv(cache)
    return s


def _load_democracy_index() -> pd.Series:
    """EIU Democracy Index 2023 overall score (0-10)."""
    cache = RAW_DIR / "democracy_index_2023.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["democracy_index"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 6.73, "Bolivia": 5.36, "Brazil": 6.97,
        "Chile": 7.93, "Colombia": 6.72, "Costa Rica": 8.16,
        "Cuba": 2.17, "Dominican Republic": 5.73, "Ecuador": 5.52,
        "El Salvador": 5.09, "Guatemala": 4.29, "Haiti": 1.55,
        "Honduras": 4.21, "Mexico": 5.66, "Nicaragua": 2.65,
        "Panama": 6.87, "Paraguay": 5.93, "Peru": 5.99,
        "Uruguay": 8.77, "Venezuela": 2.25,
    }
    s = pd.Series(data, name="democracy_index", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"democracy_index": s}).to_csv(cache)
    return s


def _load_freedom_house() -> pd.Series:
    """Freedom House Freedom in the World 2024: aggregate score (0-100)."""
    cache = RAW_DIR / "freedom_house_2024.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["freedom_house"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 84, "Bolivia": 65, "Brazil": 80,
        "Chile": 94, "Colombia": 66, "Costa Rica": 91,
        "Cuba": 13, "Dominican Republic": 68, "Ecuador": 64,
        "El Salvador": 47, "Guatemala": 50, "Haiti": 27,
        "Honduras": 43, "Mexico": 60, "Nicaragua": 9,
        "Panama": 79, "Paraguay": 63, "Peru": 70,
        "Uruguay": 97, "Venezuela": 14,
    }
    s = pd.Series(data, name="freedom_house", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"freedom_house": s}).to_csv(cache)
    return s


def _load_liberal_democracy_index() -> pd.Series:
    """V-Dem Liberal Democracy Index 2023 (0-1)."""
    cache = RAW_DIR / "vdem_ldi_2023.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["liberal_democracy_index"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 0.418, "Bolivia": 0.257, "Brazil": 0.426,
        "Chile": 0.643, "Colombia": 0.318, "Costa Rica": 0.658,
        "Cuba": 0.056, "Dominican Republic": 0.287, "Ecuador": 0.303,
        "El Salvador": 0.157, "Guatemala": 0.198, "Haiti": 0.089,
        "Honduras": 0.117, "Mexico": 0.339, "Nicaragua": 0.050,
        "Panama": 0.462, "Paraguay": 0.307, "Peru": 0.295,
        "Uruguay": 0.790, "Venezuela": 0.034,
    }
    s = pd.Series(data, name="liberal_democracy_index", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"liberal_democracy_index": s}).to_csv(cache)
    return s


def _load_press_freedom_index() -> pd.Series:
    """RSF World Press Freedom Index 2024 (0-100, higher=more free; reverse_code=true means lower raw score = more free under RSF convention — verify)."""
    cache = RAW_DIR / "press_freedom_2024.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["press_freedom_index"].reindex(COUNTRY_NAMES)

    # RSF 2024 Global Score (0-100 scale since 2022 methodology, higher = better)
    data = {
        "Argentina": 66.88, "Bolivia": 62.98, "Brazil": 65.58,
        "Chile": 72.73, "Colombia": 54.41, "Costa Rica": 77.48,
        "Cuba": 20.90, "Dominican Republic": 53.35, "Ecuador": 54.21,
        "El Salvador": 53.39, "Guatemala": 51.56, "Haiti": 33.73,
        "Honduras": 43.71, "Mexico": 51.74, "Nicaragua": 20.31,
        "Panama": 61.33, "Paraguay": 61.06, "Peru": 56.01,
        "Uruguay": 77.40, "Venezuela": 24.95,
    }
    # Note: RSF switched to 0-100 "good score" convention in 2022.
    # reverse_code=true in config was for the old convention; actual 2024 data is higher=better.
    # We store raw values here; preprocessing reads config to decide reversal.
    s = pd.Series(data, name="press_freedom_index", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"press_freedom_index": s}).to_csv(cache)
    return s


def _load_labor_productivity() -> pd.Series:
    """ILO ILOSTAT labor productivity: GDP per hour worked (2017 PPP $), 2022."""
    cache = RAW_DIR / "labor_productivity_2022.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["labor_productivity"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 20.1, "Bolivia": 7.8, "Brazil": 16.4,
        "Chile": 24.3, "Colombia": 12.9, "Costa Rica": 22.8,
        "Cuba": None, "Dominican Republic": 14.2, "Ecuador": 10.5,
        "El Salvador": 8.9, "Guatemala": 9.6, "Haiti": 2.3,
        "Honduras": 6.8, "Mexico": 20.2, "Nicaragua": 7.1,
        "Panama": 22.0, "Paraguay": 12.4, "Peru": 11.5,
        "Uruguay": 25.9, "Venezuela": 5.0,
    }
    s = pd.Series(data, name="labor_productivity", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"labor_productivity": s}).to_csv(cache)
    return s


def _load_output_per_worker() -> pd.Series:
    """ILO output per worker (GDP per employed person, 2017 PPP $), 2022."""
    cache = RAW_DIR / "output_per_worker_2022.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["output_per_worker"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 32400, "Bolivia": 13100, "Brazil": 28000,
        "Chile": 40900, "Colombia": 21400, "Costa Rica": 37200,
        "Cuba": None, "Dominican Republic": 23700, "Ecuador": 17100,
        "El Salvador": 14600, "Guatemala": 16000, "Haiti": 3500,
        "Honduras": 11000, "Mexico": 33700, "Nicaragua": 11600,
        "Panama": 39000, "Paraguay": 21600, "Peru": 20000,
        "Uruguay": 44300, "Venezuela": 8100,
    }
    s = pd.Series(data, name="output_per_worker", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"output_per_worker": s}).to_csv(cache)
    return s


def _load_global_innovation_index() -> pd.Series:
    """WIPO Global Innovation Index 2023 (0-100)."""
    cache = RAW_DIR / "gii_2023.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["global_innovation_index"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 34.0, "Bolivia": 22.8, "Brazil": 38.3,
        "Chile": 37.3, "Colombia": 32.8, "Costa Rica": 36.0,
        "Cuba": None, "Dominican Republic": 27.3, "Ecuador": 24.7,
        "El Salvador": 24.8, "Guatemala": 25.6, "Haiti": None,
        "Honduras": 22.0, "Mexico": 35.5, "Nicaragua": 21.0,
        "Panama": 31.0, "Paraguay": 26.3, "Peru": 29.5,
        "Uruguay": 34.3, "Venezuela": None,
    }
    s = pd.Series(data, name="global_innovation_index", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"global_innovation_index": s}).to_csv(cache)
    return s


def _load_global_competitiveness_index() -> pd.Series:
    """WEF Global Competitiveness Index 2019 (0-100). Final edition."""
    cache = RAW_DIR / "gci_2019.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["global_competitiveness_index"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 57.2, "Bolivia": 48.1, "Brazil": 60.9,
        "Chile": 70.5, "Colombia": 62.7, "Costa Rica": 62.9,
        "Cuba": None, "Dominican Republic": 58.3, "Ecuador": 55.7,
        "El Salvador": 56.8, "Guatemala": 55.6, "Haiti": None,
        "Honduras": 52.5, "Mexico": 64.9, "Nicaragua": 50.5,
        "Panama": 67.6, "Paraguay": 55.7, "Peru": 61.7,
        "Uruguay": 62.7, "Venezuela": None,
    }
    s = pd.Series(data, name="global_competitiveness_index", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"global_competitiveness_index": s}).to_csv(cache)
    return s


def _load_ease_of_doing_business() -> pd.Series:
    """World Bank Ease of Doing Business 2020 (0-100). Final edition (discontinued 2021)."""
    cache = RAW_DIR / "eodb_2020.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["ease_of_doing_business"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 59.0, "Bolivia": 51.4, "Brazil": 59.1,
        "Chile": 72.6, "Colombia": 70.0, "Costa Rica": 69.2,
        "Cuba": None, "Dominican Republic": 60.0, "Ecuador": 60.0,
        "El Salvador": 65.0, "Guatemala": 62.7, "Haiti": 40.0,
        "Honduras": 61.1, "Mexico": 72.4, "Nicaragua": 58.0,
        "Panama": 67.6, "Paraguay": 59.3, "Peru": 68.7,
        "Uruguay": 61.5, "Venezuela": 30.2,
    }
    s = pd.Series(data, name="ease_of_doing_business", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"ease_of_doing_business": s}).to_csv(cache)
    return s


def _load_median_age() -> pd.Series:
    """UN World Population Prospects 2024 median age (years), 2023."""
    cache = RAW_DIR / "median_age_2023.csv"
    if cache.exists():
        df = pd.read_csv(cache, index_col=0)
        return df["median_age"].reindex(COUNTRY_NAMES)

    data = {
        "Argentina": 32.0, "Bolivia": 25.5, "Brazil": 34.7,
        "Chile": 36.0, "Colombia": 32.2, "Costa Rica": 34.3,
        "Cuba": 43.0, "Dominican Republic": 29.3, "Ecuador": 28.8,
        "El Salvador": 28.1, "Guatemala": 23.4, "Haiti": 24.0,
        "Honduras": 24.5, "Mexico": 29.3, "Nicaragua": 26.8,
        "Panama": 30.4, "Paraguay": 26.0, "Peru": 29.6,
        "Uruguay": 35.8, "Venezuela": 29.2,
    }
    s = pd.Series(data, name="median_age", dtype=float).reindex(COUNTRY_NAMES)
    pd.DataFrame({"median_age": s}).to_csv(cache)
    return s


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def collect_all() -> pd.DataFrame:
    """Download / load all indicators. Returns wide DataFrame (countries × indicators)."""
    log.info("Starting data collection for %d countries", len(COUNTRIES))
    frames: dict[str, pd.Series] = {}

    # --- World Bank API indicators ---
    wb_indicators = [
        ind for ind in CFG["indicators"]
        if ind.get("wb_indicator") and not ind.get("structural", False)
    ]
    # Also fetch structural WB indicators for overlay use
    wb_structural = [
        ind for ind in CFG["indicators"]
        if ind.get("wb_indicator") and ind.get("structural", False)
    ]

    for ind in wb_indicators + wb_structural:
        wb_code = ind["wb_indicator"]
        year = ind.get("year_used", 2022)
        try:
            s = fetch_world_bank(wb_code, year)
            s.name = ind["id"]
            frames[ind["id"]] = s
        except Exception as e:
            log.error("Failed to fetch WB %s: %s", wb_code, e)

    # --- Manual / static data ---
    manual_loaders = {
        "hdi": _load_hdi,
        "mean_years_schooling": _load_mean_years_schooling,
        "cpi": _load_cpi,
        "homicide_rate": _load_homicide_rate,
        "global_peace_index": _load_global_peace_index,
        "rule_of_law": _load_rule_of_law,
        "logistics_performance": _load_logistics_performance,
        "democracy_index": _load_democracy_index,
        "freedom_house": _load_freedom_house,
        "liberal_democracy_index": _load_liberal_democracy_index,
        "press_freedom_index": _load_press_freedom_index,
        "labor_productivity": _load_labor_productivity,
        "output_per_worker": _load_output_per_worker,
        "global_innovation_index": _load_global_innovation_index,
        "global_competitiveness_index": _load_global_competitiveness_index,
        "ease_of_doing_business": _load_ease_of_doing_business,
        "median_age": _load_median_age,
    }
    for ind_id, loader in manual_loaders.items():
        try:
            s = loader()
            s.name = ind_id
            frames[ind_id] = s
        except Exception as e:
            log.error("Failed to load %s: %s", ind_id, e)

    df = pd.DataFrame(frames, index=COUNTRY_NAMES)
    log.info("Collected %d indicators for %d countries", len(df.columns), len(df))
    return df


if __name__ == "__main__":
    df = collect_all()
    out = RAW_DIR / "all_indicators_raw.csv"
    df.to_csv(out)
    log.info("Saved raw data to %s", out)
    print(df.to_string())
