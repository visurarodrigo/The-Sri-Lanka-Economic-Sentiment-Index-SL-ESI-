import streamlit as st

def apply_custom_css():
    """Applies custom CSS to make the Streamlit app look modern and professional."""
    st.markdown("""
        <style>
        /* Main background and font */
        .stApp {
            background-color: #f8f9fa;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }

        /* Title and headers */
        h1 {
            color: #1e3a8a;
            font-weight: 800 !important;
            letter-spacing: -0.02em !important;
        }
        h2, h3 {
            color: #3b82f6;
            font-weight: 700 !important;
        }

        /* Custom card style for metrics */
        [data-testid="stMetric"] {
            background-color: white;
            border: 1px solid #e5e7eb;
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #1e293b;
            color: white;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* Better table styling */
        .stDataFrame {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
        }

        /* Info and success boxes */
        .stAlert {
            border-radius: 12px !important;
            border: none !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        /* Button styling */
        .stButton>button {
            border-radius: 8px;
            background-color: #3b82f6;
            color: white;
            border: none;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #2563eb;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

def page_header(title, icon="🚀"):
    """Standardized page header with an icon and a horizontal rule."""
    st.markdown(f"## {icon} {title}")
    st.markdown("---")

def page_footer():
    """Standardized footer for all pages."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center; color: #6b7280; font-size: 0.8rem; padding: 1rem;'>
            © 2026 Sri Lanka Economic Sentiment Index (SL-ESI) Project • Built with Streamlit & Plotly
        </div>
        """,
        unsafe_allow_html=True
    )
