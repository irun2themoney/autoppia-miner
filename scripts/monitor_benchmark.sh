#!/bin/bash
# Monitor benchmark progress in real-time

echo "🔍 Monitoring Benchmark Progress"
echo "=================================="
echo ""
echo "Watching for benchmark requests..."
echo "Press Ctrl+C to stop"
echo ""

# Watch API logs for benchmark activity
ssh root@134.199.203.133 "journalctl -u autoppia-api -f" | grep --line-buffered -E "POST /solve_task|ERROR|Actions|success" | while read line; do
    timestamp=$(date '+%H:%M:%S')
    echo "[$timestamp] $line"
done

