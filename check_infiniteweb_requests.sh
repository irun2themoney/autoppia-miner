#!/bin/bash
# Check recent InfiniteWeb Arena requests and responses

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🔍 CHECKING INFINITEWEB ARENA REQUESTS & RESPONSES 🔍    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "📋 Recent API Requests (Last 100 lines):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
journalctl -u autoppia-api -n 100 --no-pager | grep -E "INCOMING REQUEST|OUTGOING RESPONSE|actions|task_id" | tail -50

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Checking for Empty Actions Responses:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
journalctl -u autoppia-api -n 200 --no-pager | grep -A 20 "OUTGOING RESPONSE" | grep -E "actions|task_id|success" | head -30

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Testing API with InfiniteWeb Arena-like Request:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-login",
    "prompt": "First, authenticate with username testuser and password password123 to log in successfully.",
    "url": ""
  }' 2>&1 | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Done! Check the output above to see what's being sent/received."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
