import os
import pandas as pd
import numpy as np
from transformers import pipeline
from tqdm import tqdm
from pathlib import Path

# Try to import torch to check for GPU acceleration, fallback to CPU if not available
try:
    import torch
    device = 0 if torch.cuda.is_available() else -1
except ImportError:
    device = -1 # Fallback to CPU

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_FILE = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'news_headlines_clean.csv'
OUTPUT_FILE = PROJECT_ROOT / 'src' / 'data' / 'processed' / 'sl_esi_monthly_index.csv'
MODEL_NAME = "ProsusAI/finbert" # State-of-the-art for financial/economic text

def main():
    print("Starting SL-ESI NLP Sentiment Scoring...")
    
    # 1. Load cleaned data
    print(f"Loading data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    print(f"   Loaded {len(df)} articles.")
    
    # 2. Initialize Sentiment Pipeline
    print(f"Loading {MODEL_NAME} model (this may take a minute to download on first run)...")
    sentiment_pipeline = pipeline(
        "sentiment-analysis", 
        model=MODEL_NAME, 
        device=device,
        truncation=True,
        max_length=512 # FinBERT max context window
    )
    
    # 3. Batch Processing for Efficiency
    print("Analyzing sentiment in batches...")
    batch_size = 32
    sentiments = []
    
    texts = df['text'].fillna("").astype(str).tolist()
    
    for i in tqdm(range(0, len(texts), batch_size), desc="Processing Batches"):
        batch = texts[i:i + batch_size]
        # FinBERT returns [{'label': 'positive'/'negative'/'neutral', 'score': 0.99}]
        results = sentiment_pipeline(batch)
        
        for res in results:
            label = res['label']
            score = res['score']
            
            # Convert to a continuous -1 to 1 scale
            if label == 'positive':
                sentiments.append(score)
            elif label == 'negative':
                sentiments.append(-score)
            else:
                sentiments.append(0.0) # Neutral
                
    # 4. Attach scores to DataFrame
    print("📎 Attaching sentiment scores to dataset...")
    df['sentiment_score'] = sentiments
    
    # 5. Aggregate to Monthly Index
    print("Aggregating to monthly SL-ESI index...")
    monthly_df = df.groupby('year_month').agg(
        article_count=('date', 'count'),
        mean_sentiment=('sentiment_score', 'mean'),
        std_sentiment=('sentiment_score', 'std') # Measures consensus vs. polarization
    ).reset_index()
    
    # Fill NaN std with 0 (happens if a month has only 1 article)
    monthly_df['std_sentiment'] = monthly_df['std_sentiment'].fillna(0)
    
    # Create "Sentiment Intensity": Mean Sentiment * log(Article Count)
    # This ensures months with massive news coverage (e.g., crisis peaks) have a stronger signal
    monthly_df['sentiment_intensity'] = monthly_df['mean_sentiment'] * np.log1p(monthly_df['article_count'])
    
    # Sort chronologically
    monthly_df = monthly_df.sort_values('year_month').reset_index(drop=True)
    
    # 6. Save to CSV
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    monthly_df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\nSuccess! Saved monthly index to {OUTPUT_FILE}")
    print("Preview of the SL-ESI Index (First 10 Months):")
    print(monthly_df.head(10).to_string(index=False))

if __name__ == "__main__":
    main()