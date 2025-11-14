#!/bin/bash

# 🚀 One-Command Deployment Script for DigitalOcean
# Run this on your DigitalOcean droplet after SSH'ing in

set -e

DROPLET_IP="134.199.201.62"
API_PORT="8080"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🚀 Autoppia API - DigitalOcean Deployment 🚀          ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

echo "📦 Step 1: Updating system..."
apt update && apt upgrade -y

echo ""
echo "📦 Step 2: Installing dependencies..."
apt install -y python3 python3-pip git curl ufw

echo ""
echo "📦 Step 3: Cloning repository..."
if [ -d "autoppia-miner" ]; then
    echo "⚠️  Directory exists, updating..."
    cd autoppia-miner
    git pull
else
    git clone https://github.com/irun2themoney/autoppia-miner.git
    cd autoppia-miner
fi

echo ""
echo "📦 Step 4: Installing Python packages..."
pip3 install -r requirements.txt

echo ""
echo "⚙️  Step 5: Setting up environment..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: You need to add your CHUTES_API_KEY to .env"
    echo "   Run: nano .env"
    echo "   Add: CHUTES_API_KEY=your_key_here"
    echo ""
    read -p "Press Enter after you've added your API key to .env..."
fi

echo ""
echo "🔥 Step 6: Configuring firewall..."
ufw allow 22/tcp
ufw allow $API_PORT/tcp
ufw --force enable
echo "✅ Firewall configured"

echo ""
echo "⚙️  Step 7: Creating systemd service..."
cat > /etc/systemd/system/autoppia-api.service << EOF
[Unit]
Description=Autoppia HTTP API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="PORT=$API_PORT"
ExecStart=/usr/bin/python3 $(pwd)/api.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "🚀 Step 8: Starting service..."
systemctl daemon-reload
systemctl enable autoppia-api
systemctl start autoppia-api

echo ""
echo "⏳ Waiting for service to start..."
sleep 5

if systemctl is-active --quiet autoppia-api; then
    echo "✅ Service is running!"
else
    echo "❌ Service failed to start. Checking logs..."
    journalctl -u autoppia-api -n 20
    exit 1
fi

echo ""
echo "🧪 Step 9: Testing endpoint..."
sleep 2
if curl -s -f http://localhost:$API_PORT/health > /dev/null; then
    echo "✅ Health check passed!"
else
    echo "⚠️  Health check failed. Service may still be starting..."
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        ✅ DEPLOYMENT COMPLETE! ✅                              ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Your Endpoint:"
echo "   IP: $DROPLET_IP"
echo "   Port: $API_PORT"
echo "   Endpoint: $DROPLET_IP:$API_PORT"
echo ""
echo "🎯 For InfiniteWeb Arena:"
echo "   Use: $DROPLET_IP:$API_PORT"
echo ""
echo "🧪 Test from your local machine:"
echo "   curl http://$DROPLET_IP:$API_PORT/health"
echo ""
echo "📝 Useful Commands:"
echo "   View logs: journalctl -u autoppia-api -f"
echo "   Check status: systemctl status autoppia-api"
echo "   Restart: systemctl restart autoppia-api"
echo ""
echo "🔥 IMPORTANT: Configure DigitalOcean Firewall:"
echo "   1. Go to: https://cloud.digitalocean.com/networking/firewalls"
echo "   2. Create/Edit firewall"
echo "   3. Add rule: Custom TCP ($API_PORT) - Allow"
echo "   4. Apply to your droplet"
echo ""

