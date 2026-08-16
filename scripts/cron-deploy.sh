#!/bin/bash
# Cron wrapper for news archive deployment
# This script is called by the cron job to deploy digest to GitHub

export HOME=/root
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Read digest content from stdin
DIGEST_FILE="/tmp/ai-digest-$(date +%Y%m%d-%H%M%S).txt"
cat > "$DIGEST_FILE"

# Run the pipeline
python3 /root/.openclaw/workspace/news-repo/scripts/full_pipeline.py "$DIGEST_FILE" "$(date +%Y-%m-%d)" 2>&1 | tee /tmp/news-archive-deploy.log

# Cleanup
rm -f "$DIGEST_FILE"
