import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Article Explorer", page_icon="", layout="wide")
st.title(" Article Explorer")

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / 'src' / 'data' / 'raw'

@st.cache_data
def load_articles():
    # Load raw data to show actual headlines and snippets
    df = pd.read_csv(RAW_PATH / 'news_headlines_raw.csv', parse_dates=['date'])
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    return df

df = load_articles()

# Filters
st.sidebar.header(" Filters")
selected_year = st.sidebar.multiselect("Select Year", options=sorted(df['year'].unique()), default=sorted(df['year'].unique()))
selected_month = st.sidebar.multiselect("Select Month", options=sorted(df['month'].unique()), default=sorted(df['month'].unique()))
search_term = st.sidebar.text_input("🔎 Search Headlines/Snippets", "")

# Apply Filters
filtered_df = df[
    (df['year'].isin(selected_year)) & 
    (df['month'].isin(selected_month))
]

if search_term:
    mask = filtered_df['title'].str.contains(search_term, case=False, na=False) | \
           filtered_df['snippet'].str.contains(search_term, case=False, na=False)
    filtered_df = filtered_df[mask]

# Display Stats
st.markdown(f"### Showing **{len(filtered_df)}** articles")

# Display Articles
for _, row in filtered_df.iterrows():
    with st.expander(f"{row['title']} ({row['date'].strftime('%Y-%m-%d')})"):
        st.write(f"**Source:** {row['source']}")
        st.write(f"**Snippet:** {row['snippet']}")
        st.markdown(f"[Read Full Article]({row['url']})")