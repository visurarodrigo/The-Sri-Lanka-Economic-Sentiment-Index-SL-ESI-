import os
import time
import re
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

def extract_date_from_text(text):
    """Robustly extract dates from messy text using regex and dateutil."""
    patterns = [
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
        r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
        r'\d{4}-\d{2}-\d{2}' # ISO format fallback
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                parsed = parser.parse(match.group(0), fuzzy=True)
                if parsed.year < 2000:
                    parsed = parsed.replace(year=parsed.year + 100)
                return parsed
            except Exception:
                continue
    return None

def scrape_economynext(max_pages=150):
    """Scrape EconomyNext economy section with robust text-based date finding."""
    articles = []
    base_url = "https://economynext.com/economy/"
    
    print("\n📰 Scraping EconomyNext...")
    for page in tqdm(range(1, max_pages + 1), desc="EconomyNext Pages"):
        url = f"{base_url}page/{page}/" if page > 1 else base_url
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Failed to fetch {url}: {e}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all heading tags that contain links (these are the article titles)
        posts = soup.find_all(lambda tag: tag.name in ['h2', 'h3', 'h4', 'h5'] and tag.find('a', href=True))
        
        if not posts:
            print("ℹ️ No more articles found. Stopping.")
            break

        page_has_valid_date = False
        
        for post in posts:
            a_tag = post.find('a')
            title = a_tag.get_text(strip=True)
            link = a_tag['href']
            
            # Get the surrounding text of the parent container to find the date
            parent = post.parent
            text_content = parent.get_text(separator=' ', strip=True)
            
            pub_date = extract_date_from_text(text_content)
            
            if pub_date:
                if pub_date < START_DATE:
                    continue
                elif pub_date <= END_DATE:
                    page_has_valid_date = True
                    
                    # Create a snippet by removing the title and "X min read"
                    snippet = text_content.replace(title, "").strip()
                    snippet = re.sub(r'\d+\s*min\s*read', '', snippet, flags=re.IGNORECASE).strip()
                    snippet = snippet[:150] + "..." if len(snippet) > 150 else snippet
                    
                    articles.append({
                        "source": "EconomyNext",
                        "title": title,
                        "date": pub_date.strftime("%Y-%m-%d"),
                        "url": link,
                        "snippet": snippet
                    })
        
        # If we've collected a good amount and hit a page with no valid dates, we've gone back too far
        if not page_has_valid_date and len(articles) > 100:
            print(f"ℹ️ Reached pre-2020 content on page {page}. Stopping early to save time.")
            break
            
        time.sleep(1.0) # Be respectful to the server
        
    return articles

def scrape_dailymirror(max_pages=50):
    """Scrape Daily Mirror Business section as a reliable secondary source."""
    articles = []
    base_url = "https://www.dailymirror.lk/business"
    
    print("\n📰 Scraping Daily Mirror Business...")
    for page in tqdm(range(1, max_pages + 1), desc="Daily Mirror Pages"):
        url = f"{base_url}/{page}" if page > 1 else base_url
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Failed to fetch {url}: {e}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Daily Mirror business articles are typically in divs with class 'single-blog' or similar
        posts = soup.find_all('div', class_='single-blog') or soup.find_all('article')
        
        if not posts:
            print("ℹ️ No more articles found. Stopping.")
            break

        for post in posts:
            title_tag = post.find('h3') or post.find('h2')
            if not title_tag or not title_tag.find('a'):
                continue
                
            a_tag = title_tag.find('a')
            title = a_tag.get_text(strip=True)
            link = a_tag['href']
            if link and not link.startswith('http'):
                link = "https://www.dailymirror.lk" + link
                
            text_content = post.get_text(separator=' ', strip=True)
            pub_date = extract_date_from_text(text_content)
            
            if pub_date and START_DATE <= pub_date <= END_DATE:
                snippet = text_content.replace(title, "").strip()[:150] + "..."
                
                articles.append({
                    "source": "Daily Mirror",
                    "title": title,
                    "date": pub_date.strftime("%Y-%m-%d"),
                    "url": link,
                    "snippet": snippet
                })
        
        time.sleep(1.5)
        
    return articles

def main():
    print("🚀 Starting SL-ESI Data Collection (2020-2026)...")
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    all_articles = []
    all_articles.extend(scrape_economynext(max_pages=150))
    all_articles.extend(scrape_dailymirror(max_pages=50))
    
    df = pd.DataFrame(all_articles)
    
    if df.empty:
        print("❌ No articles collected. Check network or website structure changes.")
        return
        
    # Deduplicate based on URL
    df = df.drop_duplicates(subset=['url']).reset_index(drop=True)
    
    # Sort by date descending
    df = df.sort_values(by='date', ascending=False).reset_index(drop=True)
    
    # Save to raw CSV
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Success! Saved {len(df)} unique articles to {OUTPUT_FILE}")
    print(f"📅 Date range in data: {df['date'].min()} to {df['date'].max()}")

if __name__ == "__main__":
    main()