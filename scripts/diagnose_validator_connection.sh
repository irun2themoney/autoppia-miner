#!/bin/bash
# Comprehensive diagnostic script for validator connection issues

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Validator Connection Diagnostic Tool"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

API_PORT="${API_PORT:-8080}"
AXON_PORT="${AXON_PORT:-8091}"
WALLET_NAME="${WALLET_NAME:-default}"
WALLET_HOTKEY="${WALLET_HOTKEY:-default}"

# Get external IP
echo "📋 Step 1: Network Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
EXTERNAL_IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || curl -s --max-time 5 ifconfig.co 2>/dev/null || echo "unknown")
echo "   External IP: $EXTERNAL_IP"
echo "   API Port: $API_PORT"
echo "   Axon Port: $AXON_PORT"
echo ""

# Check if services are running
echo "📋 Step 2: Service Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if systemctl is-active --quiet autoppia-api 2>/dev/null; then
    echo "   ✅ API service: RUNNING"
else
    echo "   ❌ API service: NOT RUNNING"
    echo "      Fix: sudo systemctl start autoppia-api"
fi

if systemctl is-active --quiet autoppia-miner 2>/dev/null; then
    echo "   ✅ Miner service: RUNNING"
else
    echo "   ❌ Miner service: NOT RUNNING"
    echo "      Fix: sudo systemctl start autoppia-miner"
fi
echo ""

# Check port listening
echo "📋 Step 3: Port Accessibility"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if netstat -tuln 2>/dev/null | grep -q ":$API_PORT " || ss -tuln 2>/dev/null | grep -q ":$API_PORT "; then
    echo "   ✅ API port $API_PORT: LISTENING"
else
    echo "   ❌ API port $API_PORT: NOT LISTENING"
fi

if netstat -tuln 2>/dev/null | grep -q ":$AXON_PORT " || ss -tuln 2>/dev/null | grep -q ":$AXON_PORT "; then
    echo "   ✅ Axon port $AXON_PORT: LISTENING"
else
    echo "   ❌ Axon port $AXON_PORT: NOT LISTENING"
fi
echo ""

# Test API accessibility
echo "📋 Step 4: API Accessibility"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if curl -s -f --max-time 5 http://localhost:$API_PORT/health > /dev/null 2>&1; then
    echo "   ✅ Local API: ACCESSIBLE"
    HEALTH_RESPONSE=$(curl -s --max-time 5 http://localhost:$API_PORT/health)
    echo "   Response: $HEALTH_RESPONSE" | head -c 100
    echo ""
else
    echo "   ❌ Local API: NOT ACCESSIBLE"
fi

if [ "$EXTERNAL_IP" != "unknown" ]; then
    if curl -s -f --max-time 5 http://$EXTERNAL_IP:$API_PORT/health > /dev/null 2>&1; then
        echo "   ✅ External API: ACCESSIBLE"
    else
        echo "   ⚠️  External API: NOT ACCESSIBLE (may be firewall issue)"
        echo "      Validators need: http://$EXTERNAL_IP:$API_PORT/solve_task"
    fi
fi
echo ""

# Check miner registration
echo "📋 Step 5: Miner Registration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v btcli &> /dev/null; then
    MINER_UID=$(btcli subnet show --netuid 36 --wallet.name "$WALLET_NAME" --wallet.hotkey "$WALLET_HOTKEY" 2>/dev/null | grep -i "uid" | head -1 | awk '{print $2}' || echo "unknown")
    if [ "$MINER_UID" != "unknown" ] && [ -n "$MINER_UID" ]; then
        echo "   ✅ Registered: UID $MINER_UID"
    else
        echo "   ❌ NOT REGISTERED on subnet 36"
        echo "      Fix: btcli subnet register --netuid 36 --wallet.name $WALLET_NAME --wallet.hotkey $WALLET_HOTKEY"
    fi
else
    echo "   ⚠️  btcli not found, cannot check registration"
fi
echo ""

# Check recent logs
echo "📋 Step 6: Recent Activity"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Miner logs (last 20 lines):"
if journalctl -u autoppia-miner -n 20 --no-pager 2>/dev/null | tail -10; then
    echo ""
else
    echo "   ⚠️  No miner logs found"
fi

echo "   Looking for validator requests..."
VALIDATOR_REQUESTS=$(journalctl -u autoppia-miner --since "1 hour ago" --no-pager 2>/dev/null | grep -i "processing task\|validator\|synapse" | wc -l)
if [ "$VALIDATOR_REQUESTS" -gt 0 ]; then
    echo "   ✅ Found $VALIDATOR_REQUESTS validator requests in last hour"
else
    echo "   ⚠️  No validator requests in last hour"
fi
echo ""

# Check axon serving
echo "📋 Step 7: Axon Serving Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if journalctl -u autoppia-miner --no-pager 2>/dev/null | grep -i "served to.*network\|serve_axon\|axon.*served" | tail -3; then
    echo "   ✅ Axon serving confirmed in logs"
else
    echo "   ❌ No axon serving confirmation found"
    echo "      This is CRITICAL - validators cannot discover you!"
fi
echo ""

# Check for errors
echo "📋 Step 8: Error Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ERRORS=$(journalctl -u autoppia-miner --since "1 hour ago" --no-pager 2>/dev/null | grep -i "error\|failed\|exception" | wc -l)
if [ "$ERRORS" -gt 0 ]; then
    echo "   ⚠️  Found $ERRORS errors in last hour:"
    journalctl -u autoppia-miner --since "1 hour ago" --no-pager 2>/dev/null | grep -i "error\|failed\|exception" | tail -5
else
    echo "   ✅ No recent errors found"
fi
echo ""

# Summary and recommendations
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary & Recommendations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "For validators to connect, you need:"
echo ""
echo "1. ✅ Miner registered on subnet 36"
echo "2. ✅ API running on port $API_PORT (accessible from internet)"
echo "3. ✅ Miner running with axon on port $AXON_PORT"
echo "4. ✅ Axon served to subtensor network (CRITICAL!)"
echo "5. ✅ Ports $API_PORT and $AXON_PORT open in firewall"
echo "6. ✅ External IP correctly configured: $EXTERNAL_IP"
echo ""
echo "Validator API endpoint should be:"
echo "   http://$EXTERNAL_IP:$API_PORT/solve_task"
echo ""
echo "Next steps:"
echo "  - Monitor logs: journalctl -u autoppia-miner -f"
echo "  - Check dashboard: http://$EXTERNAL_IP:$API_PORT/api/dashboard"
echo "  - Wait 10-30 minutes for validators to discover you"
echo "  - Check if other miners are getting requests (subnet activity)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

