import pandas as pd
import requests
from pathlib import Path
from io import StringIO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_usd_lkr_exchange.csv'

def fetch_exchange_rate():
    """Fetch USD/LKR exchange rate from FRED API."""
    print("Fetching USD/LKR exchange rate from FRED...")
    
    try:
        # FRED API direct CSV download
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXSLUS"
        response = requests.get(url)
        response.raise_for_status()
        
        # Read CSV
        df = pd.read_csv(StringIO(response.text), parse_dates=['observation_date'])

        # Filter from 2018 onwards
        df = df[df['observation_date'] >= '2018-01-01'].copy()

        # Rename column
        df.rename(columns={'DEXSLUS': 'usd_lkr_rate'}, inplace=True)

        # Resample to monthly mean
        df.set_index('observation_date', inplace=True)
        df_monthly = df.resample('ME').mean().reset_index()

        # Create year_month column
        df_monthly['year_month'] = df_monthly['observation_date'].dt.to_period('M').astype(str)

        # Keep only needed columns
        df_final = df_monthly[['year_month', 'usd_lkr_rate']].copy()

        # Save to CSV
        df_final.to_csv(OUTPUT_PATH, index=False)

        print(f"[OK] Fetched {len(df_final)} months of exchange rate data")
        print(f"[OK] Saved to: {OUTPUT_PATH}")
        print("\nFirst 5 rows:")
        print(df_final.head())
        
        return df_final
        
    except Exception as e:
        print(f"[ERROR] Error fetching exchange rate: {e}")
        print("Creating placeholder data...")
        
        # Create placeholder data
        dates = pd.date_range(start='2018-01-01', end='2026-12-01', freq='MS')
        df_placeholder = pd.DataFrame({
            'year_month': dates.to_period('M').astype(str),
            'usd_lkr_rate': None
        })
        df_placeholder.to_csv(OUTPUT_PATH, index=False)
        return df_placeholder

if __name__ == "__main__":
    fetch_exchange_rate()