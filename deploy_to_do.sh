#!/bin/bash

# DigitalOcean VPS Deployment Script for Autoppia Miner
# This script deploys both the API and Miner to a DigitalOcean VPS
# Usage: ./deploy_to_do.sh [API_ONLY|MINER_ONLY|BOTH] [wallet_name] [hotkey_name]

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🚀 AUTOPPIA MINER - DIGITALOCEAN DEPLOYMENT 🚀          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Parse arguments
DEPLOY_MODE=${1:-"BOTH"}
WALLET_NAME=${2:-"default"}
HOTKEY_NAME=${3:-"default"}

if [[ ! "$DEPLOY_MODE" =~ ^(API_ONLY|MINER_ONLY|BOTH)$ ]]; then
    echo -e "${RED}❌ Invalid deploy mode: $DEPLOY_MODE${NC}"
    echo "   Usage: ./deploy_to_do.sh [API_ONLY|MINER_ONLY|BOTH] [wallet_name] [hotkey_name]"
    exit 1
fi

echo -e "${YELLOW}Deploy Mode:${NC} $DEPLOY_MODE"
echo -e "${YELLOW}Wallet:${NC} $WALLET_NAME"
echo -e "${YELLOW}Hotkey:${NC} $HOTKEY_NAME"
echo ""

# 1. System Updates
echo -e "${BLUE}[1/6]${NC} Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y curl wget git build-essential python3-dev python3-pip python3-venv

# 2. Clone/Update Repository
echo -e "${BLUE}[2/6]${NC} Setting up repository..."
if [ ! -d "/opt/autoppia-miner" ]; then
    echo "   Cloning repository..."
    sudo git clone https://github.com/irun2themoney/autoppia-miner.git /opt/autoppia-miner
else
    echo "   Updating existing repository..."
    sudo git -C /opt/autoppia-miner pull origin main
fi
sudo chown -R $USER:$USER /opt/autoppia-miner
cd /opt/autoppia-miner

# 3. Setup Python Environment
echo -e "${BLUE}[3/6]${NC} Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure Environment
echo -e "${BLUE}[4/6]${NC} Configuring environment..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo -e "${YELLOW}⚠️  .env file created. Please edit and add your CHUTES_API_KEY:${NC}"
    echo "   sudo nano /opt/autoppia-miner/.env"
else
    echo "   .env file already exists"
fi

# 5. Deploy API Server (if needed)
if [[ "$DEPLOY_MODE" == "API_ONLY" ]] || [[ "$DEPLOY_MODE" == "BOTH" ]]; then
    echo -e "${BLUE}[5/6]${NC} Deploying API Server..."
    
    # Create systemd service for API
    sudo tee /etc/systemd/system/autoppia-api.service > /dev/null <<EOF
[Unit]
Description=Autoppia Miner API Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/autoppia-miner
Environment="PATH=/opt/autoppia-miner/venv/bin"
Environment="PORT=8000"
ExecStart=/opt/autoppia-miner/venv/bin/python3 /opt/autoppia-miner/api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable autoppia-api
    sudo systemctl restart autoppia-api
    echo -e "${GREEN}✅ API Server configured${NC}"
    echo "   Status: systemctl status autoppia-api"
    echo "   Logs: journalctl -u autoppia-api -f"
fi

# 6. Deploy Miner (if needed)
if [[ "$DEPLOY_MODE" == "MINER_ONLY" ]] || [[ "$DEPLOY_MODE" == "BOTH" ]]; then
    echo -e "${BLUE}[6/6]${NC} Deploying Bittensor Miner..."
    
    # Create systemd service for Miner
    sudo tee /etc/systemd/system/autoppia-miner.service > /dev/null <<EOF
[Unit]
Description=Autoppia Bittensor Miner
After=network.target autoppia-api.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/autoppia-miner
Environment="PATH=/opt/autoppia-miner/venv/bin"
ExecStart=/opt/autoppia-miner/venv/bin/python3 /opt/autoppia-miner/miner.py --wallet.name $WALLET_NAME --wallet.hotkey $HOTKEY_NAME --network finney --axon.port 8091
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable autoppia-miner
    sudo systemctl restart autoppia-miner
    echo -e "${GREEN}✅ Miner configured${NC}"
    echo "   Status: systemctl status autoppia-miner"
    echo "   Logs: journalctl -u autoppia-miner -f"
fi

# 7. Firewall Setup
echo -e "${BLUE}[7/7]${NC} Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 8000/tcp  # API
sudo ufw allow 8091/tcp  # Miner axon
sudo ufw enable -y || true
echo -e "${GREEN}✅ Firewall configured${NC}"

# Summary
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✅ DEPLOYMENT COMPLETED SUCCESSFULLY ✅             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [[ "$DEPLOY_MODE" == "API_ONLY" ]] || [[ "$DEPLOY_MODE" == "BOTH" ]]; then
    echo -e "${YELLOW}API Server:${NC}"
    echo "   URL: http://$(hostname -I | awk '{print $1}'):8000"
    echo "   Health: curl http://localhost:8000/health"
    echo "   Logs: sudo journalctl -u autoppia-api -f"
    echo ""
fi

if [[ "$DEPLOY_MODE" == "MINER_ONLY" ]] || [[ "$DEPLOY_MODE" == "BOTH" ]]; then
    echo -e "${YELLOW}Bittensor Miner:${NC}"
    echo "   Wallet: $WALLET_NAME"
    echo "   Hotkey: $HOTKEY_NAME"
    echo "   Status: sudo systemctl status autoppia-miner"
    echo "   Logs: sudo journalctl -u autoppia-miner -f"
    echo ""
fi

echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Edit .env file: sudo nano /opt/autoppia-miner/.env"
echo "2. Add your CHUTES_API_KEY"
echo "3. Set API_URL if running separately"
echo "4. Restart services: sudo systemctl restart autoppia-api autoppia-miner"
echo ""

echo -e "${BLUE}Configuration Files:${NC}"
echo "   API Service: /etc/systemd/system/autoppia-api.service"
echo "   Miner Service: /etc/systemd/system/autoppia-miner.service"
echo "   Environment: /opt/autoppia-miner/.env"
echo ""

echo -e "${GREEN}Deployment complete! 🎉${NC}"

