#!/bin/bash

# Live monitoring script for Autoppia Miner
# Shows real-time metrics and progress

BASE_URL="https://autoppia-miner.onrender.com"
REFRESH_INTERVAL=5  # seconds

clear
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        📊 LIVE MINER MONITORING 📊                           ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Monitoring: $BASE_URL"
echo "Refresh: Every ${REFRESH_INTERVAL}s (Press Ctrl+C to stop)"
echo ""

while true; do
    # Get current time
    current_time=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Get metrics
    metrics=$(curl -s "$BASE_URL/metrics" 2>/dev/null)
    health=$(curl -s "$BASE_URL/health" 2>/dev/null)
    
    # Clear screen and show header
    clear
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║        📊 LIVE MINER MONITORING 📊                           ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Last Updated: $current_time"
    echo "URL: $BASE_URL"
    echo ""
    
    # Parse and display metrics
    if [ -n "$metrics" ]; then
        total=$(echo "$metrics" | python3 -c "import sys, json; print(json.load(sys.stdin).get('requests', {}).get('total', 0))" 2>/dev/null)
        success=$(echo "$metrics" | python3 -c "import sys, json; print(json.load(sys.stdin).get('requests', {}).get('success', 0))" 2>/dev/null)
        errors=$(echo "$metrics" | python3 -c "import sys, json; print(json.load(sys.stdin).get('requests', {}).get('errors', 0))" 2>/dev/null)
        success_rate=$(echo "$metrics" | python3 -c "import sys, json; print(json.load(sys.stdin).get('requests', {}).get('success_rate_percent', '0%'))" 2>/dev/null)
        cache_size=$(echo "$metrics" | python3 -c "import sys, json; print(json.load(sys.stdin).get('cache', {}).get('size', 0))" 2>/dev/null)
        
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
data = json.load(sys.stdin)
by_type = data.get('by_task_type', {}).get('request_count', {})
if by_type:
    for task_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        print(f'   {task_type:20s}: {count}')
else:
    print('   No tasks processed yet')
" 2>/dev/null)
        echo "$task_types"
        echo ""
    fi
    
    # Health status
    if [ -n "$health" ]; then
        status=$(echo "$health" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null)
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🏥 HEALTH STATUS:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        if [ "$status" = "healthy" ]; then
            echo "   ✅ Status: $status"
        else
            echo "   ⚠️  Status: $status"
        fi
        echo ""
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Press Ctrl+C to stop monitoring"
    echo "Refreshing in ${REFRESH_INTERVAL} seconds..."
    
    sleep $REFRESH_INTERVAL
done

