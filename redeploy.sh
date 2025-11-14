#!/bin/bash
# 🚀 Quick Redeploy Script for Rebuilt Droplet
# Run this on your fresh DigitalOcean droplet

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🚀 QUICK REDEPLOY - REBUILT DROPLET 🚀                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Get droplet IP
DROPLET_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || hostname -I | awk '{print $1}')
echo "🌐 Detected IP: $DROPLET_IP"
echo ""

echo "📦 Step 1: Updating system..."
apt update && apt upgrade -y

echo ""
echo "📦 Step 2: Installing dependencies..."
apt install -y python3 python3-pip git curl ufw

echo ""
echo "📦 Step 3: Cloning repository..."
cd /opt
rm -rf autoppia-miner 2>/dev/null || true
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner

echo ""
echo "📦 Step 4: Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "⚙️  Step 5: Creating .env file..."
cat > .env << 'EOF'
# AI Provider (Chutes API)
CHUTES_API_KEY=cpk_384e5ee3477b4345be53ecb6cf5336d6.97cdedde58e45965820657bd8ec790fa.Op9UfWviGGaAKmInl8xqTeKHTUjx8z2n
CHUTES_API_URL=https://api.chutes.ai

# Worker Configuration
WORKER_NAME=autoppia-miner
WORKER_VERSION=0.1.0
WORKER_DESCRIPTION=Autoppia AI Worker

# Miner Configuration
API_URL=http://134.199.203.133:8080
PORT=8080

# Logging
LOG_LEVEL=INFO
CORS_ORIGINS=*
EOF

# Update API_URL if IP changed
if [ "$DROPLET_IP" != "134.199.203.133" ]; then
    echo "⚠️  IP changed to $DROPLET_IP, updating .env..."
    sed -i "s|API_URL=http://134.199.203.133:8080|API_URL=http://$DROPLET_IP:8080|g" .env
fi

echo "✅ .env file created"

echo ""
echo "📁 Step 6: Creating logs directory..."
mkdir -p logs

echo ""
echo "🔥 Step 7: Configuring firewall..."
ufw allow 22/tcp
ufw allow 8080/tcp
ufw allow 8091/tcp
ufw --force enable
echo "✅ Firewall configured"

echo ""
echo "⚙️  Step 8: Creating systemd service..."
cat > /etc/systemd/system/autoppia-api.service << SERVICEEOF
[Unit]
Description=Autoppia HTTP API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/autoppia-miner
Environment="PATH=/opt/autoppia-miner/venv/bin:/usr/bin:/usr/local/bin"
Environment="PORT=8080"
ExecStart=/opt/autoppia-miner/venv/bin/python3 /opt/autoppia-miner/api.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICEEOF

echo ""
echo "🚀 Step 9: Starting API service..."
systemctl daemon-reload
systemctl enable autoppia-api
systemctl start autoppia-api

echo ""
echo "⏳ Waiting for service to start..."
sleep 5

echo ""
echo "🔍 Step 10: Verifying deployment..."
if systemctl is-active --quiet autoppia-api; then
    echo "✅ API service is running!"
else
    echo "❌ Service failed to start. Checking logs..."
    journalctl -u autoppia-api -n 30
    exit 1
fi

echo ""
echo "🧪 Testing API..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ API is responding!"
    curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8080/health
else
    echo "⚠️  API not responding. Check logs: journalctl -u autoppia-api -n 50"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    ✅ DEPLOYMENT COMPLETE! ✅                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Configuration:"
echo "   IP: $DROPLET_IP"
echo "   API Endpoint: http://$DROPLET_IP:8080"
echo ""
echo "🔍 Next Steps:"
echo "   1. Configure DigitalOcean Firewall:"
echo "      - Go to: https://cloud.digitalocean.com/networking/firewalls"
echo "      - Add inbound rule: Custom TCP 8080 (All IPv4)"
echo "      - Apply to your droplet"
echo ""
echo "   2. Test from InfiniteWeb Arena:"
echo "      Endpoint: $DROPLET_IP:8080"
echo ""
echo "   3. View logs:"
echo "      journalctl -u autoppia-api -f"
echo ""
echo "   4. Check status:"
echo "      systemctl status autoppia-api"
echo ""

