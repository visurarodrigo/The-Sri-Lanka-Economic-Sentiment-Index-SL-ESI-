import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import datetime
from tqdm import tqdm

# Configuration
START_DATE = datetime(2020, 1, 1)
END_DATE = datetime(2026, 12, 31)
OUTPUT_FILE = "data/raw/news_headlines_raw.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def parse_date_safely(date_str):
    """Attempt to parse various date formats found in news sites."""
    try:
        # Fuzzy=True helps handle messy strings like "Published: May 15, 2022"
        parsed = parser.parse(date_str, fuzzy=True)
        # Handle 2-digit years if parser defaults to 1900s
        if parsed.year < 2000:
            parsed = parsed.replace(year=parsed.year + 100)
        return parsed
    except Exception:
        return None

def scrape_economynext(max_pages=50):
    """Scrape EconomyNext economy section."""
    articles = []
    base_url = "https://economynext.com/economy/"
    
    print("\n Scraping EconomyNext...")
    for page in tqdm(range(1, max_pages + 1), desc="EconomyNext Pages"):
        url = f"{base_url}page/{page}/" if page > 1 else base_url
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Failed to fetch {url}: {e}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        posts = soup.find_all('article') # EconomyNext uses <article> tags for posts
        
        if not posts:
            print("ℹ️ No more articles found. Stopping.")
            break

        page_has_valid_date = False
        
        for post in posts:
            title_tag = post.find('h2') or post.find('h3')
            title = title_tag.get_text(strip=True) if title_tag else "No Title"
            
            link_tag = post.find('a', href=True)
            link = link_tag['href'] if link_tag else "No Link"
            
            # EconomyNext usually has date in a <time> tag or specific class
            date_tag = post.find('time') or post.find(class_='entry-date')
            date_str = date_tag.get_text(strip=True) if date_tag else ""
            
            pub_date = parse_date_safely(date_str)
            
            if pub_date:
                if pub_date < START_DATE:
                    # Since pages are chronological, if we hit pre-2020, we can stop entirely
                    continue 
                elif pub_date <= END_DATE:
                    page_has_valid_date = True
                    
                    # Optional: Get a short snippet for context
                    snippet_tag = post.find(class_='entry-summary') or post.find('p')
                    snippet = snippet_tag.get_text(strip=True)[:150] if snippet_tag else ""
                    
                    articles.append({
                        "source": "EconomyNext",
                        "title": title,
                        "date": pub_date.strftime("%Y-%m-%d"),
                        "url": link,
                        "snippet": snippet
                    })
        
        if not page_has_valid_date and len(articles) > 0:
            # Heuristic: if a whole page has no valid dates in our range, we've likely gone too far back
            break
            
        time.sleep(1.5) # Be respectful to the server
        
    return articles

def scrape_daily_ft(max_pages=30):
    """Scrape Daily FT business section."""
    articles = []
    base_url = "https://www.ft.lk/business/"
    
    print("\n📰 Scraping Daily FT...")
    for page in tqdm(range(1, max_pages + 1), desc="Daily FT Pages"):
        url = f"{base_url}{page}" if page > 1 else base_url
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Failed to fetch {url}: {e}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        # Daily FT structure: articles are often in divs with specific classes or standard post formats
        posts = soup.find_all('div', class_='col-sm-4') or soup.find_all('article')
        
        if not posts:
            print("ℹ️ No more articles found. Stopping.")
            break

        for post in posts:
            title_tag = post.find('h3') or post.find('h4')
            title = title_tag.get_text(strip=True) if title_tag else "No Title"
            
            link_tag = post.find('a', href=True)
            link = link_tag['href'] if link_tag else "No Link"
            if link and not link.startswith('http'):
                link = "https://www.ft.lk" + link # Make absolute
                
            date_tag = post.find(class_='date') or post.find('span', string=lambda text: text and '202' in text)
            date_str = date_tag.get_text(strip=True) if date_tag else ""
            
            pub_date = parse_date_safely(date_str)
            
            if pub_date and START_DATE <= pub_date <= END_DATE:
                snippet_tag = post.find('p')
                snippet = snippet_tag.get_text(strip=True)[:150] if snippet_tag else ""
                
                articles.append({
                    "source": "Daily FT",
                    "title": title,
                    "date": pub_date.strftime("%Y-%m-%d"),
                    "url": link,
                    "snippet": snippet
                })
        
        time.sleep(2.0) # Daily FT may have stricter rate limits
        
    return articles

def main():
    print("Starting SL-ESI Data Collection (2020-2026)...")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Collect data
    all_articles = []
    all_articles.extend(scrape_economynext(max_pages=40))
    all_articles.extend(scrape_daily_ft(max_pages=30))
    
    # Create DataFrame and clean
    df = pd.DataFrame(all_articles)
    
    if df.empty:
        print("No articles collected. Check network or website structure changes.")
        return
        
    # Drop duplicates based on URL
    df = df.drop_duplicates(subset=['url']).reset_index(drop=True)
    
    # Sort by date descending
    df = df.sort_values(by='date', ascending=False).reset_index(drop=True)
    
    # Save to raw CSV
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSuccess! Saved {len(df)} unique articles to {OUTPUT_FILE}")
    print(f"Date range in data: {df['date'].min()} to {df['date'].max()}")

if __name__ == "__main__":
    main()