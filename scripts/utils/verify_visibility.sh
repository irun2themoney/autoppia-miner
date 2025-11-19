#!/bin/bash
# Verify miner visibility to validators
# Checks axon status, API health, and recent validator activity

set -e

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

API_PORT="${API_PORT:-8080}"
AXON_PORT="${AXON_PORT:-8091}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Verifying Miner Visibility to Validators"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get external IP
echo "📋 Step 1: Checking external IP..."
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")
echo "   External IP: $EXTERNAL_IP"
echo ""

# Check if API service is running
echo "📋 Step 2: Checking API service status..."
if systemctl is-active --quiet autoppia-api 2>/dev/null; then
    echo "   ✅ API service is running"
else
    echo "   ❌ API service is NOT running!"
    echo "   Start with: sudo systemctl start autoppia-api"
    echo ""
fi
echo ""

# Check if miner service is running
echo "📋 Step 3: Checking miner service status..."
if systemctl is-active --quiet autoppia-miner 2>/dev/null; then
    echo "   ✅ Miner service is running"
else
    echo "   ❌ Miner service is NOT running!"
    echo "   Start with: sudo systemctl start autoppia-miner"
    echo ""
fi
echo ""

# Test API health endpoint
echo "📋 Step 4: Testing API health endpoint..."
if curl -s -f http://localhost:$API_PORT/health > /dev/null 2>&1; then
    echo "   ✅ API is responding on port $API_PORT"
    echo ""
    echo "   Health response:"
    curl -s http://localhost:$API_PORT/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:$API_PORT/health
    echo ""
else
    echo "   ❌ API is not responding on port $API_PORT"
    echo "   Check logs: journalctl -u autoppia-api -n 50"
    echo ""
fi
echo ""

# Check if axon port is listening
echo "📋 Step 5: Checking if axon port is listening..."
if netstat -tuln 2>/dev/null | grep -q ":$AXON_PORT " || ss -tuln 2>/dev/null | grep -q ":$AXON_PORT "; then
    echo "   ✅ Axon is listening on port $AXON_PORT"
else
    echo "   ❌ Axon is NOT listening on port $AXON_PORT"
    echo "   Check miner logs: journalctl -u autoppia-miner -n 50"
    echo ""
fi
echo ""

# Check firewall status for required ports
echo "📋 Step 6: Checking firewall rules..."
if command -v ufw &> /dev/null; then
    echo "   UFW Status:"
    ufw status | grep -E "$API_PORT|$AXON_PORT" || echo "   ⚠️  Ports may not be open in UFW"
elif command -v firewall-cmd &> /dev/null; then
    echo "   Firewalld Status:"
    firewall-cmd --list-ports 2>/dev/null | grep -E "$API_PORT|$AXON_PORT" || echo "   ⚠️  Ports may not be open in firewalld"
else
    echo "   ⚠️  No firewall detected (ufw/firewalld)"
fi
echo ""

# Check recent miner logs for validator requests
echo "📋 Step 7: Checking recent validator activity..."
echo ""
echo "   Recent miner logs (looking for 'Processing task' or validator requests):"
echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if journalctl -u autoppia-miner -n 50 --no-pager 2>/dev/null | grep -i "processing\|validator\|task\|synapse" | tail -10; then
    echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   ✅ Found recent activity in logs"
else
    echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   ⚠️  No recent validator requests found in logs"
    echo ""
    echo "   This could mean:"
    echo "   - Miner just started (validators haven't discovered you yet)"
    echo "   - Miner is not properly registered"
    echo "   - Axon is not served to the network"
    echo "   - Network connectivity issues"
fi
echo ""

# Check if axon is served to network
echo "📋 Step 8: Checking miner startup logs for axon serving..."
echo ""
if journalctl -u autoppia-miner --no-pager 2>/dev/null | grep -i "served to.*network\|serve_axon" | tail -5; then
    echo "   ✅ Found axon serving in logs"
else
    echo "   ⚠️  No 'served to network' message found in logs"
    echo "   The miner may not be properly advertising itself to validators"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "For validators to discover your miner, you need:"
echo "  ✅ Miner registered on subnet 36 (check with ./check_registration.sh)"
echo "  ✅ API service running on port $API_PORT"
echo "  ✅ Miner service running with axon on port $AXON_PORT"
echo "  ✅ Axon served to subtensor network"
echo "  ✅ Ports $API_PORT and $AXON_PORT accessible from internet"
echo "  ✅ External IP correctly configured"
echo ""
echo "Next steps:"
echo "  - Monitor logs: journalctl -u autoppia-miner -f"
echo "  - Check dashboard: http://$EXTERNAL_IP:$API_PORT/dashboard"
echo "  - Wait 5-10 minutes for validators to discover you"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
