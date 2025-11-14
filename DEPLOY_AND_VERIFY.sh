#!/bin/bash
# Deploy and verify miner on DigitalOcean droplet

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🚀 DEPLOY & VERIFY MINER 🚀                           ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DROPLET_IP="134.199.203.133"
WORK_DIR="/opt/autoppia-miner"

echo "📋 Deployment Checklist:"
echo "  1. Pull latest code"
echo "  2. Install/update dependencies"
echo "  3. Update systemd services (if needed)"
echo "  4. Restart services"
echo "  5. Verify API is running"
echo "  6. Verify miner is running"
echo "  7. Test API endpoints"
echo ""

read -p "Press Enter to start deployment (or Ctrl+C to cancel)..."

echo ""
echo "🔧 Step 1: Pulling latest code..."
cd $WORK_DIR
git pull origin main
echo -e "${GREEN}✅ Code updated${NC}"

echo ""
echo "📦 Step 2: Installing dependencies..."
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

echo ""
echo "⚙️  Step 3: Checking systemd services..."
# Check if services need updating
API_SERVICE="/etc/systemd/system/autoppia-api.service"
MINER_SERVICE="/etc/systemd/system/autoppia-miner.service"

if [ -f "$API_SERVICE" ]; then
    if ! grep -q "python3 -m api.server" "$API_SERVICE"; then
        echo "   Updating API service to use modular structure..."
        sed -i 's|ExecStart=.*api.py|ExecStart=/opt/autoppia-miner/venv/bin/python3 -m api.server|' "$API_SERVICE"
        systemctl daemon-reload
        echo -e "${GREEN}✅ API service updated${NC}"
    else
        echo -e "${GREEN}✅ API service already using modular structure${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  API service not found. Creating...${NC}"
    cat > "$API_SERVICE" << EOF
[Unit]
Description=Autoppia HTTP API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$WORK_DIR
Environment="PATH=$WORK_DIR/venv/bin"
ExecStart=$WORK_DIR/venv/bin/python3 -m api.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable autoppia-api
    echo -e "${GREEN}✅ API service created${NC}"
fi

if [ -f "$MINER_SERVICE" ]; then
    if ! grep -q "python3 -m miner.miner" "$MINER_SERVICE"; then
        echo "   Updating miner service to use modular structure..."
        sed -i 's|ExecStart=.*miner.py|ExecStart=/opt/autoppia-miner/venv/bin/python3 -m miner.miner|' "$MINER_SERVICE"
        systemctl daemon-reload
        echo -e "${GREEN}✅ Miner service updated${NC}"
    else
        echo -e "${GREEN}✅ Miner service already using modular structure${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Miner service not found. Please create it manually.${NC}"
fi

echo ""
echo "🔄 Step 4: Restarting services..."
systemctl restart autoppia-api
sleep 3
systemctl restart autoppia-miner
sleep 3
echo -e "${GREEN}✅ Services restarted${NC}"

echo ""
echo "🔍 Step 5: Verifying services..."
echo ""

# Check API service
if systemctl is-active --quiet autoppia-api; then
    echo -e "${GREEN}✅ API service is running${NC}"
else
    echo -e "${RED}❌ API service is not running${NC}"
    echo "   Checking logs..."
    journalctl -u autoppia-api -n 20 --no-pager
    exit 1
fi

# Check miner service
if systemctl is-active --quiet autoppia-miner; then
    echo -e "${GREEN}✅ Miner service is running${NC}"
else
    echo -e "${RED}❌ Miner service is not running${NC}"
    echo "   Checking logs..."
    journalctl -u autoppia-miner -n 20 --no-pager
    exit 1
fi

echo ""
echo "🧪 Step 6: Testing API endpoints..."
echo ""

# Test health endpoint
echo "   Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8080/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "   Response: $HEALTH_RESPONSE"
    exit 1
fi

# Test solve_task endpoint
echo ""
echo "   Testing /solve_task endpoint..."
TASK_RESPONSE=$(curl -s -X POST http://localhost:8080/solve_task \
    -H "Content-Type: application/json" \
    -d '{"id":"test-123","prompt":"Switch to month view","url":"https://example.com"}')

if echo "$TASK_RESPONSE" | grep -q "actions"; then
    echo -e "${GREEN}✅ Solve task endpoint working${NC}"
    ACTION_COUNT=$(echo "$TASK_RESPONSE" | grep -o '"type"' | wc -l)
    echo "   Generated $ACTION_COUNT actions"
else
    echo -e "${RED}❌ Solve task endpoint failed${NC}"
    echo "   Response: $TASK_RESPONSE"
    exit 1
fi

echo ""
echo "📊 Step 7: Checking ports..."
if ss -tlnp 2>/dev/null | grep -q ":8080"; then
    echo -e "${GREEN}✅ API listening on port 8080${NC}"
else
    echo -e "${YELLOW}⚠️  Port 8080 not found (may need netstat)${NC}"
fi

if ss -tlnp 2>/dev/null | grep -q ":8091"; then
    echo -e "${GREEN}✅ Miner listening on port 8091${NC}"
else
    echo -e "${YELLOW}⚠️  Port 8091 not found (may need netstat)${NC}"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        ✅ DEPLOYMENT SUCCESSFUL! ✅                          ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Summary:"
echo "  ✅ Code updated"
echo "  ✅ Dependencies installed"
echo "  ✅ Services running"
echo "  ✅ API responding"
echo "  ✅ Endpoints working"
echo ""
echo "🔗 Access:"
echo "  API: http://$DROPLET_IP:8080"
echo "  Health: http://$DROPLET_IP:8080/health"
echo ""
echo "📊 Monitor:"
echo "  API logs: journalctl -u autoppia-api -f"
echo "  Miner logs: journalctl -u autoppia-miner -f"
echo "  Status: systemctl status autoppia-api autoppia-miner"
echo ""

