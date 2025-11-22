#!/bin/bash
# Real-time benchmark monitoring - Run this while benchmark is running

echo "🔍 Real-Time Benchmark Monitor"
echo "================================"
echo ""
echo "Watching API for benchmark requests..."
echo "Press Ctrl+C to stop"
echo ""
echo "📊 Monitoring:"
echo "   - API requests"
echo "   - Response times"
echo "   - Success/failure"
echo "   - Errors"
echo ""

# Watch API logs
ssh root@134.199.203.133 "journalctl -u autoppia-api -f --no-pager" 2>/dev/null | while IFS= read -r line; do
    # Highlight important events
    if echo "$line" | grep -q "POST /solve_task"; then
        echo "📥 $(date '+%H:%M:%S') REQUEST: $line" | grep -o "POST /solve_task.*"
    elif echo "$line" | grep -q "200 OK"; then
        echo "✅ $(date '+%H:%M:%S') SUCCESS: Request completed"
    elif echo "$line" | grep -q "ERROR"; then
        echo "❌ $(date '+%H:%M:%S') ERROR: $line" | grep -o "ERROR.*"
    fi
done

