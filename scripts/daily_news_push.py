#!/usr/bin/env python3
"""
Daily News Push - Top 10 World News
Uses NewsAPI as primary source, Gemini as backup
Run at 7:30am SGT daily via launchd
"""

import subprocess
import datetime
import sys
import os
import json
import time
import urllib.request
import urllib.parse

# Configuration
WORKSPACE = "/Users/leonard/.openclaw/workspace"

def load_newsapi_key():
    """Load NewsAPI key from .env file"""
    env_path = f'{WORKSPACE}/.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('NEWSAPI_KEY='):
                    return line.strip().split('=', 1)[1]
    return None

def fetch_newsapi():
    """Fetch news from NewsAPI"""
    api_key = load_newsapi_key()
    if not api_key:
        return None
    
    try:
        url = f'https://newsapi.org/v2/top-headlines?apiKey={api_key}&category=general&pageSize=10&language=en'
        req = urllib.request.Request(url, headers={'User-Agent': 'OpenClaw-DailyNews/1.0'})
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get('status') == 'ok' and data.get('articles'):
                articles = data['articles'][:10]
                news_lines = []
                for i, article in enumerate(articles, 1):
                    title = article.get('title', 'No title')
                    source = article.get('source', {}).get('name', 'Unknown')
                    desc = article.get('description', '')[:100]
                    news_lines.append(f"{i}. **{title}**\n   {source} - {desc}...")
                return "\n\n".join(news_lines)
    except Exception as e:
        print(f"NewsAPI error: {e}")
    
    return None

def fetch_via_openclaw(query, retries=2):
    """Fetch news via OpenClaw web_search with retries"""
    for attempt in range(retries):
        try:
            result = subprocess.run(
                ['openclaw', 'web-search', query, '--count', '5'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    content = data.get('content', '')
                    if content and 'No response' not in content and len(content) > 200:
                        return content[:1500]
                except:
                    pass
            if attempt < retries - 1:
                time.sleep(2)
        except Exception as e:
            print(f"OpenClaw attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2)
    return None

def get_daily_news():
    """Get daily news - NewsAPI first, then OpenClaw fallback"""
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H:%M %Z")
    
    header = f"""📰 **Morning News Briefing - {date_str}**
*Sources: NewsAPI, CNN, BBC, Reuters*

---

🌍 **Top 10 World News - {date_str}**

"""
    
    # Try NewsAPI first
    print("Trying NewsAPI...")
    news_content = fetch_newsapi()
    source = "NewsAPI"
    
    # If NewsAPI fails, try OpenClaw
    if not news_content:
        print("NewsAPI failed, trying OpenClaw...")
        queries = ["world news today", "CNN world news"]
        for query in queries:
            content = fetch_via_openclaw(query)
            if content:
                news_content = content
                source = "OpenClaw/Gemini"
                break
    
    # Format the news
    if news_content:
        body = news_content
    else:
        body = """⚠️ *Live news temporarily unavailable*

**Check these sources directly:**
• [CNN World](https://www.cnn.com/world)
• [BBC News](https://www.bbc.com/news/world)
• [Reuters](https://www.reuters.com/world/)
• [AP News](https://apnews.com/hub/world-news)
"""
        source = "Fallback Links"
    
    footer = f"""

---

*Source: {source} | Pushed by Adam ⚡ | {time_str}*
"""
    
    if source == "NewsAPI":
        footer += "\n*Powered by NewsAPI: https://newsapi.org*"
    
    return header + body + footer

def save_news(news_content):
    """Save news to file"""
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{WORKSPACE}/daily-news-{date_str}.md"
    
    with open(filename, 'w') as f:
        f.write(news_content)
    
    return filename

def main():
    print("="*60)
    print("Daily News Automation - Starting")
    print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Get news
    news = get_daily_news()
    
    # Save to file
    filename = save_news(news)
    print(f"\n✓ News saved to: {filename}")
    
    # Print output
    print("\n" + "="*60)
    print("NEWS CONTENT:")
    print("="*60)
    print(news)
    print("="*60)
    print("✓ Daily news automation completed!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
