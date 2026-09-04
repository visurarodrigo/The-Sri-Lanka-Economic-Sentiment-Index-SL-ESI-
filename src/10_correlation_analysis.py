import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

# Define paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_esi_merged_economic.csv'
OUTPUT_PATH = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'correlation_summary.csv'

def calculate_lagged_correlations(df, target_col, indicator_col, max_lag=3):
    """
    Calculate Pearson and Spearman correlations between target and indicator at various lags.
    
    Positive lag (e.g., lag=1): target is shifted forward. 
    Meaning: We are correlating target(t-1) with indicator(t). 
    -> This tests if sentiment LEADS the economic indicator.
    
    Negative lag (e.g., lag=-1): target is shifted backward.
    Meaning: We are correlating target(t+1) with indicator(t).
    -> This tests if sentiment LAGS the economic indicator.
    """
    results = []
    
    for lag in range(-max_lag, max_lag + 1):
        # Create shifted series
        if lag > 0:
            # Sentiment leads: shift sentiment forward (so t-1 aligns with t)
            x = df[target_col].shift(lag)
            y = df[indicator_col]
        elif lag < 0:
            # Sentiment lags: shift sentiment backward (so t+1 aligns with t)
            x = df[target_col].shift(lag)
            y = df[indicator_col]
        else:
            # Contemporaneous (lag = 0)
            x = df[target_col]
            y = df[indicator_col]
            
        # Drop NaNs created by shifting or original missing values
        valid_data = pd.DataFrame({'x': x, 'y': y}).dropna()
        
        if len(valid_data) < 10:
            continue # Skip if not enough data points for statistical significance
            
        # Calculate Pearson correlation
        pearson_corr, p_pearson = stats.pearsonr(valid_data['x'], valid_data['y'])
        
        # Calculate Spearman correlation (rank-based, robust to outliers)
        spearman_corr, p_spearman = stats.spearmanr(valid_data['x'], valid_data['y'])
        
        results.append({
            'indicator': indicator_col,
            'lag_months': lag,
            'direction': 'Sentiment Leads' if lag > 0 else ('Sentiment Lags' if lag < 0 else 'Contemporaneous'),
            'pearson_corr': round(pearson_corr, 4),
            'pearson_p_value': round(p_pearson, 4),
            'spearman_corr': round(spearman_corr, 4),
            'spearman_p_value': round(p_spearman, 4),
            'sample_size': len(valid_data)
        })
        
    return results

def main():
    print(" Starting Phase 7: Correlation & Statistical Analysis...")
    
    # 1. Load Data
    print(f" Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # Ensure numeric types for correlation columns
    cols_to_check = ['sentiment_intensity', 'tourist_arrivals', 'usd_lkr_rate', 'inflation_rate']
    for col in cols_to_check:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Drop rows where BOTH sentiment and the indicator are NaN to maximize sample size per pair
    # We will handle NaNs dynamically in the lag function, but good to note
    
    indicators = ['tourist_arrivals', 'usd_lkr_rate', 'inflation_rate']
    all_results = []
    
    print("\n Calculating lagged correlations (Lags: -3 to +3 months)...")
    print("   (Positive lag = Sentiment leads the indicator; Negative lag = Sentiment lags)")
    
    for indicator in indicators:
        print(f"\n   Analyzing: {indicator}...")
        results = calculate_lagged_correlations(df, 'sentiment_intensity', indicator, max_lag=3)
        all_results.extend(results)
        
    # 2. Create Summary DataFrame
    summary_df = pd.DataFrame(all_results)
    
    # Highlight statistically significant correlations (p < 0.05)
    summary_df['is_significant'] = summary_df['pearson_p_value'] < 0.05
    
    # 3. Save to CSV
    print(f"\n Saving correlation summary to {OUTPUT_PATH}...")
    summary_df.to_csv(OUTPUT_PATH, index=False)
    
    # 4. Print Key Insights
    print("\n" + "="*60)
    print(" KEY CORRELATION INSIGHTS")
    print("="*60)
    
    for indicator in indicators:
        ind_data = summary_df[summary_df['indicator'] == indicator]
        # Find the lag with the highest absolute Pearson correlation
        best_row = ind_data.loc[ind_data['pearson_corr'].abs().idxmax()]
        
        print(f"\n {indicator.upper().replace('_', ' ')}")
        print(f"   • Strongest correlation: {best_row['pearson_corr']:.3f} (p={best_row['pearson_p_value']:.3f})")
        print(f"   • Timing: {best_row['direction']} by {abs(int(best_row['lag_months']))} month(s)")
        
        if best_row['is_significant']:
            print("   •  Statistically significant (p < 0.05)")
        else:
            print("   •  Not statistically significant at 95% confidence level")

    print("\n" + "="*60)
    print(" Phase 7 Complete! Check `correlation_summary.csv` for the full table.")
    print("="*60)

if __name__ == "__main__":
    main()