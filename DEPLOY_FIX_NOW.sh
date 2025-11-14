#!/bin/bash
# Complete deployment script - copy and paste this entire block on your VPS

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🔧 DEPLOYING EMPTY ACTIONS FIX TO VPS 🔧                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd /opt/autoppia-miner

echo "📥 Step 1: Pulling latest code..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed. Check your connection."
    exit 1
fi

echo ""
echo "✅ Code updated successfully"
echo ""

echo "🔄 Step 2: Restarting API service..."
systemctl restart autoppia-api

echo ""
echo "⏳ Step 3: Waiting for service to start..."
sleep 5

echo ""
echo "📊 Step 4: Checking service status..."
if systemctl is-active --quiet autoppia-api; then
    echo "✅ API service is running!"
    systemctl status autoppia-api --no-pager | head -10
else
    echo "❌ API service failed to start. Checking logs..."
    journalctl -u autoppia-api -n 30 --no-pager
    exit 1
fi

echo ""
echo "🧪 Step 5: Testing API with sample request (no URL)..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-fix",
    "prompt": "Login with username test and password test123",
    "url": ""
  }')

echo "$TEST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$TEST_RESPONSE"

# Check if actions array has items
ACTION_COUNT=$(echo "$TEST_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('actions', [])))" 2>/dev/null || echo "0")

echo ""
if [ "$ACTION_COUNT" -gt "0" ]; then
    echo "✅ SUCCESS! API returned $ACTION_COUNT actions (fix is working!)"
else
    echo "⚠️  WARNING: API returned 0 actions. Check logs above."
fi

echo ""
echo "🧪 Step 6: Testing API with sample request (with URL)..."
TEST_RESPONSE2=$(curl -s -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-fix-2",
    "prompt": "Search for movies",
    "url": "https://example.com"
  }')

echo "$TEST_RESPONSE2" | python3 -m json.tool 2>/dev/null || echo "$TEST_RESPONSE2"

ACTION_COUNT2=$(echo "$TEST_RESPONSE2" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('actions', [])))" 2>/dev/null || echo "0")

echo ""
if [ "$ACTION_COUNT2" -gt "0" ]; then
    echo "✅ SUCCESS! API returned $ACTION_COUNT2 actions with URL (fix is working!)"
else
    echo "⚠️  WARNING: API returned 0 actions with URL."
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        ✅ DEPLOYMENT COMPLETE! ✅                             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 API Endpoint: http://134.199.203.133:8080"
echo ""
echo "Next: Test in InfiniteWeb Arena to verify actions are being returned!"

