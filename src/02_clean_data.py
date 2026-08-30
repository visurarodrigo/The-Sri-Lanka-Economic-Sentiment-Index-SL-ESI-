import os
import re
import pandas as pd
import numpy as np
from pathlib import Path

# Get the project root directory (parent of src)
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_FILE = PROJECT_ROOT / 'src' / 'data' / 'raw' / 'news_headlines_raw.csv'
OUTPUT_FILE = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'news_headlines_clean.csv'

def clean_text(text):
    """Basic text cleaning for NLP pipelines."""
    if not isinstance(text, str):
        return ""
    
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    
    # Remove special characters and digits (keep letters and spaces)
    # We keep letters, spaces, and basic punctuation like hyphens/apostrophes for context
    text = re.sub(r"[^a-zA-Z\s\-']", ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text.lower()

def main():
    print("Starting SL-ESI Data Cleaning...")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Load raw data
    print(f"Loading data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    print(f"   Loaded {len(df)} rows.")
    
    # 1. Drop rows with missing critical data
    initial_count = len(df)
    df = df.dropna(subset=['title', 'date', 'url']).reset_index(drop=True)
    print(f"   Dropped {initial_count - len(df)} rows with missing critical data.")
    
    # 2. Standardize dates (ensure YYYY-MM-DD)
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
    df = df.dropna(subset=['date']) # Drop any dates that failed to parse
    
    # 3. Create unified text field for NLP
    # Fill NaN snippets with empty string to prevent concatenation errors
    df['snippet'] = df['snippet'].fillna('').astype(str)
    df['text'] = (df['title'].astype(str) + " " + df['snippet']).apply(clean_text)
    
    # 4. Add helper columns for future aggregation
    df['year'] = pd.to_datetime(df['date']).dt.year
    df['month'] = pd.to_datetime(df['date']).dt.month
    df['year_month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str) # e.g., "2022-04"
    
    # 5. Final cleanup: drop raw title/snippet if you only want to keep the clean 'text', 
    # but we'll keep them for the Dashboard's "Article Explorer" page.
    # Let's just reorder columns for neatness.
    columns_order = ['date', 'year', 'month', 'year_month', 'source', 'title', 'snippet', 'text', 'url']
    df = df[columns_order]
    
    # Save to processed CSV
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n Success! Saved {len(df)} clean articles to {OUTPUT_FILE}")
    print(f" Final Date Range: {df['date'].min()} to {df['date'].max()}")
    print(f" Articles per year:\n{df['year'].value_counts().sort_index()}")

if __name__ == "__main__":
    main()