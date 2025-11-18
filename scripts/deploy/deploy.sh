#!/bin/bash
# Deployment script for Autoppia Miner

set -e

echo "🚀 Deploying Autoppia Miner..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}.env file not found!${NC}"
    echo "Please copy env.example to .env and configure it"
    exit 1
fi

# Activate virtual environment
if [ -d venv ]; then
    source venv/bin/activate
else
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
fi

# Install/update dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Reload systemd
echo -e "${YELLOW}Reloading systemd...${NC}"
systemctl daemon-reload

# Restart services
echo -e "${YELLOW}Restarting services...${NC}"
systemctl restart autoppia-api || echo -e "${YELLOW}API service not found, skipping...${NC}"
systemctl restart autoppia-miner || echo -e "${YELLOW}Miner service not found, skipping...${NC}"

# Wait a moment
sleep 3

# Check status
echo -e "${YELLOW}Checking service status...${NC}"
systemctl status autoppia-api --no-pager -l || true
systemctl status autoppia-miner --no-pager -l || true

# Test API
echo -e "${YELLOW}Testing API...${NC}"
sleep 2
if curl -s http://localhost:8080/health > /dev/null; then
    echo -e "${GREEN}✅ API is responding!${NC}"
else
    echo -e "${RED}❌ API is not responding${NC}"
    echo "Check logs: journalctl -u autoppia-api -f"
fi

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Next steps:"
echo "  - Monitor logs: journalctl -u autoppia-api -f"
echo "  - Check dashboard: http://$(hostname -I | awk '{print $1}'):8080/dashboard"
echo "  - Run tests: ./scripts/run_ultimate_test.sh"

