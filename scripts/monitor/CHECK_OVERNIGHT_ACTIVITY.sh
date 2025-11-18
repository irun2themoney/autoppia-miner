#!/bin/bash
# Check overnight miner activity and statistics

echo "📊 Overnight Miner Activity Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Time range (last 12 hours)
SINCE="12 hours ago"

# 1. Service Status
echo "1️⃣  Service Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if systemctl is-active --quiet autoppia-miner; then
    echo "   ✅ Miner: Running"
else
    echo "   ❌ Miner: Not running"
fi

if systemctl is-active --quiet autoppia-api; then
    echo "   ✅ API: Running"
else
    echo "   ❌ API: Not running"
fi
echo ""

# 2. Validator Activity Summary
echo "2️⃣  Validator Activity Summary (Last 12 Hours):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count solve_task requests
API_REQUESTS=$(journalctl -u autoppia-api --since "$SINCE" 2>/dev/null | grep -c "solve_task" || echo "0")
echo "   Total API Requests: $API_REQUESTS"

# Count forward calls
MINER_FORWARDS=$(journalctl -u autoppia-miner --since "$SINCE" 2>/dev/null | grep -cE "forward|Forward" || echo "0")
echo "   Miner Forward Calls: $MINER_FORWARDS"

# Count successful responses
SUCCESS_COUNT=$(journalctl -u autoppia-miner --since "$SINCE" 2>/dev/null | grep -cE "200 OK|success.*True" || echo "0")
echo "   Successful Responses: $SUCCESS_COUNT"

# Count errors
ERROR_COUNT=$(journalctl -u autoppia-miner --since "$SINCE" 2>/dev/null | grep -cE "ERROR|error|Exception|exception|Failed|failed" || echo "0")
API_ERRORS=$(journalctl -u autoppia-api --since "$SINCE" 2>/dev/null | grep -cE "ERROR|error|Exception|exception|500" || echo "0")
TOTAL_ERRORS=$((ERROR_COUNT + API_ERRORS))
echo "   Total Errors: $TOTAL_ERRORS"
echo ""

# 3. Recent Activity Timeline
echo "3️⃣  Recent Activity (Last 10 Requests):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
journalctl -u autoppia-api --since "$SINCE" --no-pager 2>/dev/null | grep "solve_task" | tail -10 | while read -r line; do
    timestamp=$(echo "$line" | grep -oP '\w{3} \d{1,2} \d{2}:\d{2}:\d{2}' | head -1)
    task_id=$(echo "$line" | grep -oP 'Task ID: [^\s]+' | cut -d' ' -f3)
    if [ -n "$timestamp" ] && [ -n "$task_id" ]; then
        echo "   [$timestamp] Task: $task_id"
    fi
done
if [ "$API_REQUESTS" -eq 0 ]; then
    echo "   ⚠️  No requests found in last 12 hours"
fi
echo ""

# 4. Error Analysis
if [ "$TOTAL_ERRORS" -gt 0 ]; then
    echo "4️⃣  Recent Errors:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    journalctl -u autoppia-miner --since "$SINCE" --no-pager 2>/dev/null | grep -E "ERROR|error|Exception|exception|Failed|failed" | tail -5
    journalctl -u autoppia-api --since "$SINCE" --no-pager 2>/dev/null | grep -E "ERROR|error|Exception|exception|500" | tail -5
    echo ""
fi

# 5. Sample Tasks
if [ "$API_REQUESTS" -gt 0 ]; then
    echo "5️⃣  Sample Tasks Processed:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    journalctl -u autoppia-api --since "$SINCE" --no-pager 2>/dev/null | grep -E "Prompt:|URL:" | tail -6 | while read -r line; do
        echo "   $line"
    done
    echo ""
fi

# 6. Performance Metrics
echo "6️⃣  Performance Metrics:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$API_REQUESTS" -gt 0 ]; then
    # Calculate success rate
    if [ "$SUCCESS_COUNT" -gt 0 ]; then
        SUCCESS_RATE=$(echo "scale=1; $SUCCESS_COUNT * 100 / $API_REQUESTS" | bc 2>/dev/null || echo "0")
        echo "   Success Rate: ${SUCCESS_RATE}%"
    else
        echo "   Success Rate: 0%"
    fi
    
    # Requests per hour
    REQUESTS_PER_HOUR=$(echo "scale=1; $API_REQUESTS / 12" | bc 2>/dev/null || echo "0")
    echo "   Requests/Hour: $REQUESTS_PER_HOUR"
else
    echo "   ⚠️  No activity to calculate metrics"
fi
echo ""

# 7. Service Uptime
echo "7️⃣  Service Uptime:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
systemctl show autoppia-miner --property=ActiveEnterTimestamp --value 2>/dev/null | xargs -I {} date -d {} '+%Y-%m-%d %H:%M:%S' 2>/dev/null | while read -r time; do
    echo "   Miner Started: $time"
done
systemctl show autoppia-api --property=ActiveEnterTimestamp --value 2>/dev/null | xargs -I {} date -d {} '+%Y-%m-%d %H:%M:%S' 2>/dev/null | while read -r time; do
    echo "   API Started: $time"
done
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$API_REQUESTS" -eq 0 ]; then
    echo "   ⚠️  No validator activity detected in last 12 hours"
    echo "   This is normal for new miners - validators may take time to discover you"
else
    echo "   ✅ Validators ARE testing your miner!"
    echo "   Total requests: $API_REQUESTS"
    echo "   Success rate: ${SUCCESS_RATE}%"
fi
echo ""
echo "💡 To see detailed logs:"
echo "   journalctl -u autoppia-miner --since '12 hours ago' | tail -50"
echo "   journalctl -u autoppia-api --since '12 hours ago' | tail -50"
echo ""

