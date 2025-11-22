#!/bin/bash
# Service Health Check and Auto-Restart Script
# Ensures miner and API services stay running

set -e

LOG_FILE="/var/log/autoppia-health-check.log"
MAX_RESTARTS=5
RESTART_COUNT_FILE="/tmp/autoppia-restart-count"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if service is running
check_service() {
    local service_name=$1
    if systemctl is-active --quiet "$service_name"; then
        return 0  # Service is running
    else
        return 1  # Service is not running
    fi
}

# Restart service with rate limiting
restart_service() {
    local service_name=$1
    
    # Check restart count
    local count=0
    if [ -f "$RESTART_COUNT_FILE" ]; then
        count=$(cat "$RESTART_COUNT_FILE")
    fi
    
    if [ "$count" -ge "$MAX_RESTARTS" ]; then
        log "ERROR: $service_name has restarted $count times. Stopping auto-restart to prevent loop."
        return 1
    fi
    
    log "WARNING: $service_name is not running. Restarting..."
    systemctl restart "$service_name"
    sleep 5
    
    if check_service "$service_name"; then
        log "SUCCESS: $service_name restarted successfully"
        echo $((count + 1)) > "$RESTART_COUNT_FILE"
        return 0
    else
        log "ERROR: Failed to restart $service_name"
        echo $((count + 1)) > "$RESTART_COUNT_FILE"
        return 1
    fi
}

# Reset restart count if services have been stable
reset_restart_count() {
    if [ -f "$RESTART_COUNT_FILE" ]; then
        rm "$RESTART_COUNT_FILE"
        log "INFO: Restart count reset (services stable)"
    fi
}

# Main health check
main() {
    log "INFO: Starting health check..."
    
    local api_ok=true
    local miner_ok=true
    
    # Check API service
    if ! check_service "autoppia-api"; then
        api_ok=false
        restart_service "autoppia-api"
    fi
    
    # Check miner service (only if API is running)
    if [ "$api_ok" = true ] && ! check_service "autoppia-miner"; then
        miner_ok=false
        restart_service "autoppia-miner"
    fi
    
    # If both services are running, reset restart count
    if [ "$api_ok" = true ] && [ "$miner_ok" = true ]; then
        reset_restart_count
        log "INFO: All services healthy"
    fi
    
    # Check if services are enabled
    if ! systemctl is-enabled --quiet autoppia-api; then
        log "WARNING: autoppia-api is not enabled. Enabling..."
        systemctl enable autoppia-api
    fi
    
    if ! systemctl is-enabled --quiet autoppia-miner; then
        log "WARNING: autoppia-miner is not enabled. Enabling..."
        systemctl enable autoppia-miner
    fi
}

# Run health check
main

exit 0

