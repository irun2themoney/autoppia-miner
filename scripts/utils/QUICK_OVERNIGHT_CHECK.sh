#!/bin/bash
# Quick overnight activity check

echo "📊 Quick Overnight Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Count requests in last 12 hours
REQUESTS=$(journalctl -u autoppia-api --since "12 hours ago" 2>/dev/null | grep -c "solve_task" || echo "0")

echo "Validator Requests (last 12h): $REQUESTS"
echo ""

if [ "$REQUESTS" -eq 0 ]; then
    echo "⚠️  No validator activity"
    echo ""
    echo "Recent miner logs:"
    journalctl -u autoppia-miner --since "12 hours ago" --no-pager 2>/dev/null | tail -5
else
    echo "✅ Validators ARE testing!"
    echo ""
    echo "Recent requests:"
    journalctl -u autoppia-api --since "12 hours ago" --no-pager 2>/dev/null | grep "solve_task" | tail -5
fi

echo ""
echo "For detailed report: bash CHECK_OVERNIGHT_ACTIVITY.sh"

