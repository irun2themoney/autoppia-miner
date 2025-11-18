#!/bin/bash
# Check if first validator task has been received
# Usage: ./scripts/check_first_task.sh

echo "🔍 Checking for first validator task..."
echo ""

# Check API logs for solve_task requests
API_REQUESTS=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no root@134.199.203.133 \
    "journalctl -u autoppia-api --since '1 hour ago' --no-pager | grep -E 'POST /solve_task|solve_task' | wc -l" 2>/dev/null)

# Check miner logs for task processing
MINER_TASKS=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no root@134.199.203.133 \
    "journalctl -u autoppia-miner --since '1 hour ago' --no-pager | grep -E 'process_task|Processing task|Task received' | wc -l" 2>/dev/null)

# Check dashboard metrics
METRICS=$(curl -s http://134.199.203.133:8080/api/dashboard/metrics 2>/dev/null)
TOTAL_REQUESTS=$(echo "$METRICS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('overview', {}).get('total_requests', 0))" 2>/dev/null || echo "0")
UNIQUE_VALIDATORS=$(echo "$METRICS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('validators', {}).get('unique_validators', 0))" 2>/dev/null || echo "0")

echo "📊 Status:"
echo "  API solve_task requests: $API_REQUESTS"
echo "  Miner task processing: $MINER_TASKS"
echo "  Total requests (dashboard): $TOTAL_REQUESTS"
echo "  Unique validators: $UNIQUE_VALIDATORS"
echo ""

if [ "$TOTAL_REQUESTS" -gt 0 ] || [ "$API_REQUESTS" -gt 0 ] || [ "$MINER_TASKS" -gt 0 ]; then
    echo "✅ FIRST TASK RECEIVED!"
    echo ""
    echo "🎯 Next steps:"
    echo "  1. Check IWAP: https://infinitewebarena.autoppia.com/subnet36/agents"
    echo "  2. Search for UID 160"
    echo "  3. Monitor dashboard: http://134.199.203.133:8080/api/dashboard"
    echo "  4. Review logs for performance"
else
    echo "⏳ Still waiting for first validator task..."
    echo ""
    echo "💡 Tips:"
    echo "  - Discovery typically takes 5-30 minutes"
    echo "  - Ensure miner is running: systemctl status autoppia-miner"
    echo "  - Check axon is served: journalctl -u autoppia-miner -n 20"
fi

