#!/usr/bin/env python3
"""
NewsAPI Integration for Daily News Push
Fetches top headlines from NewsAPI as primary source
Falls back to Gemini web_search if needed
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

# Load API key from environment or .env file
def load_api_key():
    """Load NewsAPI key from environment or .env file"""
    # Try environment first
    api_key = os.environ.get('NEWSAPI_KEY')
    if api_key:
        return api_key
    
    # Try .env file
    env_path = '/Users/leonard/.openclaw/workspace/.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('NEWSAPI_KEY='):
                    return line.strip().split('=', 1)[1]
    
    return None

def fetch_newsapi_headlines(api_key, category='general', country='us', page_size=10):
    """Fetch top headlines from NewsAPI"""
    
    base_url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'apiKey': api_key,
        'category': category,
        'pageSize': page_size,
        'language': 'en'
    }
    
    # Build URL
    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}?{query_string}"
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'OpenClaw-DailyNews/1.0'
        })
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get('status') == 'ok':
                return data.get('articles', [])
            else:
                print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
                
    except Exception as e:
        print(f"Error fetching from NewsAPI: {e}")
        return []

def format_newsapi_article(article, index):
    """Format a single article"""
    title = article.get('title', 'No title')
    source = article.get('source', {}).get('name', 'Unknown source')
    description = article.get('description', '')
    url = article.get('url', '')
    
    # Clean up description
    if description:
        description = description[:150] + '...' if len(description) > 150 else description
    
    return f"{index}. **{title}**\n   Source: {source}\n   {description}\n"

def get_daily_news():
    """Get daily news from NewsAPI"""
    
    api_key = load_api_key()
    if not api_key:
        print("Error: NEWSAPI_KEY not found")
        return None
    
    print("Fetching news from NewsAPI...")
    
    # Fetch general world news
    articles = fetch_newsapi_headlines(api_key, category='general', page_size=10)
    
    if not articles:
        print("No articles fetched from NewsAPI")
        return None
    
    # Format the news
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M %Z")
    
    header = f"""📰 **Morning News Briefing - {date_str}**
*Source: NewsAPI (Top Headlines)*

---

🌍 **Top 10 World News - {date_str}**

"""
    
    body = ""
    for i, article in enumerate(articles[:10], 1):
        body += format_newsapi_article(article, i) + "\n"
    
    footer = f"""
---

*Powered by NewsAPI | Pushed by Adam ⚡ | {time_str}*

*News attribution required: https://newsapi.org*
"""
    
    return header + body + footer

def save_news(news_content):
    """Save news to file"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"/Users/leonard/.openclaw/workspace/daily-news-{date_str}.md"
    
    with open(filename, 'w') as f:
        f.write(news_content)
    
    return filename

def main():
    print("="*60)
    print("Daily News - NewsAPI Integration")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Get news
    news = get_daily_news()
    
    if news:
        # Save to file
        filename = save_news(news)
        print(f"\n✓ News saved to: {filename}")
        
        # Print output
        print("\n" + "="*60)
        print(news)
        print("="*60)
        print("✓ Success!")
        return 0
    else:
        print("\n✗ Failed to fetch news")
        return 1

if __name__ == "__main__":
    sys.exit(main())
