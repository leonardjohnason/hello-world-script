#!/usr/bin/env python3
"""
Daily News Push - Top 10 World News from Mainstream Media
Run at 7:30am SGT daily
"""

import subprocess
import datetime
import sys
import os

# Add workspace to path
sys.path.insert(0, '/Users/leonard/.openclaw/workspace')

def get_news():
    """Fetch top 10 world news from mainstream sources"""
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H:%M %Z")
    
    news_header = f"""📰 **Morning News Briefing - {date_str}**
*Sources: CNN, BBC, Reuters, AP, Wall Street Journal, The Guardian*

---

"""
    
    # In a real implementation, this would call web_search
    # For now, we create a template
    
    news_content = news_header + f"""
🌍 **Top 10 World News - {date_str}**

1. **[Headline 1]** - Source
2. **[Headline 2]** - Source
3. **[Headline 3]** - Source
4. **[Headline 4]** - Source
5. **[Headline 5]** - Source
6. **[Headline 6]** - Source
7. **[Headline 7]** - Source
8. **[Headline 8]** - Source
9. **[Headline 9]** - Source
10. **[Headline 10]** - Source

---

*Pushed by Adam ⚡ | {time_str}*
"""
    
    return news_content

def save_news(news_content):
    """Save news to file"""
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"/Users/leonard/.openclaw/workspace/daily-news-{date_str}.md"
    
    with open(filename, 'w') as f:
        f.write(news_content)
    
    return filename

def main():
    print("Fetching daily news...")
    
    # Get news content
    news = get_news()
    
    # Save to file
    filename = save_news(news)
    print(f"News saved to: {filename}")
    
    # Print to stdout (for cron logging)
    print("\n" + "="*50)
    print(news)
    print("="*50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
