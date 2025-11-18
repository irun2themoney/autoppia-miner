#!/bin/bash
# Enhanced Validator Discovery Monitoring Script
# Based on Grok's recommendations

echo "🔍 Enhanced Validator Discovery Monitor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check services
echo "1️⃣  Service Status:"
if systemctl is-active --quiet autoppia-api && systemctl is-active --quiet autoppia-miner; then
    echo "   ✅ Both services running"
else
    echo "   ❌ Services not running"
    exit 1
fi
echo ""

# Check API health
echo "2️⃣  API Health Check:"
HEALTH=$(curl -s http://localhost:8080/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "   ✅ API responding"
    echo "$HEALTH" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Status: {d.get('status')}\"); print(f\"   Agent: {d.get('agent_type')}\"); print(f\"   Requests: {d.get('metrics', {}).get('total_requests', 0)}\")" 2>/dev/null || echo "   Response: $HEALTH"
else
    echo "   ❌ API not responding"
fi
echo ""

# Check recent API activity
echo "3️⃣  Recent API Activity (last 2 minutes):"
RECENT=$(journalctl -u autoppia-api --since '2 minutes ago' --no-pager | grep -E "solve_task|POST|GET" | tail -5)
if [ -n "$RECENT" ]; then
    echo "$RECENT"
else
    echo "   ⏳ No recent activity (waiting for validators...)"
fi
echo ""

# Check for validator IPs
echo "4️⃣  Validator IP Detection:"
VALIDATOR_IPS=$(journalctl -u autoppia-api --since '1 hour ago' --no-pager | grep -oE "([0-9]{1,3}\.){3}[0-9]{1,3}" | sort -u | grep -v "127.0.0.1\|134.199.203.133" | head -10)
if [ -n "$VALIDATOR_IPS" ]; then
    echo "   ✅ Validator IPs detected:"
    echo "$VALIDATOR_IPS" | while read ip; do
        echo "      - $ip"
    done
else
    echo "   ⏳ No validator IPs yet (normal if just started)"
fi
echo ""

# Check miner logs for task processing
echo "5️⃣  Miner Task Processing:"
TASKS=$(journalctl -u autoppia-miner --since '1 hour ago' --no-pager | grep -E "process_task|Processing task|Dynamic 3|success" | tail -5)
if [ -n "$TASKS" ]; then
    echo "$TASKS"
else
    echo "   ⏳ No tasks processed yet"
fi
echo ""

# Check axon status
echo "6️⃣  Axon Status:"
AXON_SERVED=$(journalctl -u autoppia-miner --since '1 hour ago' --no-pager | grep "Axon served" | tail -1)
if [ -n "$AXON_SERVED" ]; then
    echo "   ✅ $AXON_SERVED"
else
    echo "   ⚠️  No recent axon serving confirmation"
fi
echo ""

# Check ports
echo "7️⃣  Port Status:"
if ss -tlnp | grep -q ":8091"; then
    echo "   ✅ Port 8091 (axon) listening"
else
    echo "   ❌ Port 8091 not listening"
fi
if ss -tlnp | grep -q ":8080"; then
    echo "   ✅ Port 8080 (API) listening"
else
    echo "   ❌ Port 8080 not listening"
fi
echo ""

# Check firewall
echo "8️⃣  Firewall Status:"
if command -v ufw >/dev/null 2>&1; then
    UFW_8091=$(ufw status | grep 8091)
    UFW_8080=$(ufw status | grep 8080)
    if [ -n "$UFW_8091" ] && [ -n "$UFW_8080" ]; then
        echo "   ✅ Ports 8091 and 8080 allowed"
    else
        echo "   ⚠️  Check firewall rules: ufw allow 8091/tcp && ufw allow 8080/tcp"
    fi
else
    echo "   ℹ️  UFW not installed (check iptables if needed)"
fi
echo ""

# Dashboard metrics summary
echo "9️⃣  Dashboard Metrics Summary:"
METRICS=$(curl -s http://localhost:8080/api/dashboard/metrics 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "$METRICS" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    overview = d.get('overview', {})
    perf = d.get('performance', {})
    print(f\"   Total Requests: {overview.get('total_requests', 0)}\")
    print(f\"   Success Rate: {overview.get('success_rate', 0)}%\")
    print(f\"   Avg Response: {perf.get('avg_response_time', 0):.3f}s\")
    print(f\"   Health Score: {d.get('health_score', 0):.1f}\")
    validators = d.get('validators', {})
    print(f\"   Unique Validators: {validators.get('unique_validators', 0)}\")
except:
    print('   ⚠️  Could not parse metrics')
" 2>/dev/null || echo "   ⚠️  Could not fetch metrics"
else
    echo "   ❌ Could not fetch metrics"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary:"
echo ""
echo "   Status: $(systemctl is-active autoppia-api autoppia-miner >/dev/null 2>&1 && echo '✅ OPERATIONAL' || echo '❌ ISSUES')"
echo ""
echo "   Next Steps:"
echo "   - Watch logs: journalctl -u autoppia-api -f | grep solve_task"
echo "   - Check dashboard: http://134.199.203.133:8080/api/dashboard"
echo "   - Monitor miner: journalctl -u autoppia-miner -f"
echo ""
echo "   Expected Discovery: 5-30 minutes from now"
echo ""

