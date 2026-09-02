import pandas as pd
import requests
from pathlib import Path
from io import StringIO
import re

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_inflation_rate.csv'

def fetch_inflation_rate():
    """Fetch inflation data from CBSL website."""
    print("Fetching inflation rate from CBSL...")

    url = "https://www.cbsl.gov.lk/cbsl_custom/inflation/inflationwindow.php"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Use pandas read_html to get all tables
        tables = pd.read_html(StringIO(response.text))

        inflation_data = []

        for table in tables:
            current_year = None
            # We are looking for a table that has "Date" and "inflation" related columns
            # Based on observation, the rate is often in the last column
            for _, row in table.iterrows():
                first_val = str(row.iloc[0]).strip()

                # Check if first column is a year
                if re.match(r'^\d{4}$', first_val):
                    current_year = first_val
                    continue

                # Check if first column is a month
                # Common months in English
                months = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']

                if any(month in first_val for month in months) and current_year:
                    # Extract rate from the last column (index 4 in observed tables)
                    rate_val = str(row.iloc[-1]).strip()

                    # Clean rate value (remove %, handle '-', etc.)
                    if rate_val == '-' or rate_val == 'nan' or not rate_val:
                        continue

                    # Extract numeric value
                    match = re.search(r'(-?\d+\.?\d*)', rate_val)
                    if match:
                        rate = float(match.group(1))

                        # Create a date string
                        # Try to determine the month number
                        month_name = next((m for m in months if m in first_val), 'January')
                        month_num = months.index(month_name) + 1
                        date_str = f"{current_year}-{month_num:02d}"

                        inflation_data.append({
                            'year_month': date_str,
                            'inflation_rate': rate
                        })

        if inflation_data:
            df = pd.DataFrame(inflation_data)
            # Remove duplicates and sort
            df = df.drop_duplicates(subset=['year_month']).sort_values('year_month')

            df.to_csv(OUTPUT_PATH, index=False)
            print(f"Success: Scraped {len(df)} months of inflation data")
            print(f"Saved to: {OUTPUT_PATH}")
            return df
        else:
            raise Exception("No inflation data found in CBSL tables")

    except Exception as e:
        print(f"Error scraping CBSL: {e}")
        print("Trying FRED API as fallback...")

        try:
            # Fallback to FRED API
            fred_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=FPCPITOTLZGLKA"
            fred_resp = requests.get(fred_url, timeout=15)
            fred_resp.raise_for_status()

            df = pd.read_csv(StringIO(fred_resp.text), parse_dates=['DATE'])
            df = df[df['DATE'] >= '2018-01-01'].copy()
            df.rename(columns={'FPCPITOTLZGLKA': 'inflation_rate'}, inplace=True)

            # Annual data - forward fill to monthly
            df.set_index('DATE', inplace=True)
            df = df.resample('ME').ffill().reset_index()
            df['year_month'] = df['DATE'].dt.to_period('M').astype(str)
            df_final = df[['year_month', 'inflation_rate']].copy()

            df_final.to_csv(OUTPUT_PATH, index=False)
            print(f"Success: Fetched {len(df_final)} months of inflation data (from FRED)")
            print(f"Saved to: {OUTPUT_PATH}")
            return df_final

        except Exception as e2:
            print(f"FRED also failed: {e2}")
            print("Creating placeholder data...")

            dates = pd.date_range(start='2018-01-01', end='2026-12-01', freq='MS')
            df_placeholder = pd.DataFrame({
                'year_month': dates.to_period('M').astype(str),
                'inflation_rate': None
            })
            df_placeholder.to_csv(OUTPUT_PATH, index=False)
            return df_placeholder

if __name__ == "__main__":
    fetch_inflation_rate()
