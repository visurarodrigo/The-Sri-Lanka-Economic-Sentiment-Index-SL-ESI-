# Sri Lanka Economic Sentiment Index (SL-ESI) — Project Design
**Status:** Phases 1–4 complete. Phases 5–7 remaining.
**Scope note:** Extended from original 2022–2026 plan to **2020–2026** to capture the full arc: pre-crisis → COVID shock → 2022 collapse → IMF bailout → recovery. This is what makes it flagship-level — a longer, more defensible narrative window.

---

### **Phase 1: Data Sourcing & Collection** ✅ Done
**Goal:** Time-stamped dataset of Sri Lankan English news headlines (2020–2026), economy/business focus.
**What happened:**
- Sourced from **EconomyNext** (Economy + Business sections), paginated scrape with retry/backoff logic.
- Extracted title, date, URL, snippet; deduplicated by URL.
**Files:**
- `src/01_collect_data.py`
- `data/raw/news_headlines_raw.csv`

### **Phase 2: Data Cleaning & Preprocessing** ✅ Done
**Goal:** Clean, analysis-ready text.
**What happened:**
- Dropped rows with missing title/date/url, standardized dates to `YYYY-MM-DD`.
- Built unified `text` field (title + snippet), lowercased, stripped noise.
- Added `year`, `month`, `year_month` helper columns.
**Files:**
- `src/02_clean_data.py`
- `data/processed/news_headlines_clean.csv`

### **Phase 3: NLP Sentiment Scoring & Index Aggregation** ✅ Done
**Goal:** Quantify sentiment monthly.
**What happened:**
- Scored every article with **FinBERT** (`ProsusAI/finbert`), continuous -1 to +1 scale.
- Aggregated to monthly: `article_count`, `mean_sentiment`, `std_sentiment` (consensus vs. polarization).
- Added **`sentiment_intensity`** = `mean_sentiment * log1p(article_count)` — this is the volume-weighting the original plan called for, done via a log-dampened multiplier so crisis-peak months (huge coverage) register a stronger signal without letting raw volume dominate.
**Files:**
- `src/03_nlp_scoring.py`
- `data/processed/sl_esi_monthly_index.csv`

### **Phase 4: Economic Data Integration** ✅ Done
**Goal:** Merge sentiment with macro indicators.
**What happened:** *(split into four scripts instead of one, for reliability/fallback handling per source)*
- Tourism arrivals processed to monthly (`04_process_tourism_data.py`)
- USD/LKR exchange rate via FRED `DEXSLUS`, resampled to monthly mean (`05_fetch_exchange_rate.py`)
- Inflation rate scraped from CBSL, with a manual 2023 backfill + FRED fallback + placeholder fallback (`06_fetch_inflation_rate.py`)
- All four datasets merged on `year_month` (`07_merge_economic_data.py`)
**Files:**
- `src/04_process_tourism_data.py`, `05_fetch_exchange_rate.py`, `06_fetch_inflation_rate.py`, `07_merge_economic_data.py`
- `data/processed/sl_esi_merged_economic.csv` ← master dataset

---

### **Phase 5: Event Annotation Layer** 🔜 Next
**Goal:** Turn the merged dataset into a story, not just a chart — this is what separates flagship from generic.
**What happens:**
- Build a small `data/reference/key_events.csv` (or `.py` dict) of major dates: Easter Attacks (Apr 2019), COVID lockdowns (Mar 2020), 2022 crisis peak (fuel/forex shortage, Aug 2022 default), IMF deal (Mar 2023), 2024 presidential election, 2024 parliamentary election.
- Each event gets: `date`, `label`, `category` (political/economic/external-shock), `short_description`.
- This file is what powers the vertical annotation markers in the dashboard (Phase 6) — build it now so Phase 6 is just plotting.
**Files:**
- `src/08_build_event_annotations.py`
- `data/reference/key_events.csv`

### **Phase 6: Time Series Forecasting**
**Goal:** Forecast future sentiment.
**What happens:**
- Fit **SARIMA** and **Prophet** on `sentiment_intensity` (your tourism project already validated SARIMA's strength on Sri Lankan macro series — reuse that comparison methodology here for consistency across your portfolio).
- Report both models' forecasts with confidence intervals; pick the better model based on MAE/RMSE/SMAPE as primary, keep both for the dashboard toggle.
- Backtest on held-out recent months, not just in-sample fit.
**Files:**
- `src/09_forecast.py`
- `data/processed/sl_esi_forecast_results.csv`
- `artifacts/sarima_model.pkl`, `artifacts/prophet_model.json`

### **Phase 7: Correlation & Statistical Analysis**
**Goal:** Quantify sentiment vs. real economic indicators — reviewers will ask "does this actually correlate with anything real?"
**What happens:**
- Pearson/Spearman correlation of `sentiment_intensity` against `usd_lkr_rate`, `inflation_rate`, `tourist_arrivals`.
- Cross-correlation at lags (does sentiment lead or lag the exchange rate by 1–3 months?) — this lag analysis is a strong differentiator.
- Save a summary table for the dashboard's Correlation page.
**Files:**
- `src/10_correlation_analysis.py`
- `data/processed/correlation_summary.csv`

### **Phase 8: Streamlit Dashboard**
**Goal:** Multi-page app telling the crisis story end-to-end.
**Pages:**
- **1. Overview:** SL-ESI line chart with event annotations from Phase 5 overlaid as vertical markers.
- **2. Correlation Explorer:** Dual-axis / scatter plots vs. exchange rate, inflation, tourism, with the lag-correlation table from Phase 7.
- **3. Forecast:** SARIMA vs. Prophet forecast with confidence bands and a model-choice explainer.
- **4. Article Explorer:** Filterable `st.dataframe` — month, sentiment polarity, keyword search — showing the actual headlines behind the numbers.
**Files:**
- `pages/1_Overview.py`, `pages/2_Correlations.py`, `pages/3_Forecast.py`, `pages/4_Article_Explorer.py`
- `utils/plotting.py`
- `.streamlit/config.toml`

### **Phase 9: Documentation, Deployment & LinkedIn**
**Goal:** Package for recruiters.
**What happens:**
- Flagship-level `README.md`: problem → data → methodology (FinBERT + SARIMA/Prophet) → key findings (e.g., sentiment-to-forex lag) → live demo link → cross-links to Tourism Forecasting and PickMe NLP projects for a coherent portfolio narrative.
- Deploy to Streamlit Cloud.
- LinkedIn post draft highlighting the 2020–2026 crisis-arc angle.
**Files:**
- `README.md`, `.gitignore`, `docs/linkedin_post_draft.md`

---

