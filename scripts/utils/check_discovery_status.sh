#!/bin/bash
# Quick Discovery Status Check
# Fast check to see if validators have discovered you

echo "⚡ Quick Discovery Status Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get total requests
TOTAL_REQUESTS=$(curl -s http://localhost:8080/api/dashboard/metrics 2>/dev/null | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('overview', {}).get('total_requests', 0))" 2>/dev/null || echo "0")

# Check for validator IPs in last hour
VALIDATOR_COUNT=$(journalctl -u autoppia-api --since '1 hour ago' --no-pager | grep -E "solve_task|POST /solve_task" | grep -oE "([0-9]{1,3}\.){3}[0-9]{1,3}" | grep -v "127.0.0.1\|134.199.203.133" | sort -u | wc -l)

# Check for recent activity
RECENT_ACTIVITY=$(journalctl -u autoppia-api --since '5 minutes ago' --no-pager | grep -c "solve_task")

echo "📊 Current Status:"
echo "   Total Requests: $TOTAL_REQUESTS"
echo "   Unique Validators: $VALIDATOR_COUNT"
echo "   Activity (last 5 min): $RECENT_ACTIVITY requests"
echo ""

if [ "$TOTAL_REQUESTS" -gt 0 ]; then
    echo "✅ DISCOVERED! Validators are testing your miner!"
    echo ""
    echo "   Recent validator IPs:"
    journalctl -u autoppia-api --since '1 hour ago' --no-pager | grep "solve_task" | grep -oE "([0-9]{1,3}\.){3}[0-9]{1,3}" | grep -v "127.0.0.1\|134.199.203.133" | sort -u | head -5 | while read ip; do
        echo "      - $ip"
    done
elif [ "$RECENT_ACTIVITY" -gt 0 ]; then
    echo "🟡 ACTIVITY DETECTED! Validators may be probing..."
else
    echo "⏳ WAITING... No validator activity yet (this is normal)"
    echo ""
    echo "   Expected discovery: 5-30 minutes"
    echo "   Your miner is ready and waiting!"
fi
echo ""

