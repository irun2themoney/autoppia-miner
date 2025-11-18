#!/bin/bash
# Monitor IWAP for UID 160 discovery and alert when found
# Usage: ./scripts/monitor_iwap_discovery.sh [interval_seconds]

INTERVAL=${1:-60}  # Default 60 seconds
UID=160
LOG_FILE="/tmp/iwap_discovery.log"
ALERT_SENT=false

echo "🔍 Monitoring IWAP for UID 160 discovery..."
echo "Checking every ${INTERVAL} seconds..."
echo "Log: $LOG_FILE"
echo ""

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Check IWAP agents page for UID 160
    RESPONSE=$(curl -s "https://infinitewebarena.autoppia.com/subnet36/agents" 2>&1)
    
    if echo "$RESPONSE" | grep -q "UID: 160\|UID: $UID"; then
        if [ "$ALERT_SENT" = false ]; then
            echo "🎉🎉🎉 UID 160 DISCOVERED ON IWAP! 🎉🎉🎉"
            echo "[$TIMESTAMP] UID 160 is now visible on IWAP!"
            echo "$RESPONSE" | grep -A 5 -B 5 "UID: 160\|UID: $UID" | head -20
            echo ""
            echo "View at: https://infinitewebarena.autoppia.com/subnet36/agents"
            echo ""
            
            # Log to file
            echo "[$TIMESTAMP] UID 160 DISCOVERED" >> "$LOG_FILE"
            echo "$RESPONSE" | grep -A 10 "UID: 160\|UID: $UID" >> "$LOG_FILE"
            
            ALERT_SENT=true
        fi
    else
        if [ "$ALERT_SENT" = false ]; then
            echo "[$TIMESTAMP] Still waiting for discovery... (UID 160 not found)"
        fi
    fi
    
    sleep "$INTERVAL"
done

