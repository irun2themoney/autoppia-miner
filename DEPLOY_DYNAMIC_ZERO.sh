#!/bin/bash
# Deploy Dynamic Zero Optimizations to DigitalOcean VPS
# This script pulls latest code and restarts services

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🚀 DEPLOYING DYNAMIC ZERO OPTIMIZATIONS 🚀              ║"
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
sleep 5

echo ""
echo "✅ Checking service status..."
systemctl status autoppia-api --no-pager | head -15

echo ""
echo "🧪 Testing API endpoint..."
curl -s -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-dynamic-zero",
    "prompt": "Search for restaurants",
    "url": "http://84.247.180.192:8003/?seed=123"
  }' | python3 -m json.tool | head -20

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Dynamic Zero optimizations deployed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Key improvements:"
echo "  • Enhanced action templates for D1-D4 complexity"
echo "  • Multiple fallback selectors for dynamic HTML"
echo "  • Pop-up detection and handling"
echo "  • Optimized for completion + precision (WTA rules)"
echo "  • Fixed Chutes API authentication"
echo ""
echo "🌐 API Endpoint: http://134.199.203.133:8080"
echo "📈 Monitor logs: journalctl -u autoppia-api -f"
echo ""

