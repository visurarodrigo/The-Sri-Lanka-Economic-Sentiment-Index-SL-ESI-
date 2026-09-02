# 04_merge_economic_data.py
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Input paths
ESI_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_esi_monthly_index.csv'
TOURISM_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_tourism_monthly.csv'
EXCHANGE_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_usd_lkr_exchange.csv'
INFLATION_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_inflation_rate.csv'

# Output path
OUTPUT_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_esi_merged_economic.csv'

def merge_datasets():
    """Merge all economic datasets."""
    print("Merging economic datasets...")
    
    # 1. Load SL-ESI Index
    print("  Loading SL-ESI index...")
    esi_df = pd.read_csv(ESI_PATH)
    esi_df['year_month'] = pd.to_datetime(esi_df['year_month'], format='%Y-%m').dt.to_period('M').astype(str)
    
    # 2. Load Tourism Data
    print("  Loading tourism data...")
    tourism_df = pd.read_csv(TOURISM_PATH)
    
    # 3. Load Exchange Rate
    print("  Loading exchange rate...")
    exchange_df = pd.read_csv(EXCHANGE_PATH)
    
    # 4. Load Inflation Rate
    print("  Loading inflation rate...")
    inflation_df = pd.read_csv(INFLATION_PATH)
    
    # 5. Merge all datasets
    print("  Merging datasets...")
    merged_df = esi_df.copy()
    merged_df = pd.merge(merged_df, tourism_df, on='year_month', how='left')
    merged_df = pd.merge(merged_df, exchange_df, on='year_month', how='left')
    merged_df = pd.merge(merged_df, inflation_df, on='year_month', how='left')
    
    # Sort chronologically
    merged_df = merged_df.sort_values('year_month').reset_index(drop=True)
    
    # Save
    merged_df.to_csv(OUTPUT_PATH, index=False)
    
    print(f"\n✓ Successfully merged {len(merged_df)} rows")
    print(f"✓ Saved to: {OUTPUT_PATH}")
    print("\nPreview (first 10 rows with sentiment data):")
    preview = merged_df[merged_df['article_count'].notna()].head(10)
    print(preview[['year_month', 'article_count', 'sentiment_intensity', 
                   'tourist_arrivals', 'usd_lkr_rate', 'inflation_rate']].to_string(index=False))
    
    return merged_df

if __name__ == "__main__":
    merge_datasets()