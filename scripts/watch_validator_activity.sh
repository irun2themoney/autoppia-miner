#!/bin/bash
# Live Validator Activity Watcher
# Run this to watch for validator discovery in real-time

echo "👀 Live Validator Activity Monitor"
echo "Press Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Watch API logs for solve_task requests
echo "📡 Watching API for /solve_task requests..."
echo "   (This will show validator IPs when they start testing)"
echo ""

journalctl -u autoppia-api -f --no-pager | while read line; do
    # Highlight solve_task requests
    if echo "$line" | grep -q "solve_task"; then
        echo "🎯 $(date '+%H:%M:%S') - $line" | grep --color=always -E "solve_task|POST|validator|134.199"
    # Highlight health checks (validators probing)
    elif echo "$line" | grep -qE "GET /health|GET /api/dashboard"; then
        echo "💚 $(date '+%H:%M:%S') - $line" | grep --color=always -E "health|dashboard"
    # Show all other activity
    elif echo "$line" | grep -qE "INFO.*GET|INFO.*POST"; then
        echo "📥 $(date '+%H:%M:%S') - $line"
    fi
done

