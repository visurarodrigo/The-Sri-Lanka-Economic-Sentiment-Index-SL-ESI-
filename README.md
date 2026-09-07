# 🇱🇰 Sri Lanka Economic Sentiment Index (SL-ESI)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://the-sri-lanka-economic-sentiment-index-sl-esi.streamlit.app/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/visurarodrigo/The-Sri-Lanka-Economic-Sentiment-Index-SL-ESI-)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-FF4B4B?logo=streamlit)](https://streamlit.io/)

> **Tracking the pulse of a nation:** Correlating news media sentiment with macroeconomic recovery from 2020 to 2026.

## 🌐 Live Demo
🔗 **[View the Live Interactive Dashboard](https://the-sri-lanka-economic-sentiment-index-sl-esi.streamlit.app/)**

## 💡 Project Overview
The Sri Lankan economic crisis of 2022 was unprecedented, but could the media have predicted it? The **Sri Lanka Economic Sentiment Index (SL-ESI)** is an end-to-end NLP and time-series forecasting project that quantifies economic sentiment from thousands of news headlines and correlates it with real-world macroeconomic indicators (tourism, exchange rates, and inflation). 

Unlike traditional economic indicators that lag, this project demonstrates that **media sentiment can act as a leading indicator**, predicting inflation spikes up to 2 months in advance.

## 🔑 Key Insights
- 🔮 **Predictive Power:** News sentiment acts as a leading indicator, correlating with inflation spikes with a **2-month lag** (Pearson: -0.492, p < 0.05).
- 📉 **Crisis Reflection:** The index accurately captured the 2022 economic collapse, showing a sharp divergence in sentiment intensity that preceded official macroeconomic downturns.
- ✈️ **Tourism Correlation:** A strong contemporaneous correlation (0.482) between positive sentiment and tourist arrivals, validating the index's reflection of real-world recovery.

## 🛠️ Tech Stack
- **Data Collection & NLP:** Python, BeautifulSoup, `transformers` (FinBERT)
- **Data Processing:** Pandas, NumPy
- **Time Series Forecasting:** Prophet, SARIMA, Statsmodels
- **Visualization & Deployment:** Streamlit, Plotly
- **Version Control:** Git, GitHub

## 📂 Project Structure
```text
├── app.py                      # Main Streamlit entry point
├── pages/                      # Multi-page Streamlit app
│   ├── 1_Overview.py
│   ├── 2_Correlations.py
│   ├── 3_Forecast.py
│   └── 4_Article_Explorer.py
├── src/                        # Data pipeline scripts
│   ├── 01_collect_data.py
│   ├── 02_clean_data.py
│   ├── 03_nlp_scoring.py
│   ├── 04_process_tourism_data.py
│   ├── 05_fetch_exchange_rate.py
│   ├── 06_fetch_inflation_rate.py
│   ├── 07_merge_economic_data.py
│   ├── 08_build_event_annotations.py
│   ├── 09_forecast.py
│   └── 10_correlation_analysis.py
├── data/                       # Raw, processed, and reference data
├── artifacts/                  # Saved models (Prophet, SARIMA) and EDA outputs
├── utils/                      # Helper functions (plotting, UI helpers)
├── requirements.txt            # Python dependencies
└── README.md
```

## 🚀 How to Run Locally
1. Clone the repository:
   ```bash
   git clone https://github.com/visurarodrigo/The-Sri-Lanka-Economic-Sentiment-Index-SL-ESI-.git
   cd The-Sri-Lanka-Economic-Sentiment-Index-SL-ESI-
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).

---
*Built with ❤️ by [Visura Rodrigo](https://github.com/visurarodrigo)*


