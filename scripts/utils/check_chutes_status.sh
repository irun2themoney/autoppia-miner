#!/bin/bash
# Check current Chutes API status

SERVER="root@134.199.203.133"
PASSWORD="DigitalOcean4life"

echo "📊 Checking Chutes API Status..."
echo "=" | head -c 60 && echo ""

# Check recent logs for Chutes activity
echo "Recent Chutes activity (last 2 minutes):"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" \
  "journalctl -u autoppia-api --since '2 minutes ago' --no-pager | grep -i -E 'chutes|llm|qwen|template|rate|429' | tail -20"

echo ""
echo "API Health:"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" \
  "curl -s http://localhost:8080/health | python3 -m json.tool"

echo ""
echo "💡 To monitor in real-time, run: ./monitor_chutes.sh"

