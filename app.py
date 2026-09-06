import streamlit as st
from utils.ui_helpers import apply_custom_css, page_footer

st.set_page_config(page_title="SL-ESI Dashboard", page_icon="🇰", layout="wide")

# Apply Modern UI styling
apply_custom_css()

# Hero Section
st.markdown("""
    <div style='text-align: center; padding: 3rem 1rem;'>
        <h1 style='font-size: 3.5rem; margin-bottom: 0;'>The Sri Lanka Economic Sentiment Index</h1>
        <p style='font-size: 1.5rem; color: #6b7280; max-width: 800px; margin: 1rem auto;'>
            Tracking the pulse of a nation: Correlating news sentiment with macroeconomic recovery from 2020 to 2026.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Feature Grid
col1, col2 = st.columns(2)

with col1:
    st.info("""
    ### 📊 The Sentiment Arc
    Explore the **SL-ESI Overview** to see the core trendline of economic sentiment.
    Understand how the 2022 crisis shifted public perception and how it has evolved during the recovery phase.
    """)
    st.info("""
    ### 🔗 Correlation Analysis
    Dive into the **Correlation Explorer** to see if sentiment serves as a leading indicator
    for tourist arrivals, inflation rates, and exchange rate volatility.
    """)

with col2:
    st.info("""
    ### 🔮 Future Outlook
    Visit the **Forecast** page to see sentiment predictions powered by the Prophet model,
    providing a probabilistic view of economic sentiment for the next 12 months.
    """)
    st.info("""
    ### 📰 Article Evidence
    Use the **Article Explorer** to search through thousands of news headlines
    and see the actual reporting that drives the index values.
    """)

st.markdown("<br>", unsafe_allow_html=True)
st.success("👈 **Ready to explore?** Select a page from the sidebar to begin.")

page_footer()
