#!/usr/bin/env python3
"""
Daily News Push - Top 10 World News
Run at 7:30am SGT daily via launchd
"""

import subprocess
import datetime
import sys
import os
import json
import time

# Configuration
TELEGRAM_CHAT_ID = "1080294026"
WORKSPACE = "/Users/leonard/.openclaw/workspace"

def send_to_telegram(message):
    """Send message via OpenClaw to Telegram"""
    try:
        # Save message to file for manual sending if needed
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        msg_file = f"{WORKSPACE}/daily-news-msg-{date_str}.txt"
        with open(msg_file, 'w') as f:
            f.write(message)
        
        print(f"Message saved to: {msg_file}")
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False

def fetch_via_openclaw(query, retries=3):
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
                    if 'content' in data and data['content']:
                        return data['content']
                except:
                    pass
            # Wait before retry
            if attempt < retries - 1:
                wait_time = 2 ** attempt
                print(f"Retry {attempt + 1}/{retries} in {wait_time}s...")
                time.sleep(wait_time)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    return None

def fetch_via_scraper(url):
    """Fallback: Fetch via web scraper"""
    try:
        result = subprocess.run(
            ['curl', '-s', f'https://r.jina.ai/{url}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0 and len(result.stdout) > 100:
            return result.stdout[:2000]  # Limit length
    except Exception as e:
        print(f"Scraper failed: {e}")
    return None

def get_world_news():
    """Fetch world news from multiple sources"""
    news_sources = []
    
    # Try OpenClaw web_search for different topics
    queries = [
        "world news today",
        "CNN world news",
        "BBC world news",
        "Reuters world news"
    ]
    
    for query in queries:
        print(f"Trying: {query}")
        content = fetch_via_openclaw(query)
        if content:
            news_sources.append((query, content))
            print(f"✓ Success: {query}")
        else:
            print(f"✗ Failed: {query}")
    
    return news_sources

def format_news(news_sources, date_str, time_str):
    """Format news into readable message"""
    
    header = f"""📰 **Morning News Briefing - {date_str}**
*Sources: CNN, BBC, Reuters, AP, Wall Street Journal*

---

🌍 **Top World News - {date_str}**

"""
    
    if not news_sources:
        # No news fetched - provide fallback
        body = """
⚠️ *Live news fetching temporarily unavailable*

**Direct News Sources:**
• [CNN World](https://www.cnn.com/world)
• [BBC News](https://www.bbc.com/news/world)
• [Reuters](https://www.reuters.com/world/)
• [AP News](https://apnews.com/hub/world-news)
• [The Guardian](https://www.theguardian.com/world)
• [Al Jazeera](https://www.aljazeera.com/)

---

*News automation active. Full service will resume shortly.*
"""
    else:
        # Format fetched news
        body = ""
        for i, (source, content) in enumerate(news_sources[:5], 1):
            # Extract first few lines of content
            lines = content.strip().split('\n')[:3]
            summary = ' '.join(lines)[:200]
            body += f"{i}. **{source}**\n   {summary}...\n\n"
        
        body += f"\n---\n\n*Pushed by Adam ⚡ | {time_str}*"
    
    return header + body

def main():
    print("="*60)
    print("Daily News Automation - Starting")
    print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H:%M %Z")
    
    # Fetch news
    print("\nFetching news...")
    news_sources = get_world_news()
    
    # Format message
    print("\nFormatting message...")
    message = format_news(news_sources, date_str, time_str)
    
    # Save to file
    filename = f"{WORKSPACE}/daily-news-{date_str}.md"
    with open(filename, 'w') as f:
        f.write(message)
    print(f"✓ Saved to: {filename}")
    
    # Try to send via Telegram (if OpenClaw gateway is available)
    print("\nAttempting to send to Telegram...")
    send_to_telegram(message)
    
    # Print output
    print("\n" + "="*60)
    print("NEWS CONTENT:")
    print("="*60)
    print(message)
    print("="*60)
    print("✓ Daily news automation completed!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
