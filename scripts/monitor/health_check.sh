#!/bin/bash
# Comprehensive health check script for the miner
# Checks all critical components and provides actionable recommendations

echo "🔍 Comprehensive Miner Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check 1: Services Status
echo "1️⃣  Services Status:"
if systemctl is-active --quiet autoppia-miner 2>/dev/null; then
    echo -e "   ${GREEN}✅${NC} Miner service: RUNNING"
else
    echo -e "   ${RED}❌${NC} Miner service: NOT RUNNING"
    echo "   Action: sudo systemctl start autoppia-miner"
fi

if systemctl is-active --quiet autoppia-api 2>/dev/null; then
    echo -e "   ${GREEN}✅${NC} API service: RUNNING"
else
    echo -e "   ${RED}❌${NC} API service: NOT RUNNING"
    echo "   Action: sudo systemctl start autoppia-api"
fi
echo ""

# Check 2: Port Status
echo "2️⃣  Port Status:"
if lsof -i :8091 >/dev/null 2>&1; then
    echo -e "   ${GREEN}✅${NC} Port 8091 (Axon): LISTENING"
else
    echo -e "   ${RED}❌${NC} Port 8091 (Axon): NOT LISTENING"
fi

if lsof -i :8080 >/dev/null 2>&1; then
    echo -e "   ${GREEN}✅${NC} Port 8080 (API): LISTENING"
else
    echo -e "   ${RED}❌${NC} Port 8080 (API): NOT LISTENING"
fi
echo ""

# Check 3: API Health
echo "3️⃣  API Health:"
API_RESPONSE=$(curl -s http://localhost:8080/health 2>/dev/null)
if [ $? -eq 0 ] && echo "$API_RESPONSE" | grep -q "healthy"; then
    echo -e "   ${GREEN}✅${NC} API is healthy"
    echo "$API_RESPONSE" | python3 -m json.tool 2>/dev/null | head -10
else
    echo -e "   ${RED}❌${NC} API health check failed"
fi
echo ""

# Check 4: Miner Registration
echo "4️⃣  Miner Registration:"
cd /opt/autoppia-miner 2>/dev/null || cd ~/autoppia-miner 2>/dev/null || cd . 2>/dev/null
REGISTRATION=$(python3 -c "
from bittensor import wallet as bt_wallet, subtensor as bt_subtensor
try:
    w = bt_wallet(name='default', hotkey='default')
    st = bt_subtensor(network='finney')
    metagraph = st.metagraph(netuid=36)
    uid = metagraph.hotkeys.index(w.hotkey.ss58_address) if w.hotkey.ss58_address in metagraph.hotkeys else None
    if uid is not None:
        print(f'UID: {uid}')
        print(f'Incentive: {metagraph.I[uid]:.6f}')
        print(f'Trust: {metagraph.T[uid]:.6f}')
        print(f'Stake: {metagraph.S[uid]:.2f} TAO')
    else:
        print('NOT REGISTERED')
except Exception as e:
    print(f'ERROR: {e}')
" 2>/dev/null)

if echo "$REGISTRATION" | grep -q "UID:"; then
    echo -e "   ${GREEN}✅${NC} Miner is registered"
    echo "$REGISTRATION" | sed 's/^/   /'
else
    echo -e "   ${RED}❌${NC} Miner registration check failed"
    echo "   $REGISTRATION" | sed 's/^/   /'
fi
echo ""

# Check 5: Recent Validator Activity
echo "5️⃣  Recent Validator Activity:"
RECENT_LOGS=$(journalctl -u autoppia-miner -n 50 --no-pager 2>/dev/null | grep -i "task\|synapse\|processing" | tail -5)
if [ -n "$RECENT_LOGS" ]; then
    echo -e "   ${GREEN}✅${NC} Recent activity found:"
    echo "$RECENT_LOGS" | sed 's/^/   /' | head -3
else
    echo -e "   ${YELLOW}⚠️${NC}  No recent validator activity"
    echo "   This is normal if validators haven't tested you yet"
fi
echo ""

# Check 6: Dashboard Metrics
echo "6️⃣  Dashboard Metrics:"
DASHBOARD=$(curl -s http://localhost:8080/api/dashboard/metrics 2>/dev/null)
if [ $? -eq 0 ]; then
    TOTAL_REQUESTS=$(echo "$DASHBOARD" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('overview', {}).get('total_requests', 0))" 2>/dev/null)
    SUCCESS_RATE=$(echo "$DASHBOARD" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('overview', {}).get('success_rate', 0))" 2>/dev/null)
    UPTIME=$(echo "$DASHBOARD" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('overview', {}).get('uptime_hours', 0))" 2>/dev/null)
    
    echo "   Total Requests: $TOTAL_REQUESTS"
    echo "   Success Rate: ${SUCCESS_RATE}%"
    echo "   Uptime: ${UPTIME} hours"
    
    # Check proactive monitoring
    HEALTH=$(echo "$DASHBOARD" | python3 -c "import sys, json; d=json.load(sys.stdin); pm=d.get('proactive_monitoring', {}); print(f\"Health Score: {pm.get('health_score', 0):.1f}/100\"); print(f\"Status: {pm.get('status', 'unknown')}\"); print(f\"Hours Since Activity: {pm.get('hours_since_last_activity', 0):.1f}\")" 2>/dev/null)
    if [ -n "$HEALTH" ]; then
        echo "   $HEALTH" | sed 's/^/   /'
    fi
else
    echo -e "   ${RED}❌${NC} Could not fetch dashboard metrics"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary:"
echo "   View full dashboard: http://localhost:8080/api/dashboard"
echo "   Monitor logs: journalctl -u autoppia-miner -f"
echo "   Watch for tests: ~/watch_for_tests.sh"
echo ""

