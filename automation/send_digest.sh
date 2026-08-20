#!/bin/bash
# AI Digest sender for Telegram
# Usage: ./send_digest.sh <html_file> <caption>

BOT_TOKEN="8054755692:AAGJdEcuGKWfk4MWwDXoLdh_5OMelI_h8bA"
CHAT_ID="436123763"
HTML_FILE="$1"
CAPTION="${2:-🔥 AI-Дайджест от Gavrick!}"

if [ ! -f "$HTML_FILE" ]; then
    echo "ERROR: File not found: $HTML_FILE"
    exit 1
fi

curl -s -F "chat_id=$CHAT_ID" \
  -F "document=@$HTML_FILE" \
  -F "caption=$CAPTION" \
  "https://api.telegram.org/bot$BOT_TOKEN/sendDocument" | jq -r '.ok'
