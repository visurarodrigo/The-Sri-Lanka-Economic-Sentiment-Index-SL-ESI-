
### **Phase 1: Data Sourcing & Collection (Week 1)**
**Goal:** Gather a robust, time-stamped dataset of Sri Lankan English news headlines (2022–2026), prioritizing economy, finance, and business sections.
**What Happens:** 
- We identify 2–3 reliable, scrape-friendly sources (e.g., Daily FT, EconomyNext, or RSS feeds from NewsFirst/Ada Derana).
- We write a script to extract the headline, publication date, URL, and optionally a short snippet.
- We save the raw data to ensure reproducibility.
**Files Created:**
- `src/01_collect_data.py` (The scraping/data fetching script)
- `data/raw/news_headlines_raw.csv` (Unprocessed data)
- `requirements.txt` (Updated with new dependencies like `feedparser` or `BeautifulSoup`)

### **Phase 2: Data Cleaning & Preprocessing (Week 1)**
**Goal:** Transform raw text into a clean, analysis-ready format.
**What Happens:**
- Remove duplicates, handle missing dates, and standardize date formats to `YYYY-MM-DD`.
- Filter out irrelevant noise (e.g., sports, entertainment) using simple keyword matching (e.g., "economy", "inflation", "IMF", "rupee", "central bank").
- Create a `month_year` column for later aggregation.
**Files Created:**
- `src/02_clean_data.py`
- `data/processed/news_headlines_clean.csv`

### **Phase 3: NLP Sentiment Scoring & Index Aggregation (Week 2)**
**Goal:** Convert text into a quantifiable monthly sentiment index.
**What Happens:**
- We apply a pre-trained model. *Recommendation:* Use **FinBERT** (financial sentiment) or a fine-tuned **DistilBERT** (since you already have this in your toolkit) to score each headline from -1 (negative) to +1 (positive).
- We aggregate daily scores into a **monthly SL-ESI**. A simple mean is good, but a *volume-weighted mean* (giving more weight to months with higher news volume) is more robust and flagship-level.
**Files Created:**
- `src/03_nlp_scoring.py` (Handles model inference and aggregation)
- `data/processed/sl_esi_monthly_index.csv` (Columns: `month`, `avg_sentiment`, `article_count`, `weighted_sentiment`)
- `models/` (Directory to cache the Hugging Face model locally)

### **Phase 4: Economic Data Integration (Week 2)**
**Goal:** Merge the sentiment index with real-world macroeconomic indicators for correlation analysis.
**What Happens:**
- Fetch historical USD/LKR exchange rates and Sri Lanka CPI/Inflation data (via Central Bank of Sri Lanka API, World Bank API, or a curated CSV).
- Merge this with your existing Sri Lanka Tourism arrivals dataset.
- Align all datasets to the same monthly frequency.
**Files Created:**
- `src/04_fetch_economic_data.py`
- `data/processed/sl_esi_merged_economic.csv` (The master dataset for visualization and forecasting)

### **Phase 5: Time Series Forecasting (Week 3)**
**Goal:** Build a predictive model to forecast future economic sentiment.
**What Happens:**
- We use **Prophet** (recommended here for its robust handling of missing data, easy seasonality modeling, and built-in confidence intervals) to fit the historical monthly SL-ESI.
- We generate a 6–12 month forward forecast.
- We save the model artifacts and forecast results.
**Files Created:**
- `src/05_forecast.py`
- `data/processed/sl_esi_forecast_results.csv`
- `artifacts/prophet_model.json` (or `.pkl`)

### **Phase 6: Streamlit Dashboard Development (Week 3–4)**
**Goal:** Build a polished, multi-page, interactive web app that tells the story.
**What Happens:**
- We use Streamlit’s native `pages/` directory structure for a clean 4-page app.
- **Page 1: SL-ESI Overview:** Line chart of the index over time, with `st.plotly_chart` and annotated vertical markers for key events (e.g., "April 2022: Crisis Peak", "March 2023: IMF Bailout").
- **Page 2: Economic Correlation Explorer:** Dual-axis charts or scatter plots with trendlines showing Sentiment vs. USD/LKR, Inflation, and Tourism.
- **Page 3: Sentiment Forecast:** Prophet forecast plot with shaded confidence intervals, explaining the model’s assumptions.
- **Page 4: Article Explorer:** An interactive `st.dataframe` with filters for month, sentiment polarity (Positive/Negative/Neutral), and keyword search, allowing users to read the actual headlines driving the data.
**Files Created:**
- `app.py` (or `pages/1_📈_Overview.py`, `pages/2_🔗_Correlations.py`, `pages/3_🔮_Forecast.py`, `pages/4_📰_Article_Explorer.py`)
- `utils/plotting.py` (Reusable, clean Plotly chart functions to keep page files tidy)
- `.streamlit/config.toml` (For theming and page settings)

### **Phase 7: Documentation, Deployment & LinkedIn (Week 4)**
**Goal:** Package the project professionally for public viewing and recruiter attention.
**What Happens:**
- Write a comprehensive, flagship-level `README.md` (Problem, Solution, Methodology, Tech Stack, Key Findings, Live Demo link, and cross-links to your PickMe and Tourism projects).
- Push to GitHub and deploy to Streamlit Cloud.
- Draft a high-impact LinkedIn post.
**Files Created:**
- `README.md`
- `.gitignore` (Ensuring raw data or large model files aren’t unnecessarily committed)
- `docs/linkedin_post_draft.md`


