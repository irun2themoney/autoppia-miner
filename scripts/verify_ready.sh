#!/bin/bash
# Comprehensive verification that miner is ready for validators
# Usage: ./scripts/verify_ready.sh

echo "🔍 Verifying Miner Readiness for Validator Discovery..."
echo "=================================================="
echo ""

ERRORS=0
WARNINGS=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((ERRORS++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

# 1. Check miner service
echo "1. Checking Miner Service..."
MINER_STATUS=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no root@134.199.203.133 \
    "systemctl is-active autoppia-miner" 2>/dev/null)
if [ "$MINER_STATUS" = "active" ]; then
    check_pass "Miner service is running"
else
    check_fail "Miner service is NOT running (status: $MINER_STATUS)"
fi

# 2. Check API service
echo ""
echo "2. Checking API Service..."
API_STATUS=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no root@134.199.203.133 \
    "systemctl is-active autoppia-api" 2>/dev/null)
if [ "$API_STATUS" = "active" ]; then
    check_pass "API service is running"
else
    check_fail "API service is NOT running (status: $API_STATUS)"
fi

# 3. Check API health endpoint
echo ""
echo "3. Checking API Health..."
HEALTH_RESPONSE=$(curl -s http://134.199.203.133:8080/health 2>/dev/null)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    check_pass "API health check passed"
    echo "   Response: $(echo "$HEALTH_RESPONSE" | head -c 100)..."
else
    check_fail "API health check failed"
fi

# 4. Check solve_task endpoint
echo ""
echo "4. Testing solve_task Endpoint..."
TEST_RESPONSE=$(curl -s -X POST http://134.199.203.133:8080/solve_task \
    -H "Content-Type: application/json" \
    -d '{"id":"test-123","prompt":"Click the login button","url":"https://example.com"}' 2>/dev/null)
if echo "$TEST_RESPONSE" | grep -q "actions"; then
    check_pass "solve_task endpoint responding"
    ACTION_COUNT=$(echo "$TEST_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('actions', [])))" 2>/dev/null || echo "0")
    echo "   Generated $ACTION_COUNT actions"
else
    check_fail "solve_task endpoint not responding correctly"
fi

# 5. Check miner logs for axon serving
echo ""
echo "5. Checking Axon Status..."
AXON_SERVING=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no root@134.199.203.133 \
    "journalctl -u autoppia-miner --since '10 minutes ago' --no-pager | grep -i 'serving\|axon\|uid' | tail -5" 2>/dev/null)
if echo "$AXON_SERVING" | grep -qi "serving\|axon"; then
    check_pass "Axon appears to be serving"
    echo "   Recent logs:"
    echo "$AXON_SERVING" | sed 's/^/   /'
else
    check_warn "Could not confirm axon serving from recent logs"
    echo "   (This is OK if miner just started)"
fi

# 6. Check UID registration
echo ""
echo "6. Checking UID Registration..."
UID_CHECK=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no root@134.199.203.133 \
    "journalctl -u autoppia-miner --since '1 hour ago' --no-pager | grep -i 'uid.*160\|registered' | tail -3" 2>/dev/null)
if echo "$UID_CHECK" | grep -qi "160\|registered"; then
    check_pass "UID 160 appears registered"
    echo "$UID_CHECK" | sed 's/^/   /'
else
    check_warn "Could not confirm UID 160 in recent logs"
fi

# 7. Check port accessibility
echo ""
echo "7. Checking Port Accessibility..."
PORT_8080=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://134.199.203.133:8080/health 2>/dev/null)
if [ "$PORT_8080" = "200" ]; then
    check_pass "Port 8080 is accessible"
else
    check_fail "Port 8080 not accessible (HTTP $PORT_8080)"
fi

# 8. Check firewall
echo ""
echo "8. Checking Firewall..."
FIREWALL_STATUS=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no root@134.199.203.133 \
    "ufw status | grep '8080\|8091' | head -2" 2>/dev/null)
if echo "$FIREWALL_STATUS" | grep -q "8080\|8091"; then
    check_pass "Firewall rules found for ports"
    echo "$FIREWALL_STATUS" | sed 's/^/   /'
else
    check_warn "Could not verify firewall rules (may be using iptables)"
fi

# 9. Check recent errors
echo ""
echo "9. Checking for Recent Errors..."
RECENT_ERRORS=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no root@134.199.203.133 \
    "journalctl -u autoppia-miner -u autoppia-api --since '1 hour ago' --no-pager | grep -i 'error\|exception\|failed' | wc -l" 2>/dev/null)
if [ "$RECENT_ERRORS" -eq 0 ]; then
    check_pass "No recent errors found"
else
    check_warn "Found $RECENT_ERRORS recent errors (may be normal)"
fi

# 10. Check dashboard metrics
echo ""
echo "10. Checking Dashboard Metrics..."
METRICS=$(curl -s http://134.199.203.133:8080/api/dashboard/metrics 2>/dev/null)
if [ -n "$METRICS" ]; then
    TOTAL_REQUESTS=$(echo "$METRICS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('overview', {}).get('total_requests', 0))" 2>/dev/null || echo "0")
    if [ "$TOTAL_REQUESTS" -ge 0 ]; then
        check_pass "Dashboard metrics accessible"
        echo "   Total requests: $TOTAL_REQUESTS"
    else
        check_warn "Dashboard metrics accessible but data unclear"
    fi
else
    check_warn "Could not fetch dashboard metrics"
fi

# Summary
echo ""
echo "=================================================="
echo "📊 Verification Summary:"
echo "   ✅ Passed: $((10 - ERRORS - WARNINGS))"
if [ $WARNINGS -gt 0 ]; then
    echo "   ⚠️  Warnings: $WARNINGS"
fi
if [ $ERRORS -gt 0 ]; then
    echo "   ❌ Errors: $ERRORS"
fi
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}🎉 MINER IS READY FOR VALIDATOR DISCOVERY!${NC}"
    echo ""
    echo "✅ Everything looks good. You're ready to receive validator tasks."
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Wait for validators to discover you (5-30 minutes typical)"
    echo "   2. Monitor with: ./scripts/monitor_iwap_discovery.sh"
    echo "   3. Check first task: ./scripts/check_first_task.sh"
    echo "   4. Watch dashboard: http://134.199.203.133:8080/api/dashboard"
    echo ""
    echo "💡 Pro Tip: You can also test on IWA Playground:"
    echo "   https://infinitewebarena.autoppia.com/playground"
    echo "   Endpoint: 134.199.203.133:8080"
else
    echo -e "${RED}⚠️  SOME ISSUES FOUND - Please review errors above${NC}"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   - Check services: systemctl status autoppia-miner autoppia-api"
    echo "   - Check logs: journalctl -u autoppia-miner -n 50"
    echo "   - Verify firewall: ufw status"
fi

exit $ERRORS

