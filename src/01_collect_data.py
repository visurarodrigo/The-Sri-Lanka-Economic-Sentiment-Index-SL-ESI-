import os
import time
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import datetime
from tqdm import tqdm

"""
01_collect_data.py
==================
This script scrapes news headlines, dates, and snippets from EconomyNext.com.
It targets the 'Economy' and 'Business' sections to gather a dataset for the
Sri Lanka Economic Sentiment Index (SL-ESI) covering the period 2020-2026.

The process involves:
1. Iterating through paginated archive pages.
2. Extracting article titles, links, and publication dates from the HTML.
3. Filtering articles by the specified date range.
4. Cleaning and deduplicating the results.
5. Saving the raw data to a CSV file.
"""

# Configuration
# Define the date range for data collection to capture the pre-crisis, crisis, and recovery periods
START_DATE = datetime(2020, 1, 1)
END_DATE = datetime(2026, 12, 31)
OUTPUT_FILE = "data/raw/news_headlines_raw.csv"
# Use a browser-like User-Agent to avoid being blocked by the server
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def extract_date_from_text(text):
    """
    Robustly extract dates from messy text using regex and dateutil.

    Args:
        text (str): The text content around the headline where the date is typically located.

    Returns:
        datetime or None: The parsed date if found and valid, otherwise None.
    """
    # Define patterns to match common date formats used on the website
    patterns = [
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}', # e.g., "January 1, 2023"
        r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', # e.g., "1 January 2023"
        r'\d{4}-\d{2}-\d{2}' # ISO format fallback (e.g., "2023-01-01")
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                # Use dateutil.parser.parse for flexible parsing of the matched string
                parsed = parser.parse(match.group(0), fuzzy=True)
                # Handle edge cases where parser might misinterpret years (e.g., 2-digit years)
                if parsed.year < 2000:
                    parsed = parsed.replace(year=parsed.year + 100)
                return parsed
            except Exception:
                continue
    return None

def fetch_with_retry(url, max_retries=3):
    """
    Fetch a URL with exponential backoff retry logic for 500/429 errors.

    Args:
        url (str): The target URL to fetch.
        max_retries (int): Number of times to attempt the request before giving up.

    Returns:
        requests.Response or None: The response object if successful, else None.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status() # Raise exception for 4xx/5xx errors
            return response
        except requests.exceptions.HTTPError as e:
            # Handle Rate Limiting (429) and Server Errors (500, 502, 503, 504)
            if response.status_code in [429, 500, 502, 503, 504]:
                # Exponential backoff: 2^0 + 2, 2^1 + 2, 2^2 + 2...
                wait_time = (2 ** attempt) + 2
                print(f"\n⚠️ Server error {response.status_code} on {url}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                # For other HTTP errors (e.g., 404), skip the page immediately
                print(f"\n⚠️ HTTP Error {response.status_code} on {url}. Skipping.")
                return None
        except requests.exceptions.RequestException as e:
            # Handle network timeouts or DNS issues
            print(f"\n⚠️ Request failed on {url}: {e}. Retrying...")
            time.sleep(3)
    print(f"❌ Failed to fetch {url} after {max_retries} retries. Skipping.")
    return None

def scrape_section(section_name, base_url, max_pages=150):
    """
    Generic scraper for any EconomyNext section.

    Args:
        section_name (str): Name of the section (for logging and source labeling).
        base_url (str): The base URL for the section.
        max_pages (int): Limit on how many pages to scrape to prevent infinite loops.

    Returns:
        list: A list of dictionaries containing article data.
    """
    articles = []
    print(f"\n📰 Scraping EconomyNext: {section_name} (Target: 2020-2026)...")

    # Iterate through pages using a progress bar
    for page in tqdm(range(1, max_pages + 1), desc=f"{section_name} Pages"):
        # Handle pagination: page 1 is the base URL, subsequent pages use /page/N/
        url = f"{base_url}page/{page}/" if page > 1 else base_url

        response = fetch_with_retry(url)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all heading tags that contain a link (typically the headlines)
        posts = soup.find_all(lambda tag: tag.name in ['h2', 'h3', 'h4', 'h5'] and tag.find('a', href=True))

        if not posts:
            print(f"ℹ️ No more articles found in {section_name}. Stopping.")
            break

        page_has_valid_date = False

        for post in posts:
            a_tag = post.find('a')
            title = a_tag.get_text(strip=True)
            link = a_tag['href']

            # The date is often in the parent container or nearby text, not inside the <a> tag
            parent = post.parent
            text_content = parent.get_text(separator=' ', strip=True)
            pub_date = extract_date_from_text(text_content)

            if pub_date:
                # Stop collecting if we go before the start date
                if pub_date < START_DATE:
                    continue
                # Keep collecting if within the target date range
                elif pub_date <= END_DATE:
                    page_has_valid_date = True

                    # Extract a snippet by removing the title from the surrounding text
                    snippet = text_content.replace(title, "").strip()
                    # Clean up common noise like "5 min read"
                    snippet = re.sub(r'\d+\s*min\s*read', '', snippet, flags=re.IGNORECASE).strip()
                    # Truncate snippet for consistency
                    snippet = snippet[:150] + "..." if len(snippet) > 150 else snippet

                    articles.append({
                        "source": f"EconomyNext ({section_name})",
                        "title": title,
                        "date": pub_date.strftime("%Y-%m-%d"),
                        "url": link,
                        "snippet": snippet
                    })

        # Early exit condition:
        # If we've already collected a significant number of articles and a whole page
        # contains no articles within the target date range, we've likely reached the end.
        if not page_has_valid_date and len(articles) > 2000:
            print(f"\nℹ️ Reached pre-2020 content in {section_name}. Stopping early.")
            break

        time.sleep(1.0) # Respectful delay to avoid triggering rate limits

    return articles

def main():
    """Main execution flow for data collection."""
    print("🚀 Starting SL-ESI Data Collection (2020-2026)...")
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    all_articles = []
    # Scrape both Economy and Business sections to ensure we capture the full 2022 crisis arc
    # We use a higher max_pages for these sections to ensure deep coverage
    all_articles.extend(scrape_section("Economy", "https://economynext.com/economy/", max_pages=300))
    all_articles.extend(scrape_section("Business", "https://economynext.com/business/", max_pages=300))

    # Convert the list of dictionaries to a pandas DataFrame for easy manipulation
    df = pd.DataFrame(all_articles)

    if df.empty:
        print("❌ No articles collected.")
        return

    # Deduplicate based on URL since some articles may appear in both Economy and Business sections
    df = df.drop_duplicates(subset=['url']).reset_index(drop=True)

    # Sort by date descending to have the most recent news first
    df = df.sort_values(by='date', ascending=False).reset_index(drop=True)

    # Save the cleaned dataset to a CSV file for use in subsequent analysis (02_preprocess_data.py)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Success! Saved {len(df)} unique articles to {OUTPUT_FILE}")
    print(f"📅 Date range in data: {df['date'].min()} to {df['date'].max()}")

if __name__ == "__main__":
    main()
