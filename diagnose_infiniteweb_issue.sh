#!/bin/bash
# Comprehensive diagnostic script for InfiniteWeb Arena communication issues

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🔍 DIAGNOSING INFINITEWEB ARENA COMMUNICATION ISSUE 🔍   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd /opt/autoppia-miner

echo "📥 Step 1: Pulling latest code..."
git pull origin main

echo ""
echo "🔄 Step 2: Restarting API service..."
systemctl restart autoppia-api
sleep 5

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Step 3: Checking API Service Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
systemctl status autoppia-api --no-pager | head -15

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Step 4: Testing API Accessibility (Local)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing /health endpoint..."
curl -s http://localhost:8080/health | python3 -m json.tool || echo "❌ Health check failed"

echo ""
echo "Testing /solve_task endpoint..."
curl -s -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "diagnostic-test",
    "prompt": "Test prompt",
    "url": ""
  }' | python3 -m json.tool | head -30 || echo "❌ solve_task failed"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔥 Step 5: Checking Firewall (UFW)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ufw status | grep -E "8080|Status" || echo "UFW not active or port 8080 not configured"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 Step 6: Checking Network Listeners"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
netstat -tlnp | grep 8080 || ss -tlnp | grep 8080 || echo "Port 8080 not listening"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Step 7: Recent API Logs (Last 50 lines)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
journalctl -u autoppia-api -n 50 --no-pager | tail -50

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Step 8: Checking for InfiniteWeb Arena Requests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Searching for requests from InfiniteWeb Arena IPs..."
journalctl -u autoppia-api -n 500 --no-pager | grep -E "🌐|REQUEST|84.247.180" | tail -20 || echo "No InfiniteWeb Arena requests found in recent logs"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Step 9: Official Autoppia Resources"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 Documentation: https://luxit.gitbook.io/autoppia-docs"
echo "📦 GitHub Repo: https://github.com/autoppia/autoppia_web_agents_subnet"
echo "🌐 InfiniteWeb Arena: https://infinitewebarena.autoppia.com/"
echo ""
echo "⚠️  IMPORTANT: Check the official repository for:"
echo "   1. Exact API endpoint InfiniteWeb Arena uses"
echo "   2. Required response format"
echo "   3. Any authentication or headers required"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Diagnostic Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next Steps:"
echo "1. Review the logs above to see if InfiniteWeb Arena requests are reaching the API"
echo "2. Check the official Autoppia GitHub repository for API specification"
echo "3. Verify DigitalOcean firewall allows port 8080 from all IPs"
echo "4. Test the API from an external location to verify accessibility"
echo ""

