# Technical Report: Sri Lanka Economic Sentiment Index (SL-ESI)

**Project Links:** [🚀 Live Dashboard](https://the-sri-lanka-economic-sentiment-index-sl-esi.streamlit.app/) | [💻 GitHub Repository](https://github.com/visurarodrigo/The-Sri-Lanka-Economic-Sentiment-Index-SL-ESI-)

![Project Home](artifacts/App%20previews/Home.png)

## 1. Executive Summary

The **Sri Lanka Economic Sentiment Index (SL-ESI)** is a high-fidelity analytical framework designed to quantify and forecast macroeconomic health through the lens of financial news sentiment. By integrating Natural Language Processing (NLP) with traditional time-series analysis, the project examines the narrative arc of Sri Lanka's economy from the onset of the COVID-19 pandemic in early 2020 through the catastrophic sovereign default of 2022 and into the subsequent fragile recovery period ending in August 2026.

### Key Achievements
The project successfully implemented a seven-phase data engineering and machine learning pipeline, transforming thousands of raw news headlines into a structured sentiment index. This index was then validated against three critical macroeconomic indicators: tourist arrivals, the USD/LKR exchange rate, and the national inflation rate.

### Main Findings
- **Predictive Capability:** News sentiment serves as a statistically significant leading indicator for inflation spikes, exhibiting a **2-month lead time** (Pearson correlation: -0.492, $p < 0.05$).
- **Crisis Mirroring:** The index accurately captured the 2022 economic collapse, with sentiment intensity plummeting to a peak negative value of **-1.305 in May 2022**, preceding the worst of the macroeconomic downturn.
- **Recovery Synchronization:** A strong contemporaneous correlation (0.482) was identified between positive sentiment and the recovery of tourist arrivals, suggesting that media sentiment closely tracks real-world tourism rebound.
- **Model Performance:** Among the time-series models evaluated, **Prophet** demonstrated superior robustness to outliers and better out-of-sample forecasting accuracy compared to SARIMA for this specific volatility-heavy dataset.

---

## 2. Project Overview

### Problem Statement
Traditional macroeconomic indicators—such as GDP growth, Consumer Price Index (CPI), and Foreign Exchange reserves—are inherently **lagging indicators**. They record events after they have occurred, often with a reporting delay of weeks or months. In the context of Sri Lanka's volatile economic environment, there is a critical need for **leading indicators** that can signal impending shocks or recovery phases before they are fully reflected in official statistics.

### Objectives
The primary goal of the SL-ESI is to test the hypothesis that the collective sentiment of professional financial news media acts as a proxy for economic expectations and can forecast macroeconomic shifts. Specifically, the project aims to:
1. Build a robust pipeline for automated financial news collection and sentiment quantification.
2. Develop a volume-weighted sentiment index to mitigate the noise of low-coverage periods.
3. Statistically validate the relationship between sentiment and macroeconomic reality.
4. Forecast future sentiment trends to provide an early-warning signal for economic instability.

### Scope
- **Time Period:** February 2020 to August 2026.
- **Data Sources:** News headlines and snippets from *EconomyNext*, macroeconomic data from the Federal Reserve Economic Data (FRED) API, and the Central Bank of Sri Lanka (CBSL).
- **Focus:** Economic and business sentiment specifically tailored to the Sri Lankan context.

### Significance
This project contributes to the field of "Nowcasting"—the attempt to predict the present or very near future. By combining behavioral data (sentiment) with structural data (macro indicators), the SL-ESI provides a more holistic view of the crisis-to-recovery narrative, offering a tool that is potentially useful for policymakers, investors, and economic researchers.

---

## 3. Methodology

### 3.1 Data Collection
The foundation of the SL-ESI is a comprehensive dataset of financial news.

![Data Collection Stats](artifacts/EDA%20Outputs/Data%20Collection%20Statistics.png)

- **News Sourcing:** An automated scraper was developed to extract titles, dates, and snippets from the "Economy" and "Business" sections of *EconomyNext*. This source was selected for its focus on high-impact financial reporting.
- **Economic Indicators:**
    - **Tourism:** Monthly tourist arrival figures.
    - **Exchange Rate:** USD/LKR daily rates resampled to monthly means via the FRED API (`DEXSLUS`).
    - **Inflation:** Monthly CPI inflation rates sourced from CBSL and FRED.
- **Volume:** The pipeline processed thousands of articles, ensuring coverage across the entire 2020–2026 window.

### 3.2 Data Processing Pipeline
The raw data underwent a rigorous multi-stage transformation:

![Sentiment Distribution](artifacts/EDA%20Outputs/Sentiment%20Distribution%20Over%20Time.png)

1. **Cleaning:** Articles were deduplicated by URL, and dates were standardized. A unified `text` field was created by combining titles and snippets.
2. **NLP Sentiment Analysis:** Each article was scored using **FinBERT** (`ProsusAI/finbert`), a BERT-based model pre-trained on a massive financial corpus. Unlike general-purpose sentiment models, FinBERT distinguishes between "inflation" as a neutral economic term and "inflation" as a negative signal in a financial context. The output is a continuous score ranging from **-1 (highly negative) to +1 (highly positive)**.
3. **Index Calculation:** To prevent months with very few articles from skewing the index, a **log-dampened intensity formula** was implemented:
   $$\text{Sentiment Intensity} = \text{Mean Sentiment} \times \log(1 + \text{Article Count})$$
   This ensures that months with high media volume (typically during crises) register a stronger signal, reflecting the "intensity" of the public narrative.

### 3.3 Economic Data Integration
The sentiment index was merged with macroeconomic data on a `year_month` basis. 

![Multi-Indicator Timeline](artifacts/EDA%20Outputs/Multi-Indicator%20Timeline.png)

- **Merging Strategy:** A left-join approach was used, ensuring the sentiment timeline remained the primary axis.
- **Handling Missing Data:** For the inflation rate, which suffered from reporting gaps in 2023, a tiered fallback strategy was used: CBSL $\rightarrow$ FRED $\rightarrow$ Linear Interpolation/Placeholder.

### 3.4 Event Annotation
To provide context to the numerical trends, a custom annotation layer was built. 

![Events Timeline](artifacts/EDA%20Outputs/Events%20Timeline.png)

Key events were categorized into three types:
- **External Shocks:** (e.g., COVID-19 Lockdown, Global Trade War, Cyclone Ditwah).
- **Policy Shocks/Reforms:** (e.g., Organic Fertilizer Ban, Vehicle Import Liberalization).
- **Political Shifts:** (e.g., Sovereign Default, President's Flight, IMF Bailout, 2024 Elections).

### 3.5 Forecasting Models
Two distinct time-series models were compared to forecast the `sentiment_intensity`:

![Model Comparison](artifacts/EDA%20Outputs/Model%20Comparison.png)

1. **SARIMA (Seasonal AutoRegressive Integrated Moving Average):** Used to capture linear trends and strong monthly seasonality.
2. **Prophet (by Meta):** Used for its ability to handle non-linear growth and its robustness to extreme outliers (common in crisis data).

**Model Selection:** The models were evaluated using a backtesting approach (training on data up to Dec 2025, testing on 2026). Prophet was selected as the primary model due to a lower Mean Absolute Error (MAE) and better handling of the volatile sentiment swings observed during political shifts.

### 3.6 Correlation Analysis
The relationship between sentiment and indicators was tested using Pearson and Spearman correlations.

![Correlation Heatmap](artifacts/EDA%20Outputs/Correlation%20Heatmap.png)
![Leading Indicator Analysis](artifacts/EDA%20Outputs/Sentiment%20as%20Leading-Lagging%20Indicator.png)

- **Lag Analysis:** Cross-correlation was performed at lags of -3 to +3 months to determine if sentiment leads or lags the economic indicators.
- **Statistical Significance:** P-values were calculated to ensure that the observed correlations were not due to random chance.

---

## 4. Key Findings

### Sentiment Trends and Crisis Mirroring
The SL-ESI exhibited a striking correlation with the real-world economic collapse of 2022. 

![Multi-Indicator Timeline](artifacts/EDA%20Outputs/Multi-Indicator%20Timeline.png)

- **The May 2022 Trough:** The index hit its absolute minimum of **-1.305** in May 2022. This coincided with the peak of fuel shortages and the initial signals of a sovereign default.
- **The 2023 Stabilization:** Sentiment began a slow climb following the **IMF Bailout approval in March 2023**, indicating that the market perceived the bailout as the primary turning point for stability.

### Correlation with Economic Indicators
| Indicator | Peak Correlation | Lag | Significance | Relationship |
| :--- | :---: | :---: | :---: | :--- |
| **Inflation Rate** | -0.492 | +2 Mo | High | Sentiment leads inflation spikes |
| **Tourist Arrivals** | 0.482 | 0 Mo | High | Strong contemporaneous link |
| **Exchange Rate** | Low | N/A | Low | Weak direct linear correlation |

The most significant finding is the **2-month leading relationship with inflation**. A sharp drop in news sentiment typically preceded a rise in the inflation rate, suggesting that financial media captures the "expectation" of price hikes before they are fully realized in the CPI.

### Recovery Arc
The period from 2024 to 2026 shows a "fragile recovery" narrative. Sentiment became more positive following the 2024 elections and the liberalization of imports. By August 2026, the sentiment intensity had recovered to **1.21**, reflecting a cautiously optimistic outlook on macroeconomic stability.

---

## 5. Technical Implementation

### 5.1 Architecture
The project is structured as a sequential pipeline, moving from raw data to a deployed application.

**Data Flow:**
`EconomyNext Scraper` $\rightarrow$ `Cleaning Module` $\rightarrow$ `FinBERT Scorer` $\rightarrow$ `Macro Integration` $\rightarrow$ `Annotation Layer` $\rightarrow$ `Forecasting/Correlation` $\rightarrow$ `Streamlit Dashboard`.

**Technology Stack:**
- **Language:** Python 3.12
- **NLP:** `transformers` (HuggingFace), `ProsusAI/finbert`
- **Time-Series:** `prophet`, `statsmodels` (SARIMAX)
- **Data Manipulation:** `pandas`, `numpy`
- **Visualization:** `plotly`, `matplotlib`, `seaborn`
- **Deployment:** `streamlit`

### 5.2 Key Components
- **Collection Scripts (`01_collect_data.py`):** Implements paginated scraping with retry logic to handle website timeouts.
- **NLP Scorer (`03_nlp_scoring.py`):** Manages the FinBERT pipeline and implements the log-weighted intensity formula.
- **Economic Integrator (`04_` through `07_`):** Modular scripts that fetch data from different sources (FRED, CBSL) and merge them into a master dataset.
- **Analysis Modules (`09_forecast.py`, `10_correlation_analysis.py`):** Conduct the heavy statistical lifting, including model backtesting and lag analysis.
- **Dashboard (`app.py` & `pages/`):** A multi-page Streamlit app providing interactive access to the findings.

### 5.3 Data Files
- **Raw Data:** `news_headlines_raw.csv` (unprocessed scraping results).
- **Processed Data:** `sl_esi_merged_economic.csv` (the master dataset containing sentiment, FX, inflation, and tourism).
- **Reference Data:** `key_events.csv` (the curated list of economic and political shocks).

---

## 6. Dashboard Features

The Streamlit dashboard transforms the technical analysis into an accessible narrative:

1. **Overview Page:** 
   ![Overview Preview](artifacts/App%20previews/Overview%20.png)
   - Features the primary SL-ESI timeline.
   - Overlays the `key_events.csv` data as vertical markers, allowing users to see exactly how events (like the IMF deal) affected the index.

2. **Correlations Page:**
   ![Correlations Preview](artifacts/App%20previews/Correlation%20.png)
   - Provides interactive dual-axis charts comparing sentiment with the exchange rate, inflation, and tourism.
   - Displays the lag-correlation table to prove the "leading indicator" hypothesis.

3. **Forecast Page:**
   ![Forecast Preview](artifacts/App%20previews/Forecast.png)
   - Visualizes the Prophet model's predictions for the next 12 months.
   - Includes confidence intervals (shaded areas) to represent the uncertainty of the forecast.

4. **Article Explorer:**
   ![Article Explorer Preview](artifacts/App%20previews/Artical%20explorer%20.png)
   - A searchable database of all headlines used in the study.
   - Allows users to filter by sentiment polarity, enabling them to see the specific news stories that drove the index down during the 2022 crisis.

---

## 7. Visualizations

The project relies on several key visualizations to communicate findings:
- **Multi-Indicator Timeline:** Overlays sentiment, inflation, and FX rates on a single timeline to show the 2022 divergence.
- **Correlation Heatmap:** A matrix showing the strength of relationships between all variables, highlighting the inflation-sentiment link.
- **Lag Analysis Plots:** Charts showing how correlation changes as sentiment is shifted by 1, 2, or 3 months.
- **Model Comparison Plot:** A visual comparison of SARIMA vs. Prophet's fit on the test set, justifying the choice of Prophet.
- **Sentiment Distribution Over Time:** A histogram showing the shift from a neutral distribution (2020) to a polarized, negative distribution (2022) and back.

---

## 8. Challenges & Solutions

### Data Quality and Availability
- **Challenge:** The inflation rate data from the Central Bank had gaps and inconsistent formatting for certain years.
- **Solution:** Implemented a tiered data fetching strategy. If the primary CBSL source failed, the script attempted to fetch from FRED; if both failed, it used linear interpolation for short gaps to maintain time-series continuity.

### Volume-Sentiment Skew
- **Challenge:** In months with very few articles, a single highly positive or negative headline could swing the mean sentiment drastically, creating "fake" volatility.
- **Solution:** Developed the `sentiment_intensity` metric. By multiplying the mean by $\log(1 + \text{count})$, the project ensures that sentiment moves are only considered "intense" when they are backed by significant media volume.

### Model Volatility
- **Challenge:** Standard ARIMA models struggled with the extreme "black swan" events of 2022 (e.g., the President fleeing), which created massive outliers.
- **Solution:** Transitioned to **Prophet**, which uses a decomposable time-series model (trend, seasonality, holidays) and is far more robust to outliers, resulting in a more stable long-term forecast.

---

## 9. Limitations

- **Source Bias:** The index relies solely on *EconomyNext*. While it is a premier financial source, the index may reflect the specific editorial perspective of one organization.
- **Language Constraint:** The analysis is limited to English-language news. Economic sentiment in Sinhala and Tamil media may differ and was not captured.
- **Causality vs. Correlation:** While the 2-month lead for inflation is statistically significant, this is a correlation. It does not definitively prove that news *causes* inflation, but rather that it *signals* it.
- **External Shock Sensitivity:** The model' accuracy can be temporarily degraded by completely unpredictable events (e.g., Cyclone Ditwah), which no historical model can forecast.

---

## 10. Future Work

To evolve the SL-ESI into a production-grade economic tool, the following improvements are proposed:
1. **Multi-Source Integration:** Expand the scraper to include other news outlets and official government press releases to reduce bias.
2. **Multilingual NLP:** Incorporate Sinhala and Tamil BERT models to capture a broader spectrum of national sentiment.
3. **Real-Time Pipeline:** Transition from batch processing to a real-time API-driven pipeline that updates the index daily.
4. **Expanded Indicator Set:** Integrate other indicators such as energy prices, electricity generation levels, and stock market indices (CSE) to deepen the correlation analysis.

---

## 11. Conclusion

The Sri Lanka Economic Sentiment Index (SL-ESI) successfully demonstrates that financial news sentiment is a powerful, low-latency proxy for macroeconomic health. The project's most critical contribution is the empirical validation of sentiment as a leading indicator for inflation in the Sri Lankan context. 

By capturing the full arc from the 2020 pandemic to the 2022 default and the subsequent recovery, the SL-ESI provides a blueprint for how behavioral NLP can complement traditional economic analysis. The findings suggest that monitoring media "intensity" can provide early warnings of economic instability, offering a valuable tool for risk management in volatile emerging markets.

---

## 12. References & Resources

- **Data Sources:**
    - *EconomyNext* (News Headlines)
    - *Federal Reserve Economic Data (FRED)* (USD/LKR Exchange Rate)
    - *Central Bank of Sri Lanka (CBSL)* (CPI Inflation)
- **Technical References:**
    - `ProsusAI/finbert`: Pre-trained BERT model for financial sentiment.
    - `Prophet`: Time-series forecasting framework by Meta.
    - `Statsmodels`: Python library for SARIMAX implementation.
- **Code Repository:** [GitHub - The-Sri-Lanka-Economic-Sentiment-Index-SL-ESI-](https://github.com/visurarodrigo/The-Sri-Lanka-Economic-Sentiment-Index-SL-ESI-)
