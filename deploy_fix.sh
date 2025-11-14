#!/bin/bash
# Deploy the empty actions fix to VPS

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🔧 DEPLOYING EMPTY ACTIONS FIX TO VPS 🔧                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd /opt/autoppia-miner

echo "📥 Pulling latest code..."
git pull origin main

echo ""
echo "🔄 Restarting API service..."
systemctl restart autoppia-api

echo ""
echo "⏳ Waiting for service to start..."
sleep 3

echo ""
echo "📊 Checking service status..."
systemctl status autoppia-api --no-pager | head -15

echo ""
echo "🧪 Testing API with sample request..."
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-fix",
    "prompt": "Login with username test and password test123",
    "url": ""
  }' | python3 -m json.tool

echo ""
echo "✅ Fix deployed! Check the response above - it should have actions array with items."

