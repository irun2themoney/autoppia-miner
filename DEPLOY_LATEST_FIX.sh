#!/bin/bash
# Deploy latest code with response validation fix

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🚀 DEPLOYING LATEST FIX WITH RESPONSE VALIDATION 🚀     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd /opt/autoppia-miner

echo "📥 Step 1: Pulling latest code..."
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
echo "🧪 Step 5: Testing API with sample request..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-validation",
    "prompt": "Login with username test and password test123",
    "url": ""
  }')

echo "$TEST_RESPONSE" | python3 -m json.tool

# Check action count
ACTION_COUNT=$(echo "$TEST_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('actions', [])))" 2>/dev/null || echo "0")

echo ""
if [ "$ACTION_COUNT" -gt "0" ]; then
    echo "✅ SUCCESS! API returned $ACTION_COUNT actions"
else
    echo "❌ ERROR: API returned 0 actions"
fi

echo ""
echo "📋 Step 6: Recent logs (last 30 lines)..."
journalctl -u autoppia-api -n 30 --no-pager | tail -20

echo ""
echo "✅ Deployment complete!"

