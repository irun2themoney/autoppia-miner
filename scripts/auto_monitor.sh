#!/bin/bash
# Automated monitoring - runs all checks and monitors for discovery
# Usage: ./scripts/auto_monitor.sh

echo "🚀 Automated Miner Monitoring Started"
echo "======================================"
echo ""

# Run verification
echo "1️⃣ Running Readiness Verification..."
./scripts/verify_ready.sh
echo ""

# Check dashboard
echo "2️⃣ Checking Dashboard Metrics..."
METRICS=$(curl -s http://134.199.203.133:8080/api/dashboard/metrics 2>/dev/null)
if [ -n "$METRICS" ]; then
    TOTAL_REQUESTS=$(echo "$METRICS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('overview', {}).get('total_requests', 0))" 2>/dev/null || echo "0")
    UNIQUE_VALIDATORS=$(echo "$METRICS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('validators', {}).get('unique_validators', 0))" 2>/dev/null || echo "0")
    SUCCESS_RATE=$(echo "$METRICS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('overview', {}).get('success_rate', 0))" 2>/dev/null || echo "0")
    
    echo "   ✅ Dashboard accessible"
    echo "   📊 Total Requests: $TOTAL_REQUESTS"
    echo "   👥 Unique Validators: $UNIQUE_VALIDATORS"
    echo "   📈 Success Rate: $SUCCESS_RATE%"
    
    if [ "$TOTAL_REQUESTS" -gt 0 ]; then
        echo ""
        echo "   🎉 VALIDATOR ACTIVITY DETECTED!"
    fi
else
    echo "   ⚠️  Could not fetch dashboard metrics"
fi
echo ""

# Check IWAP
echo "3️⃣ Checking IWAP for UID 160..."
IWAP_CHECK=$(curl -s "https://infinitewebarena.autoppia.com/subnet36/agents" 2>/dev/null)
if echo "$IWAP_CHECK" | grep -qi "uid.*160\|160"; then
    echo "   🎉🎉🎉 UID 160 FOUND ON IWAP! 🎉🎉🎉"
    echo ""
    echo "$IWAP_CHECK" | grep -i "uid.*160\|160" | head -3
    echo ""
    echo "   View at: https://infinitewebarena.autoppia.com/subnet36/agents"
else
    echo "   ⏳ UID 160 not yet visible (waiting for first task completion)"
fi
echo ""

# Summary
echo "======================================"
echo "📋 Summary:"
echo "   ✅ Verification: Complete"
echo "   ✅ Dashboard: Checked"
echo "   ✅ IWAP: Checked"
echo ""
echo "💡 Next Steps:"
echo "   - Run this script periodically: ./scripts/auto_monitor.sh"
echo "   - Or start continuous monitoring: ./scripts/monitor_iwap_discovery.sh"
echo "   - View dashboard: http://134.199.203.133:8080/api/dashboard"
echo ""

