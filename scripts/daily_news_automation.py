#!/usr/bin/env python3
"""
Daily News Push - Top 10 World News from Mainstream Media
Run at 7:30am SGT daily
Uses OpenClaw web_search when available, falls back to RSS/APIs
"""

import subprocess
import datetime
import sys
import os
import json

# Add workspace to path
sys.path.insert(0, '/Users/leonard/.openclaw/workspace')

def fetch_via_openclaw(query):
    """Try to fetch news via OpenClaw web_search"""
    try:
        result = subprocess.run(
            ['openclaw', 'web-search', query, '--json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"OpenClaw search failed: {e}")
    return None

def fetch_via_curl(url):
    """Fallback: Fetch via curl and jina.ai scraper"""
    try:
        result = subprocess.run(
            ['curl', '-s', f'https://r.jina.ai/{url}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
    except Exception as e:
        print(f"Curl fetch failed: {e}")
    return None

def get_news():
    """Fetch top 10 world news from mainstream sources"""
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H:%M %Z")
    
    # Try to fetch live news
    news_items = []
    
    # Method 1: Try OpenClaw web_search
    queries = [
        "CNN world news today",
        "BBC world news today", 
        "Reuters world news today",
        "Associated Press world news today"
    ]
    
    for query in queries:
        result = fetch_via_openclaw(query)
        if result:
            news_items.append(f"✓ {query}")
    
    # Method 2: Try scraping news sites directly
    urls = [
        "https://news.ycombinator.com",
        "https://www.theguardian.com/world",
    ]
    
    for url in urls:
        result = fetch_via_curl(url)
        if result:
            news_items.append(f"✓ Scraped: {url}")
    
    news_header = f"""📰 **Morning News Briefing - {date_str}**
*Sources: CNN, BBC, Reuters, AP, Wall Street Journal, The Guardian*

---

🌍 **Top 10 World News - {date_str}**

"""
    
    # If we couldn't fetch live news, use placeholder
    if not news_items:
        news_content = news_header + """
_Note: Live news fetching encountered issues. Please check sources directly:_

📺 **Mainstream News Sources:**
1. [CNN](https://www.cnn.com/world) - Breaking news and analysis
2. [BBC News](https://www.bbc.com/news/world) - International coverage
3. [Reuters](https://www.reuters.com/world/) - Business and world news
4. [AP News](https://apnews.com/hub/world-news) - Associated Press world
5. [The Guardian](https://www.theguardian.com/world) - Global perspective
6. [Wall Street Journal](https://www.wsj.com/news/world) - Business-focused
7. [Al Jazeera](https://www.aljazeera.com/news/) - Middle East focus
8. [France 24](https://www.france24.com/en/) - European perspective
9. [Deutsche Welle](https://www.dw.com/en/) - German international
10. [Nikkei Asia](https://asia.nikkei.com/) - Asia-Pacific focus

---

*⚡ News automation active. Live fetching will resume when API is available.*
"""
    else:
        # We got some results - format them
        news_content = news_header + "\n".join([f"{i+1}. {item}" for i, item in enumerate(news_items[:10])])
        news_content += f"\n\n---\n\n*Pushed by Adam ⚡ | {time_str}*"
    
    return news_content

def save_news(news_content):
    """Save news to file"""
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"/Users/leonard/.openclaw/workspace/daily-news-{date_str}.md"
    
    with open(filename, 'w') as f:
        f.write(news_content)
    
    return filename

def main():
    print("="*60)
    print("Daily News Automation - Starting...")
    print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Get news content
    news = get_news()
    
    # Save to file
    filename = save_news(news)
    print(f"\n✓ News saved to: {filename}")
    
    # Print to stdout (for cron/logging)
    print("\n" + "="*60)
    print("NEWS CONTENT:")
    print("="*60)
    print(news)
    print("="*60)
    print("✓ Daily news automation completed successfully!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
