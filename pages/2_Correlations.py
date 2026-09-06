import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.plotting import create_scatter_plot
from utils.ui_helpers import apply_custom_css, page_header, page_footer

st.set_page_config(page_title="Correlations", page_icon="🔗", layout="wide")

# Apply Modern UI styling
apply_custom_css()
page_header("Correlation Explorer", "🔗")

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / 'src' / 'data' / 'processed'

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH / 'sl_esi_merged_economic.csv', parse_dates=['year_month'])
    corr_df = pd.read_csv(DATA_PATH / 'correlation_summary.csv')
    return df, corr_df

df, corr_df = load_data()

# Scatter Plots
st.subheader("Sentiment vs. Macroeconomic Indicators")
indicator = st.selectbox("Select Indicator", ['tourist_arrivals', 'usd_lkr_rate', 'inflation_rate'])

fig = create_scatter_plot(df, 'sentiment_intensity', indicator, title=f"Sentiment vs {indicator.replace('_', ' ').title()}")
st.plotly_chart(fig, use_container_width=True)

# Lag Correlation Table
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("Lag Correlation Analysis")
st.markdown("""
This table shows the correlation between sentiment and economic indicators at different time lags.
- **Positive Lag**: Sentiment *leads* the economic indicator (predictive power).
- **Negative Lag**: Sentiment *lags* behind the economic indicator (reactive).
""")

# Filter table
selected_indicator = st.selectbox("Filter by Indicator", corr_df['indicator'].unique())
filtered_corr = corr_df[corr_df['indicator'] == selected_indicator]

st.dataframe(filtered_corr, use_container_width=True, hide_index=True)

# Highlight best lag
best_row = filtered_corr.loc[filtered_corr['pearson_corr'].abs().idxmax()]
st.success(f"**Strongest Correlation:** {best_row['pearson_corr']:.3f} at Lag {int(best_row['lag_months'])} ({best_row['direction']})")

page_footer()
