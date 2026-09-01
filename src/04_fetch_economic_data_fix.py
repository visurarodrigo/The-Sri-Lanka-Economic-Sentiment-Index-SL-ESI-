import os
from pathlib import Path
import pandas as pd
import requests
from io import StringIO

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Configuration
MERGED_DATA_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_esi_merged_economic.csv'
OUTPUT_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_esi_merged_economic.csv'

def fetch_fred_data():
    print("🌐 Fetching macroeconomic data directly from FRED API...")
    
    # 1. Fetch Exchange Rate (DEXSLUS)
    print("   📉 Fetching Monthly USD/LKR Exchange Rate (DEXSLUS)...")
    url_exch = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXSLUS"
    try:
        resp_exch = requests.get(url_exch)
        resp_exch.raise_for_status()
        df_exch = pd.read_csv(StringIO(resp_exch.text), parse_dates=['DATE'], index_col='DATE')
        df_exch = df_exch['2018-01-01':'2026-12-31'].copy()
        df_exch['year_month'] = df_exch.index.to_period('M').astype(str)
        df_exch_monthly = df_exch.groupby('year_month')['DEXSLUS'].mean().reset_index()
        df_exch_monthly.rename(columns={'DEXSLUS': 'usd_lkr_rate'}, inplace=True)
    except Exception as e:
        print(f"   ⚠️ Error fetching exchange rate: {e}")
        df_exch_monthly = pd.DataFrame(columns=['year_month', 'usd_lkr_rate'])

    # 2. Fetch Inflation (FPCPITOTLZGLKA)
    print("   📈 Fetching Annual Inflation Rate (FPCPITOTLZGLKA) and forward-filling...")
    url_inf = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=FPCPITOTLZGLKA"
    try:
        resp_inf = requests.get(url_inf)
        resp_inf.raise_for_status()
        df_inf = pd.read_csv(StringIO(resp_inf.text), parse_dates=['DATE'], index_col='DATE')
        df_inf = df_inf['2018-01-01':'2026-12-31'].copy()
        df_inf['year'] = df_inf.index.year.astype(str)
        df_inf.rename(columns={'FPCPITOTLZGLKA': 'inflation_rate'}, inplace=True)
        
        # Create monthly dataframe and forward-fill the annual data
        dates = pd.date_range(start='2018-01-01', end='2026-12-01', freq='MS')
        df_inf_monthly = pd.DataFrame({'year_month': dates.to_period('M').astype(str)})
        df_inf_monthly['year'] = df_inf_monthly['year_month'].str[:4]
        
        df_inf_monthly = df_inf_monthly.merge(df_inf[['year', 'inflation_rate']], on='year', how='left')
        df_inf_monthly['inflation_rate'] = df_inf_monthly['inflation_rate'].ffill()
        df_inf_monthly = df_inf_monthly[['year_month', 'inflation_rate']]
        
    except Exception as e:
        print(f"   ⚠️ Error fetching inflation: {e}")
        dates = pd.date_range(start='2018-01-01', end='2026-12-01', freq='MS')
        df_inf_monthly = pd.DataFrame({'year_month': dates.to_period('M').astype(str), 'inflation_rate': pd.NA})

    # Merge macro data together
    macro_df = pd.merge(df_exch_monthly, df_inf_monthly, on='year_month', how='outer')
    return macro_df

def main():
    print("🚀 Starting Phase 4: Economic Data Integration (Robust)...")
    
    # 1. Load existing data
    print(f"📂 Loading existing data from {MERGED_DATA_PATH}...")
    if not os.path.exists(MERGED_DATA_PATH):
        print("❌ Base merged data not found. Please run previous steps first.")
        return
    df_base = pd.read_csv(MERGED_DATA_PATH)
    
    # 2. Fetch macro data
    macro_df = fetch_fred_data()
    
    # 3. Merge
    print("🔗 Merging macroeconomic data with existing dataset...")
    df_final = df_base.merge(macro_df, on='year_month', how='left')
    
    # 4. Save
    print(f"💾 Saving corrected dataset to {OUTPUT_PATH}...")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df_final.to_csv(OUTPUT_PATH, index=False)
    
    print("\n✅ Success! Saved corrected dataset.")
    print("📊 Preview of corrected data (First 15 Months):")
    
    # Safety check: only print columns that actually exist to prevent KeyError
    cols_to_print = ['year_month', 'article_count', 'sentiment_intensity', 'tourist_arrivals', 'usd_lkr_rate', 'inflation_rate']
    existing_cols = [c for c in cols_to_print if c in df_final.columns]
    
    print(df_final[existing_cols].head(15).to_string(index=False))

if __name__ == "__main__":
    main()