#!/bin/bash

# 🚀 Quick VPS Deployment Script for Autoppia HTTP API
# This script helps set up the API server on a VPS

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🚀 Autoppia API VPS Deployment Script 🚀               ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

# Get configuration
read -p "Enter API port (default: 8080): " API_PORT
API_PORT=${API_PORT:-8080}

read -p "Enter working directory (default: /root/autoppia-miner): " WORK_DIR
WORK_DIR=${WORK_DIR:-/root/autoppia-miner}

read -p "Enter Python path (default: /usr/bin/python3): " PYTHON_PATH
PYTHON_PATH=${PYTHON_PATH:-/usr/bin/python3}

echo ""
echo -e "${YELLOW}📋 Configuration:${NC}"
echo "   Port: $API_PORT"
echo "   Directory: $WORK_DIR"
echo "   Python: $PYTHON_PATH"
echo ""

# Step 1: Update system
echo -e "${GREEN}📦 Step 1: Updating system...${NC}"
apt update && apt upgrade -y

# Step 2: Install dependencies
echo -e "${GREEN}📦 Step 2: Installing dependencies...${NC}"
apt install -y python3 python3-pip git curl ufw

# Step 3: Install Python packages
echo -e "${GREEN}📦 Step 3: Installing Python packages...${NC}"
if [ -f "$WORK_DIR/requirements.txt" ]; then
    pip3 install -r "$WORK_DIR/requirements.txt"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found. Installing basic packages...${NC}"
    pip3 install fastapi uvicorn loguru python-dotenv httpx pydantic
fi

# Step 4: Configure firewall
echo -e "${GREEN}🔥 Step 4: Configuring firewall...${NC}"
ufw allow 22/tcp
ufw allow $API_PORT/tcp
ufw --force enable
echo -e "${GREEN}✅ Firewall configured${NC}"

# Step 5: Create systemd service
echo -e "${GREEN}⚙️  Step 5: Creating systemd service...${NC}"
cat > /etc/systemd/system/autoppia-api.service << EOF
[Unit]
Description=Autoppia HTTP API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$WORK_DIR
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="PORT=$API_PORT"
ExecStart=$PYTHON_PATH $WORK_DIR/api.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Step 6: Enable and start service
echo -e "${GREEN}🚀 Step 6: Starting service...${NC}"
systemctl daemon-reload
systemctl enable autoppia-api
systemctl start autoppia-api

# Step 7: Wait a moment and check status
sleep 3
if systemctl is-active --quiet autoppia-api; then
    echo -e "${GREEN}✅ Service is running!${NC}"
else
    echo -e "${RED}❌ Service failed to start. Check logs:${NC}"
    echo "   journalctl -u autoppia-api -n 50"
    exit 1
fi

# Step 8: Get public IP
echo ""
echo -e "${GREEN}🌐 Step 7: Getting public IP...${NC}"
PUBLIC_IP=$(curl -s -4 ifconfig.me || curl -s ifconfig.me || echo "unknown")
echo -e "${GREEN}✅ Your public IP: $PUBLIC_IP${NC}"

# Step 9: Test endpoint
echo ""
echo -e "${GREEN}🧪 Step 8: Testing endpoint...${NC}"
sleep 2
if curl -s -f http://localhost:$API_PORT/health > /dev/null; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${YELLOW}⚠️  Health check failed. Service may still be starting...${NC}"
fi

# Summary
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        ✅ DEPLOYMENT COMPLETE! ✅                              ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}📋 Summary:${NC}"
echo "   Service: autoppia-api"
echo "   Status: $(systemctl is-active autoppia-api)"
echo "   Port: $API_PORT"
echo "   Public IP: $PUBLIC_IP"
echo "   Endpoint: $PUBLIC_IP:$API_PORT"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "   1. Test endpoint: curl http://$PUBLIC_IP:$API_PORT/health"
echo "   2. Configure in InfiniteWeb Arena: $PUBLIC_IP:$API_PORT"
echo "   3. View logs: journalctl -u autoppia-api -f"
echo "   4. Check status: systemctl status autoppia-api"
echo ""
echo -e "${YELLOW}🔧 Useful Commands:${NC}"
echo "   Restart: systemctl restart autoppia-api"
echo "   Stop: systemctl stop autoppia-api"
echo "   Logs: journalctl -u autoppia-api -f"
echo ""

