#!/bin/bash
# Auto News Push Script - Runs at 7:30am daily
# Sends top 5 news from: Iran war, Ukraine war, China, Singapore, World

# Get current date
DATE=$(date "+%Y-%m-%d")
TIME=$(date "+%H:%M")

echo "📰 早报新闻 - $DATE $TIME"
echo ""

# Function to send message via OpenClaw (using sessions_send or similar)
# This will be called by the cron job
