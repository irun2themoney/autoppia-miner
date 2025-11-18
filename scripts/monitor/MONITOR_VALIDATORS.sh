#!/bin/bash
# Real-time validator activity monitor
# Shows filtered logs from both miner and API

echo "🔍 Real-Time Validator Activity Monitor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Watching for validator activity..."
echo "Press Ctrl+C to stop"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to format log output
format_log() {
    while IFS= read -r line; do
        # Color code miner logs
        if echo "$line" | grep -q "autoppia-miner"; then
            echo -e "\033[0;34m[Miner]\033[0m $line"
        # Color code API logs
        elif echo "$line" | grep -q "autoppia-api"; then
            echo -e "\033[0;32m[API]\033[0m $line"
        else
            echo "$line"
        fi
    done
}

# Monitor both services with filtering
{
    # Miner logs - validator activity
    journalctl -u autoppia-miner -f --no-pager 2>/dev/null | \
        grep --line-buffered -E "forward|synapse|process_task|validator|Forward|Synapse|ERROR|error|Exception|exception" -i | \
        while IFS= read -r line; do
            echo -e "\033[0;34m[Miner]\033[0m $(date '+%H:%M:%S') $line"
        done &
    
    MINER_PID=$!
    
    # API logs - solve_task requests
    journalctl -u autoppia-api -f --no-pager 2>/dev/null | \
        grep --line-buffered -E "solve_task|POST|Task ID|Prompt|URL|ERROR|error|Exception|exception" -i | \
        while IFS= read -r line; do
            echo -e "\033[0;32m[API]\033[0m $(date '+%H:%M:%S') $line"
        done &
    
    API_PID=$!
    
    # Wait for Ctrl+C
    trap "kill $MINER_PID $API_PID 2>/dev/null; exit" INT TERM
    wait
}

