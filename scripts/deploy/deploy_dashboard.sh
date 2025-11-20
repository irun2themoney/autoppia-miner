#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting Dashboard Deployment...${NC}"

# Server details
SERVER_IP="134.199.203.133"
USER="root"
REMOTE_DIR="/opt/autoppia-miner"

echo -e "${YELLOW}📡 Connecting to ${SERVER_IP}...${NC}"

ssh -t $USER@$SERVER_IP "bash -c '
    set -e
    cd $REMOTE_DIR
    
    echo -e \"${YELLOW}📥 Pulling latest dashboard code...${NC}\"
    # Stash any local changes just in case
    git stash
    git pull origin main
    
    echo -e \"${YELLOW}📦 Installing dependencies...${NC}\"
    source venv/bin/activate
    pip install -r requirements.txt
    
    echo -e \"${YELLOW}🔄 Restarting API service...${NC}\"
    systemctl restart autoppia-api
    
    # Check if miner is still running (it might restart due to dependency, which is fine)
    if systemctl is-active --quiet autoppia-miner; then
        echo -e \"${GREEN}✅ Miner is active.${NC}\"
    else
        echo -e \"${YELLOW}⚠️ Miner stopped (likely due to dependency). Restarting miner...${NC}\"
        systemctl restart autoppia-miner
    fi
    
    echo -e \"${GREEN}✨ Dashboard deployed successfully!${NC}\"
    echo -e \"📊 View it at: http://${SERVER_IP}:8080/api/dashboard\"
'"

echo -e "${GREEN}✅ Deployment sequence complete.${NC}"
