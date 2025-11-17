#!/bin/bash
# Monitor Chutes API usage on the remote server

SERVER="root@134.199.203.133"
PASSWORD="DigitalOcean4life"

echo "🔍 Monitoring Chutes API usage..."
echo "Press Ctrl+C to stop"
echo "=" | head -c 60 && echo ""

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" \
  "journalctl -u autoppia-api -f --no-pager | grep -i -E 'chutes|llm|qwen|template|rate|429|using|generated'"

