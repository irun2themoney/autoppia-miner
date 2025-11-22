#!/bin/bash
# Verify Miner Configuration - Ensure Everything Matches Working State

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Verifying Miner Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

API_PORT="${API_PORT:-8080}"
AXON_PORT="${AXON_PORT:-8091}"
EXTERNAL_IP="134.199.203.133"

echo "📋 Step 1: Service Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if systemctl is-active --quiet autoppia-miner 2>/dev/null; then
    echo "   ✅ Miner service: RUNNING"
else
    echo "   ❌ Miner service: NOT RUNNING"
    exit 1
fi

if systemctl is-active --quiet autoppia-api 2>/dev/null; then
    echo "   ✅ API service: RUNNING"
else
    echo "   ❌ API service: NOT RUNNING"
    exit 1
fi
echo ""

echo "📋 Step 2: Port Accessibility"
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

echo "📋 Step 3: IP Detection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Expected IP: $EXTERNAL_IP"
if journalctl -u autoppia-miner --no-pager 2>/dev/null | grep -q "Final external IP: $EXTERNAL_IP"; then
    echo "   ✅ IP detection: CORRECT ($EXTERNAL_IP)"
else
    echo "   ⚠️  IP detection: Check logs for IP"
fi
echo ""

echo "📋 Step 4: Axon Serving"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if journalctl -u autoppia-miner --no-pager 2>/dev/null | grep -q "Axon served to subtensor network"; then
    echo "   ✅ Axon: SERVED TO NETWORK"
else
    echo "   ❌ Axon: NOT SERVED TO NETWORK"
fi
echo ""

echo "📋 Step 5: Registration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if journalctl -u autoppia-miner --no-pager 2>/dev/null | grep -q "Miner registered! UID:"; then
    UID=$(journalctl -u autoppia-miner --no-pager 2>/dev/null | grep "Miner registered! UID:" | tail -1 | grep -oP 'UID: \K\d+')
    echo "   ✅ Miner: REGISTERED (UID: $UID)"
else
    echo "   ❌ Miner: NOT REGISTERED"
fi
echo ""

echo "📋 Step 6: API Endpoint"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
EXPECTED_URL="http://$EXTERNAL_IP:$API_PORT/solve_task"
if journalctl -u autoppia-miner --no-pager 2>/dev/null | grep -q "Validator API endpoint: $EXPECTED_URL"; then
    echo "   ✅ API endpoint: CORRECT ($EXPECTED_URL)"
else
    echo "   ⚠️  API endpoint: Check logs"
fi
echo ""

echo "📋 Step 7: API Accessibility"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if curl -s -f --max-time 3 http://localhost:$API_PORT/health > /dev/null 2>&1; then
    echo "   ✅ Local API: ACCESSIBLE"
else
    echo "   ❌ Local API: NOT ACCESSIBLE"
fi

if curl -s -f --max-time 5 http://$EXTERNAL_IP:$API_PORT/health > /dev/null 2>&1; then
    echo "   ✅ External API: ACCESSIBLE"
else
    echo "   ⚠️  External API: NOT ACCESSIBLE (may be firewall or timeout)"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "If all checks pass, your miner is configured correctly!"
echo "Validators should be able to discover and connect to your miner."
echo ""

