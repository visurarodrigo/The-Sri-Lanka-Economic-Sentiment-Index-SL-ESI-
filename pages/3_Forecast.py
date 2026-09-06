import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Forecast", page_icon="🔮", layout="wide")
st.title("Economic Sentiment Forecast (2026-2027)")

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / 'src' / 'data' / 'processed'

@st.cache_data
def load_data():
    hist = pd.read_csv(DATA_PATH / 'sl_esi_merged_economic.csv', parse_dates=['year_month'])
    forecast = pd.read_csv(DATA_PATH / 'sl_esi_forecast_results.csv', parse_dates=['year_month'])
    return hist, forecast

hist, forecast = load_data()

st.markdown("""
This page displays the forecasted Economic Sentiment Intensity for the next 12 months. 
The model used is **Prophet**, which was selected for its superior handling of 
seasonality and confidence intervals compared to SARIMA.
""")

# Model Explainer
with st.expander(" Model Selection Explainer (SARIMA vs. Prophet)"):
    st.markdown("""
    - **SARIMA**: Great for strict linear trends and seasonality, but struggles with the high volatility 
      and structural breaks seen in Sri Lanka's crisis data.
    - **Prophet**: Handles outliers, missing data, and non-linear trends much better. It provides robust 
      confidence intervals (`yhat_lower`, `yhat_upper`), making it the superior choice for this dataset.
    - **Result**: Prophet achieved a lower MAE (0.2856) compared to SARIMA (0.2871) on the holdout set.
    """)

# Forecast Chart
st.subheader("Historical vs. Forecasted Sentiment")
fig = go.Figure()

# Historical Data
fig.add_trace(go.Scatter(
    x=hist['year_month'], y=hist['sentiment_intensity'], 
    mode='lines', name='Historical Sentiment', line=dict(color='#1f77b4', width=2)
))

# Forecast Data
fig.add_trace(go.Scatter(
    x=forecast['year_month'], y=forecast['forecast_sentiment'], 
    mode='lines', name='Forecast (Prophet)', line=dict(color='#ff7f0e', width=3, dash='dot')
))

# Confidence Interval
fig.add_trace(go.Scatter(
    x=forecast['year_month'], y=forecast['upper_bound'],
    mode='lines', name='Upper Bound', line=dict(color='rgba(255, 127, 14, 0.2)', width=0),
    fill='tonexty', fillcolor='rgba(255, 127, 14, 0.2)'
))
fig.add_trace(go.Scatter(
    x=forecast['year_month'], y=forecast['lower_bound'],
    mode='lines', name='Lower Bound', line=dict(color='rgba(255, 127, 14, 0.2)', width=0),
    fill='tozeroy', fillcolor='rgba(255, 127, 14, 0.2)'
))

fig.update_layout(
    title="Sentiment Intensity Forecast with 95% Confidence Interval",
    xaxis_title="Date", yaxis_title="Sentiment Intensity",
    hovermode="x unified", template="plotly_white", height=600
)
st.plotly_chart(fig, use_container_width=True)

# Forecast Table
st.subheader(" Forecasted Values (Next 12 Months)")
st.dataframe(forecast[['year_month', 'forecast_sentiment', 'lower_bound', 'upper_bound']], use_container_width=True, hide_index=True)