#!/bin/bash
# Check DigitalOcean server status

SERVER_IP="134.199.203.133"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 DigitalOcean Server Status Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Server IP: $SERVER_IP"
echo ""

# Check if server is reachable
echo "📋 Step 1: Server Connectivity"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ping -c 1 -W 2 $SERVER_IP > /dev/null 2>&1; then
    echo "   ✅ Server is reachable"
else
    echo "   ❌ Server is not reachable (may be down or firewall blocking ping)"
fi
echo ""

# Check API health
echo "📋 Step 2: API Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
HEALTH_RESPONSE=$(curl -s --max-time 5 http://$SERVER_IP:8080/health 2>&1)
if echo "$HEALTH_RESPONSE" | grep -q "healthy\|status"; then
    echo "   ✅ API is responding"
    echo "   Response: $HEALTH_RESPONSE" | head -c 200
    echo ""
else
    echo "   ❌ API is not responding"
    echo "   Error: $HEALTH_RESPONSE"
fi
echo ""

# Check API metrics
echo "📋 Step 3: API Metrics"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
METRICS_RESPONSE=$(curl -s --max-time 5 http://$SERVER_IP:8080/api/dashboard/metrics 2>&1)
if echo "$METRICS_RESPONSE" | grep -q "total_requests\|success_rate"; then
    echo "   ✅ Metrics endpoint is working"
    echo "   Metrics: $METRICS_RESPONSE" | head -c 300
    echo ""
else
    echo "   ⚠️  Metrics endpoint may not be accessible"
fi
echo ""

# Check if we can SSH (if keys are set up)
echo "📋 Step 4: SSH Access (if configured)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   To check services on server, SSH in:"
echo "   ssh root@$SERVER_IP"
echo ""
echo "   Then run:"
echo "   systemctl status autoppia-api"
echo "   systemctl status autoppia-miner"
echo "   journalctl -u autoppia-miner -n 50"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Server: $SERVER_IP"
echo "API: http://$SERVER_IP:8080"
echo "Dashboard: http://$SERVER_IP:8080/api/dashboard"
echo ""
echo "To check miner status on server:"
echo "  ssh root@$SERVER_IP 'journalctl -u autoppia-miner -n 100 | grep -i \"uid\\|registered\\|served\"'"
echo ""

