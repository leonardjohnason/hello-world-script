# Daily News Automation

## Overview
Automated daily news push at 7:30am SGT with top 10 world news from mainstream media sources.

## Sources
- CNN
- BBC
- Reuters
- Associated Press (AP)
- Wall Street Journal
- The Guardian

## Schedule
- **Time:** 7:30am SGT daily
- **Format:** Markdown with emojis and clear sections
- **Output:** Saved to workspace + can be pushed to Telegram/Discord

## Files

| File | Purpose |
|------|---------|
| `scripts/daily_news_automation.py` | Main news fetcher script |
| `scripts/daily-news-push.sh` | Bash wrapper script |
| `logs/daily-news.log` | Execution logs |
| `logs/daily-news-error.log` | Error logs |
| `daily-news-YYYY-MM-DD.md` | Daily news output files |

## How It Works

### Method: macOS LaunchAgent
The job runs via macOS launchd (more reliable than cron on macOS):

```bash
# Check if job is loaded
launchctl list | grep ai.openclaw.daily-news

# View logs
tail -f /Users/leonard/.openclaw/workspace/logs/daily-news.log

# Run manually
python3 scripts/daily_news_automation.py
```

### Manual Run
```bash
cd /Users/leonard/.openclaw/workspace
python3 scripts/daily_news_automation.py
```

## Configuration

To modify the schedule, edit:
```
~/Library/LaunchAgents/ai.openclaw.daily-news.plist
```

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/ai.openclaw.daily-news.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.daily-news.plist
```

## Future Enhancements
- [ ] Integrate with OpenClaw web_search for live news fetching
- [ ] Auto-push to Telegram/Discord
- [ ] Filter by categories (Tech, Politics, Business, etc.)
- [ ] Weekend summary edition

---

*Setup by Adam ⚡*
