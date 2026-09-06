import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.plotting import create_line_chart_with_events
from utils.ui_helpers import apply_custom_css, page_header, page_footer

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")

# Apply Modern UI styling
apply_custom_css()
page_header("SL-ESI Overview: The Crisis & Recovery Arc", "📊")

# Paths
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / 'src' / 'data' / 'processed'
REF_PATH = ROOT / 'src' / 'data' / 'reference'

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH / 'sl_esi_merged_economic.csv', parse_dates=['year_month'])
    events = pd.read_csv(REF_PATH / 'key_events.csv', parse_dates=['date'])
    return df, events

df, events = load_data()

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest Sentiment", f"{df['sentiment_intensity'].iloc[-1]:.2f}")
col2.metric("Latest Exchange Rate", f"Rs. {df['usd_lkr_rate'].iloc[-1]:.2f}")
col3.metric("Latest Inflation", f"{df['inflation_rate'].iloc[-1]:.2f}%")
col4.metric("Latest Tourists", f"{int(df['tourist_arrivals'].iloc[-1]):,}")

st.markdown("<br>", unsafe_allow_html=True)

# Main Chart
st.subheader("Economic Sentiment Intensity Over Time")
fig = create_line_chart_with_events(df, 'year_month', 'sentiment_intensity', events,
                                    "SL-ESI Sentiment Intensity with Key Events", "Sentiment Intensity")
st.plotly_chart(fig, use_container_width=True)

# Event Details
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("Key Economic & Political Events")
st.dataframe(events[['date', 'label', 'category', 'description']], use_container_width=True, hide_index=True)

page_footer()
