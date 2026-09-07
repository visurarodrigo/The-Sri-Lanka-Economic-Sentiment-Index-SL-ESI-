# Sri Lanka Economic Sentiment Index (SL-ESI)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://the-sri-lanka-economic-sentiment-index-sl-esi.streamlit.app/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/visurarodrigo/The-Sri-Lanka-Economic-Sentiment-Index-SL-ESI-)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-FF4B4B?logo=streamlit)](https://streamlit.io/)

> **Tracking the pulse of a nation:** A high-fidelity NLP and Time-Series pipeline quantifying economic sentiment to analyze and forecast Sri Lanka's macroeconomic recovery (2020–2026).

---

## 📖 The Story
The Sri Lankan economic crisis of 2022 was one of the most severe sovereign defaults in modern history. While official macroeconomic indicators (GDP, Inflation, Forex reserves) are critical, they are often **lagging indicators** - they tell us what *happened*, not what is *about to happen*.

The **Sri Lanka Economic Sentiment Index (SL-ESI)** was built to test a hypothesis: **Can the collective sentiment of financial news media act as a leading indicator for economic shocks?** 

By analyzing thousands of headlines from 2020 to 2026, this project captures the full narrative arc: from the pre-crisis stability and COVID-19 shocks to the 2022 collapse, the IMF bailout, and the subsequent fragile recovery.

---

## 🖼️ Visual Showcase

### 🚀 Interactive Dashboard
The project culminates in a multi-page Streamlit application that transforms raw NLP scores into actionable economic insights.

| Home Page | Overview & Events |
| :---: | :---: |
| <img src="artifacts/App previews/Home.png" width="400"> | <img src="artifacts/App previews/Overview .png" width="400"> |

| Correlation Analysis | Economic Forecasting |
| :---: | :---: |
| <img src="artifacts/App previews/Correlation .png" width="400"> | <img src="artifacts/App previews/Forecast.png" width="400"> |

| Article Explorer | |
| :---: | :---: |
| <img src="artifacts/App previews/Artical explorer .png" width="800"> | |

### 📊 Analytical Depth (EDA)
Beyond the app, the project involves rigorous statistical validation:

| Sentiment as a Leading Indicator | Correlation Heatmap |
| :---: | :---: |
| <img src="artifacts/EDA Outputs/Sentiment as Leading-Lagging Indicator.png" width="400"> | <img src="artifacts/EDA Outputs/Correlation Heatmap.png" width="400"> |

---

## 🛠️ Technical Methodology

The SL-ESI is built on a sophisticated 7-phase data pipeline:

### 1. Data Sourcing & NLP Pipeline
- **Collection:** Automated scraping of economy and business sections from *EconomyNext* (2020–2026).
- **Sentiment Scoring:** Leveraged **FinBERT** (`ProsusAI/finbert`), a BERT model pre-trained on financial corpora, ensuring nuance in economic terminology (e.g., distinguishing "inflation" as a neutral term vs. a negative economic signal).
- **Volume Weighting:** To prevent low-volume months from skewing the index, I implemented a log-dampened intensity formula:
  $$\text{Sentiment Intensity} = \text{Mean Sentiment} \times \log(1 + \text{Article Count})$$

### 2. Macroeconomic Integration
Integrated four distinct data streams to validate sentiment against reality:
- **Tourism:** Monthly arrivals data.
- **Currency:** USD/LKR exchange rates (via FRED).
- **Inflation:** Consumer Price Index (CPI) data (via CBSL/FRED).
- **Events:** A custom annotation layer mapping key political and economic shocks (e.g., IMF Deal, Presidential Elections).

### 3. Time-Series Forecasting
To predict future sentiment trends, I compared two industry-standard models:
- **SARIMA:** Captures seasonality and auto-regressive trends.
- **Prophet:** Robust to outliers and handles non-linear growth.

---

## 🔑 Key Findings

- 🔮 **Predictive Signal:** News sentiment acts as a leading indicator for inflation spikes with a **2-month lag** (Pearson: -0.492, $p < 0.05$).
- 📉 **Crisis Mirroring:** The index accurately captured the 2022 collapse, showing a sharp divergence in sentiment intensity that preceded official macroeconomic downturns.
- ✈️ **Tourism Synergy:** A strong contemporaneous correlation (0.482) between positive sentiment and tourist arrivals, validating the index's ability to reflect real-world recovery.

---

## 💻 Tech Stack

- **NLP & ML:** `transformers` (FinBERT), `statsmodels`, `prophet`, `scikit-learn`
- **Data Engineering:** `pandas`, `numpy`, `BeautifulSoup4`
- **Visuals & App:** `streamlit`, `plotly`
- **Environment:** `Python 3.12`, `Git`

---

## 🚀 Getting Started

### Local Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/visurarodrigo/The-Sri-Lanka-Economic-Sentiment-Index-SL-ESI-.git
   cd The-Sri-Lanka-Economic-Sentiment-Index-SL-ESI-
   ```
2. **Setup Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Launch Dashboard:**
   ```bash
   streamlit run app.py
   ```

### Project Structure
```text
├── app.py                      # Main Entry Point
├── pages/                      # Multi-page App Logic
│   ├── 1_Overview.py           # Sentiment Timeline & Event Markers
│   ├── 2_Correlations.py      # Macro-Indicator Correlation Analysis
│   ├── 3_Forecast.py           # SARIMA vs Prophet Predictions
│   └── 4_Article_Explorer.py   # Searchable Sentiment Database
├── src/                        # Data Pipeline (Collection $\rightarrow$ Integration)
├── artifacts/                  # ML Models & EDA Visualizations
├── utils/                      # Reusable Plotting & UI Helpers
└── requirements.txt            # Project Dependencies
```

---

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).

---
*Developed by [Visura Rodrigo](https://github.com/visurarodrigo) as a flagship project in Economic NLP and Time-Series Analysis.*
