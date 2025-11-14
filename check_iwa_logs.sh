#!/bin/bash
# Check logs for InfiniteWeb Arena requests

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🔍 CHECKING LOGS FOR INFINITEWEB ARENA REQUESTS 🔍      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd /opt/autoppia-miner

echo "📥 Step 1: Pulling latest code with detailed logging..."
git pull origin main

echo ""
echo "🔄 Step 2: Restarting API service..."
systemctl restart autoppia-api

echo ""
echo "⏳ Step 3: Waiting for service to start..."
sleep 5

echo ""
echo "📊 Step 4: Checking service status..."
systemctl status autoppia-api --no-pager | head -10

echo ""
echo "📋 Step 5: Recent API logs (last 100 lines, filtered)..."
journalctl -u autoppia-api -n 100 --no-pager | grep -E "Received task|Task prompt|Task URL|Full request|Classified|Template generated|actions|Returning response|Error|error|Exception" | tail -50

echo ""
echo "📋 Step 6: ALL recent logs (last 50 lines, no filter)..."
journalctl -u autoppia-api -n 50 --no-pager | tail -30

echo ""
echo "🧪 Step 7: Testing API with InfiniteWeb Arena-like request..."
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-iwa-debug",
    "prompt": "First, authenticate with username test and password password123 to log in successfully.",
    "url": ""
  }' | python3 -m json.tool

echo ""
echo "📋 Step 8: Logs after test request..."
sleep 2
journalctl -u autoppia-api -n 20 --no-pager | grep -E "Received task|Task prompt|actions|Returning response"

echo ""
echo "✅ Done! Review the logs above to see what's happening."

