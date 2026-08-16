#!/bin/bash
# Wrapper script for cron - generates HTML pages from digest and deploys to GitHub

set -e

REPO_DIR="/root/.openclaw/workspace/news-repo"
DIGEST_FILE="/tmp/ai-digest-latest.txt"
DATE="$1"

if [ -z "$DATE" ]; then
    DATE=$(date +%Y-%m-%d)
fi

# Write digest from stdin to file
cat > "$DIGEST_FILE"

# Generate pages and push
cd "$REPO_DIR"
python3 scripts/generate_news_pages.py "$DIGEST_FILE" "$DATE"

echo "✅ News archive updated for $DATE"
