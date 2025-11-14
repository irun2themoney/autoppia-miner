#!/bin/bash

# Single snapshot monitoring script for Autoppia Miner
# No keyboard shortcuts needed - just shows current status

# Using DigitalOcean deployment
BASE_URL="http://134.199.203.133:8080"

clear
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        📊 MINER STATUS SNAPSHOT 📊                           ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "URL: $BASE_URL"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Get metrics
metrics=$(curl -s --max-time 10 "$BASE_URL/metrics" 2>/dev/null)
health=$(curl -s --max-time 10 "$BASE_URL/health" 2>/dev/null)

# Parse and display metrics
if [ -n "$metrics" ] && echo "$metrics" | grep -q "requests"; then
    total=$(echo "$metrics" | python3 -c "import sys, json; print(json.load(sys.stdin).get('requests', {}).get('total', 0))" 2>/dev/null || echo "0")
    success=$(echo "$metrics" | python3 -c "import sys, json; print(json.load(sys.stdin).get('requests', {}).get('success', 0))" 2>/dev/null || echo "0")
    errors=$(echo "$metrics" | python3 -c "import sys, json; print(json.load(sys.stdin).get('requests', {}).get('errors', 0))" 2>/dev/null || echo "0")
    success_rate=$(echo "$metrics" | python3 -c "import sys, json; print(json.load(sys.stdin).get('requests', {}).get('success_rate_percent', '0%'))" 2>/dev/null || echo "0%")
    cache_size=$(echo "$metrics" | python3 -c "import sys, json; print(json.load(sys.stdin).get('cache', {}).get('size', 0))" 2>/dev/null || echo "0")
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 REQUEST STATISTICS:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   Total Requests:    $total"
    echo "   Successful:        $success"
    echo "   Errors:            $errors"
    echo "   Success Rate:      $success_rate"
    echo "   Cache Size:        $cache_size / 100"
    echo ""
    
    # Task type breakdown
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 TASK TYPE BREAKDOWN:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    task_types=$(echo "$metrics" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    by_type = data.get('by_task_type', {}).get('request_count', {})
    if by_type:
        for task_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            print(f'   {task_type:20s}: {count}')
    else:
        print('   No tasks processed yet')
except:
    print('   Unable to parse task types')
" 2>/dev/null)
    echo "$task_types"
    echo ""
else
    echo "⚠️  Could not fetch metrics (service may be sleeping)"
    echo ""
fi

# Health status
if [ -n "$health" ] && echo "$health" | grep -q "status"; then
    status=$(echo "$health" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "unknown")
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🏥 HEALTH STATUS:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ "$status" = "healthy" ]; then
        echo "   ✅ Status: $status"
    else
        echo "   ⚠️  Status: $status"
    fi
    echo ""
else
    echo "⚠️  Could not fetch health status"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 TIP: Run this script again to refresh: ./monitor_once.sh"
echo ""

