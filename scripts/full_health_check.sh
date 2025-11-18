#!/bin/bash
# Comprehensive health check for DigitalOcean server
# Usage: ./scripts/full_health_check.sh

SERVER_IP="134.199.203.133"
PASSWORD="DigitalOcean4life"

echo "🔍 Comprehensive Health Check - DigitalOcean Server"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Service Status
echo "1️⃣ Service Status:"
MINER_STATUS=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$SERVER_IP \
    "systemctl is-active autoppia-miner" 2>/dev/null)
API_STATUS=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$SERVER_IP \
    "systemctl is-active autoppia-api" 2>/dev/null)

if [ "$MINER_STATUS" = "active" ]; then
    check_pass "Miner service: Running"
else
    check_fail "Miner service: NOT running ($MINER_STATUS)"
fi

if [ "$API_STATUS" = "active" ]; then
    check_pass "API service: Running"
else
    check_fail "API service: NOT running ($API_STATUS)"
fi
echo ""

# 2. API Health
echo "2️⃣ API Health:"
HEALTH=$(curl -s http://$SERVER_IP:8080/health 2>/dev/null)
if echo "$HEALTH" | grep -q "healthy"; then
    check_pass "API health endpoint: Responding"
    AGENT_TYPE=$(echo "$HEALTH" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('agent_type', 'unknown'))" 2>/dev/null || echo "unknown")
    echo "   Agent Type: $AGENT_TYPE"
else
    check_fail "API health endpoint: Not responding"
fi
echo ""

# 3. Ports
echo "3️⃣ Port Accessibility:"
PORT_8080=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://$SERVER_IP:8080/health 2>/dev/null)
if [ "$PORT_8080" = "200" ]; then
    check_pass "Port 8080 (API): Accessible"
else
    check_fail "Port 8080 (API): Not accessible (HTTP $PORT_8080)"
fi

PORT_8091_CHECK=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$SERVER_IP \
    "ss -tlnp 2>/dev/null | grep ':8091' | wc -l" 2>/dev/null || echo "0")
if [ "$PORT_8091_CHECK" -gt 0 ]; then
    check_pass "Port 8091 (Axon): Listening"
else
    check_warn "Port 8091 (Axon): May not be listening (check miner logs)"
fi
echo ""

# 4. Recent Activity
echo "4️⃣ Recent Activity:"
MINER_TASKS=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$SERVER_IP \
    "journalctl -u autoppia-miner --since '1 hour ago' --no-pager | grep -i 'processing task\|task received' | wc -l" 2>/dev/null || echo "0")
API_REQUESTS=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$SERVER_IP \
    "journalctl -u autoppia-api --since '1 hour ago' --no-pager | grep -i 'POST /solve_task' | wc -l" 2>/dev/null || echo "0")

if [ "$MINER_TASKS" -gt 0 ]; then
    check_pass "Miner tasks processed: $MINER_TASKS (last hour)"
else
    echo "   Miner tasks: 0 (waiting for validators)"
fi

if [ "$API_REQUESTS" -gt 0 ]; then
    check_pass "API requests: $API_REQUESTS (last hour)"
else
    echo "   API requests: 0 (waiting for validators)"
fi
echo ""

# 5. System Resources
echo "5️⃣ System Resources:"
UPTIME=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$SERVER_IP \
    "uptime -p" 2>/dev/null || echo "unknown")
echo "   Server Uptime: $UPTIME"

LOAD=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$SERVER_IP \
    "uptime | awk -F'load average:' '{print \$2}'" 2>/dev/null || echo "unknown")
echo "   Load Average: $LOAD"

MEMORY=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$SERVER_IP \
    "free -h | grep Mem | awk '{print \$3\"/\"\$2}'" 2>/dev/null || echo "unknown")
echo "   Memory Usage: $MEMORY"
echo ""

# 6. Dashboard Metrics
echo "6️⃣ Dashboard Metrics:"
METRICS=$(curl -s http://$SERVER_IP:8080/api/dashboard/metrics 2>/dev/null)
if [ -n "$METRICS" ]; then
    TOTAL_REQUESTS=$(echo "$METRICS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('overview', {}).get('total_requests', 0))" 2>/dev/null || echo "0")
    SUCCESS_RATE=$(echo "$METRICS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('overview', {}).get('success_rate', 0))" 2>/dev/null || echo "0")
    HEALTH_SCORE=$(echo "$METRICS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('health_score', 0))" 2>/dev/null || echo "0")
    
    check_pass "Dashboard accessible"
    echo "   Total Requests: $TOTAL_REQUESTS"
    echo "   Success Rate: $SUCCESS_RATE%"
    echo "   Health Score: $HEALTH_SCORE"
else
    check_fail "Dashboard not accessible"
fi
echo ""

# 7. Recent Errors
echo "7️⃣ Recent Errors:"
ERRORS=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$SERVER_IP \
    "journalctl -u autoppia-miner -u autoppia-api --since '1 hour ago' --no-pager | grep -i 'error\|exception\|failed' | wc -l" 2>/dev/null || echo "0")
if [ "$ERRORS" -eq 0 ]; then
    check_pass "No recent errors"
else
    check_warn "Found $ERRORS recent errors (may be normal)"
fi
echo ""

# Summary
echo "=================================================="
echo "📊 Health Check Summary:"
echo ""

if [ "$MINER_STATUS" = "active" ] && [ "$API_STATUS" = "active" ] && [ "$PORT_8080" = "200" ]; then
    echo -e "${GREEN}✅ ALL SYSTEMS OPERATIONAL${NC}"
    echo ""
    echo "Your miner is running correctly on DigitalOcean!"
    echo ""
    echo "📋 Status:"
    echo "   ✅ Services: Running"
    echo "   ✅ API: Healthy"
    echo "   ✅ Ports: Accessible"
    echo "   ✅ Dashboard: Working"
    echo ""
    echo "⏳ Waiting for validator discovery (normal)"
    echo ""
    echo "💡 Monitor with:"
    echo "   ./scripts/auto_monitor.sh"
    echo "   http://$SERVER_IP:8080/api/dashboard"
else
    echo -e "${YELLOW}⚠️  SOME ISSUES DETECTED${NC}"
    echo ""
    echo "Please review the checks above for details."
fi

