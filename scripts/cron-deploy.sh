#!/bin/bash
# Cron wrapper for news archive deployment
# This script is called by the cron job to deploy digest to GitHub

export HOME=/root
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

DIGEST_FILE="/tmp/ai-digest-$(date +%Y%m%d-%H%M%S).txt"

# Try to read digest from stdin first, then fallback to latest digest file
if [ -t 0 ]; then
    # stdin is a terminal (empty) — use latest digest file
    LATEST_DIGEST=$(ls -t /tmp/ai-digest-latest.txt /tmp/ai-digest-*.txt 2>/dev/null | head -1)
    if [ -n "$LATEST_DIGEST" ] && [ -f "$LATEST_DIGEST" ]; then
        cp "$LATEST_DIGEST" "$DIGEST_FILE"
        echo "Using digest: $LATEST_DIGEST"
    else
        echo "Error: No digest file found and stdin is empty"
        exit 1
    fi
else
    # stdin has data — read it
    cat > "$DIGEST_FILE"
fi

# Run the pipeline
python3 /root/.openclaw/workspace/news-repo/scripts/full_pipeline.py "$DIGEST_FILE" "$(date +%Y-%m-%d)" 2>&1 | tee /tmp/news-archive-deploy.log

# Cleanup
rm -f "$DIGEST_FILE"
