#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to clear screen and show header
clear_screen() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BLUE}Autoppia Miner Monitor${NC} - Refreshing every 60 seconds      ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to get miner status
get_miner_status() {
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📊 MINER STATUS${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    pm2 status autoppia_miner 2>/dev/null | grep -E "(autoppia_miner|online|errored|stopped)" || echo "Miner not found"
    echo ""
}

# Function to get recent activity
get_recent_activity() {
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📝 RECENT ACTIVITY (Last 15 lines)${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    pm2 logs autoppia_miner --lines 15 --nostream 2>&1 | tail -15 | sed 's/.*autoppia | //' | tail -15
    echo ""
}

# Function to get wallet balance
get_wallet_balance() {
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}💰 WALLET BALANCE${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    btcli wallet balance --wallet.name default 2>&1 | grep -E "(Free|Stake|Total|Wallet)" || echo "Unable to fetch balance"
    echo ""
}

# Function to get worker health
get_worker_health() {
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🏥 WORKER HEALTH${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    HEALTH=$(curl -s https://autoppia-miner.onrender.com/health 2>&1)
    if echo "$HEALTH" | grep -q "healthy"; then
        echo -e "${GREEN}✅ Worker is healthy${NC}"
    else
        echo -e "${RED}⚠️  Worker may have issues${NC}"
    fi
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
    echo ""
}

# Function to check for tasks
check_task_activity() {
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📋 TASK ACTIVITY${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    RECENT_LOGS=$(pm2 logs autoppia_miner --lines 50 --nostream 2>&1)
    
    TASK_COUNT=$(echo "$RECENT_LOGS" | grep -i "task\|forward\|synapse" | wc -l | tr -d ' ')
    ERROR_COUNT=$(echo "$RECENT_LOGS" | grep -i "error\|failed\|exception" | wc -l | tr -d ' ')
    
    echo -e "Tasks/Activity mentions: ${CYAN}$TASK_COUNT${NC}"
    echo -e "Errors/Warnings: ${RED}$ERROR_COUNT${NC}"
    
    # Show last few task-related entries
    echo ""
    echo "Recent task-related activity:"
    echo "$RECENT_LOGS" | grep -i "task\|forward\|synapse\|received\|completed" | tail -5 | sed 's/.*autoppia | //' || echo "No recent task activity"
    echo ""
}

# Function to show timestamp
show_timestamp() {
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "Last updated: ${CYAN}$(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "Next refresh in: ${CYAN}60 seconds${NC} (Press Ctrl+C to exit)"
    echo ""
}

# Main monitoring loop
while true; do
    clear_screen
    get_miner_status
    get_wallet_balance
    get_worker_health
    check_task_activity
    get_recent_activity
    show_timestamp
    
    # Wait 60 seconds before next refresh
    sleep 60
done

