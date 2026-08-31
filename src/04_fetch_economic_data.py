import os
import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Configuration
ESI_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_esi_monthly_index.csv'
TOURISM_PATH = PROJECT_ROOT / 'src' / 'data' / 'raw' / 'sl_tourism_arrivals_clean.csv'
OUTPUT_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_esi_merged_economic.csv'

def process_tourism_data():
    """Load and clean the tourism dataset to match YYYY-MM format."""
    print(f"📂 Processing tourism data from {TOURISM_PATH}...")
    df = pd.read_csv(TOURISM_PATH)
    
    # Convert 'Date' column to datetime. 
    # The format is M/D/YYYY, so we let pandas infer it, but explicitly handle it.
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    
    # Drop any rows where date parsing failed
    df = df.dropna(subset=['Date'])
    
    # Create the year_month column in YYYY-MM format
    df['year_month'] = df['Date'].dt.to_period('M').astype(str)
    
    # Group by year_month and sum arrivals (just in case there are multiple entries per month)
    tourism_monthly = df.groupby('year_month')['Arrivals'].sum().reset_index()
    tourism_monthly.rename(columns={'Arrivals': 'tourist_arrivals'}, inplace=True)
    
    print(f" Tourism data processed: {len(tourism_monthly)} months.")
    return tourism_monthly

def fetch_macro_data():
    """Fetch USD/LKR exchange rate and Inflation from FRED API."""
    print("Fetching macroeconomic data from FRED API...")
    
    start_date = "2018-01-01"
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    macro_df = pd.DataFrame()
    
    try:
        # Fetch Exchange Rate: Sri Lanka Rupees to One U.S. Dollar (Monthly)
        # Series ID: EXSRSL
        print(" Fetching USD/LKR Exchange Rate (EXSRSL)...")
        exchange_df = pdr.DataReader('EXSRSL', 'fred', start_date, end_date)
        exchange_df.columns = ['usd_lkr_rate']
        exchange_df['year_month'] = exchange_df.index.to_period('M').astype(str)
        
        # Fetch Inflation: Consumer Price Index, Annual Percent Change
        # Series ID: PCPIPCTL (Inflation, consumer prices, Sri Lanka)
        print(" Fetching Inflation Rate (PCPIPCTL)...")
        inflation_df = pdr.DataReader('PCPIPCTL', 'fred', start_date, end_date)
        inflation_df.columns = ['inflation_rate']
        inflation_df['year_month'] = inflation_df.index.to_period('M').astype(str)
        
        # Merge macro data
        macro_df = pd.merge(exchange_df, inflation_df, on='year_month', how='outer')
        macro_df['year_month'] = pd.to_datetime(macro_df['year_month'])
        
        # Forward fill missing inflation values (common with monthly CPI data)
        macro_df['inflation_rate'] = macro_df['inflation_rate'].ffill()
        
        print(" Macro data fetched successfully.")
        
    except Exception as e:
        print(f"  Error fetching from FRED: {e}")
        print("   Creating placeholder data. Please check your internet connection or FRED API.")
        # Fallback placeholder to prevent pipeline crash
        dates = pd.date_range(start="2020-01", end="2026-05", freq='MS')
        macro_df = pd.DataFrame({
            'year_month': dates.to_period('M').astype(str),
            'usd_lkr_rate': np.nan,
            'inflation_rate': np.nan
        })
        macro_df['year_month'] = pd.to_datetime(macro_df['year_month'])

    return macro_df

def main():
    print("Starting Phase 4: Economic Data Integration...")
    
    # 1. Load SL-ESI Index
    print(f"Loading SL-ESI index from {ESI_PATH}...")
    esi_df = pd.read_csv(ESI_PATH)
    esi_df['year_month'] = pd.to_datetime(esi_df['year_month'])
    
    # 2. Process Tourism Data
    tourism_df = process_tourism_data()
    tourism_df['year_month'] = pd.to_datetime(tourism_df['year_month'])
    
    # 3. Fetch Macro Data
    macro_df = fetch_macro_data()
    
    # 4. Merge All Datasets
    print("Merging Sentiment, Tourism, and Macroeconomic data...")
    merged_df = pd.merge(esi_df, tourism_df, on='year_month', how='outer')
    merged_df = pd.merge(merged_df, macro_df, on='year_month', how='outer')
    
    # Sort chronologically
    merged_df = merged_df.sort_values('year_month').reset_index(drop=True)
    
    # Format year_month back to string for clean CSV output
    merged_df['year_month'] = merged_df['year_month'].dt.strftime('%Y-%m')
    
    # 5. Save to Processed Directory
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    merged_df.to_csv(OUTPUT_PATH, index=False)
    
    print(f"\n Success! Saved merged dataset to {OUTPUT_PATH}")
    print(" Preview of merged data (First 10 Months):")
    print(merged_df[['year_month', 'article_count', 'sentiment_intensity', 'tourist_arrivals', 'usd_lkr_rate', 'inflation_rate']].head(10).to_string(index=False))

if __name__ == "__main__":
    main()