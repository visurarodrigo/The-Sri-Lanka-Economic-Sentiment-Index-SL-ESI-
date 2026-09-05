import streamlit as st

st.set_page_config(page_title="SL-ESI Dashboard", page_icon="🇰", layout="wide")

st.title("🇱🇰 Sri Lanka Economic Sentiment Index (SL-ESI)")
st.markdown("""
Welcome to the **Sri Lanka Economic Sentiment Index (SL-ESI)** Dashboard. 
This interactive dashboard tracks the economic sentiment of Sri Lanka from 2020 to 2026, 
correlating news sentiment with real-world macroeconomic indicators like tourism, 
exchange rates, and inflation.

### 🧭 Navigation
Use the sidebar to explore the different pages:
- ** Overview**: The core SL-ESI trendline with major economic events.
- ** Correlation Explorer**: How sentiment correlates with real economic indicators.
- **🔮 Forecast**: Future sentiment predictions using SARIMA and Prophet.
- **📰 Article Explorer**: Read the actual news headlines driving the sentiment.
""")

st.info("👈 Select a page from the sidebar to begin exploring.")