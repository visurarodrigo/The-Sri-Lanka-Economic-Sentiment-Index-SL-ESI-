import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.ui_helpers import apply_custom_css, page_header, page_footer

st.set_page_config(page_title="Article Explorer", page_icon="📰", layout="wide")

# Apply Modern UI styling
apply_custom_css()
page_header("Article Explorer", "📰")

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
total_articles = len(filtered_df)
st.markdown(f"### Found **{total_articles}** articles")

if total_articles == 0:
    st.warning("No articles found matching your criteria.")
else:
    # Pagination
    articles_per_page = 20
    num_pages = (total_articles // articles_per_page) + (1 if total_articles % articles_per_page > 0 else 0)

    if num_pages > 1:
        page = st.number_input("Page", min_value=1, max_value=num_pages, value=1)
        start_idx = (page - 1) * articles_per_page
        end_idx = start_idx + articles_per_page
        display_df = filtered_df.iloc[start_idx:end_idx]
        st.markdown(f"Showing articles {start_idx + 1} to {min(end_idx, total_articles)} of {total_articles}")
    else:
        display_df = filtered_df

    # Display Articles
    for _, row in display_df.iterrows():
        with st.expander(f"{row['title']} ({row['date'].strftime('%Y-%m-%d')})"):
            st.write(f"**Source:** {row['source']}")
            st.write(f"**Snippet:** {row['snippet']}")
            st.markdown(f"[Read Full Article]({row['url']})")

page_footer()
