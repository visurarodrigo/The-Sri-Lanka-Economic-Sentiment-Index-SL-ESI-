import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOURISM_RAW_PATH = PROJECT_ROOT / 'src' / 'data' / 'raw' / 'sl_tourism_arrivals_clean.csv'
TOURISM_PROCESSED_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_tourism_monthly.csv'

def process_tourism_data():
    """Process tourism data to YYYY-MM format."""
    print("Processing tourism data...")
    
    # Load raw data
    df = pd.read_csv(TOURISM_RAW_PATH)
    
    # Convert Date to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
    
    # Drop rows with invalid dates
    df = df.dropna(subset=['Date'])
    
    # Create year_month column in YYYY-MM format
    df['year_month'] = df['Date'].dt.to_period('M').astype(str)
    
    # Group by month and sum arrivals
    tourism_monthly = df.groupby('year_month')['Arrivals'].sum().reset_index()
    tourism_monthly.rename(columns={'Arrivals': 'tourist_arrivals'}, inplace=True)
    
    # Sort by year_month
    tourism_monthly = tourism_monthly.sort_values('year_month').reset_index(drop=True)
    
    # Save to processed folder
    tourism_monthly.to_csv(TOURISM_PROCESSED_PATH, index=False)
    
    print(f"✓ Processed {len(tourism_monthly)} months of tourism data")
    print(f"✓ Saved to: {TOURISM_PROCESSED_PATH}")
    print("\nFirst 5 rows:")
    print(tourism_monthly.head())
    
    return tourism_monthly

if __name__ == "__main__":
    process_tourism_data()