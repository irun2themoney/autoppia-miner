#!/bin/bash

# 🚀 One-Command Deployment Script for Bittensor Miner on DigitalOcean
# Run this on your DigitalOcean droplet after SSH'ing in

set -e

AXON_PORT="8091"
WALLET_NAME="${1:-default}"
HOTKEY_NAME="${2:-default}"
NETWORK="${3:-finney}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║     🚀 Autoppia Bittensor Miner - DigitalOcean Setup 🚀      ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

echo "📋 Configuration:"
echo "   Wallet: $WALLET_NAME"
echo "   Hotkey: $HOTKEY_NAME"
echo "   Network: $NETWORK"
echo "   Axon Port: $AXON_PORT"
echo ""

# Get droplet IP
DROPLET_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "YOUR_IP_HERE")
echo "🌐 Detected IP: $DROPLET_IP"
echo ""

echo "📦 Step 1: Updating system..."
apt update && apt upgrade -y

echo ""
echo "📦 Step 2: Installing dependencies..."
apt install -y python3 python3-pip git curl ufw screen

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
fi

# Update API_URL to use localhost (API runs on same droplet)
sed -i "s|API_URL=.*|API_URL=http://localhost:8080|" .env
echo "✅ Configured API_URL=http://localhost:8080"

echo ""
echo "🔐 Step 6: Checking wallet setup..."
if ! command -v btcli &> /dev/null; then
    echo "⚠️  btcli not found. Installing bittensor..."
    pip3 install bittensor
fi

# Check if wallet exists
if ! btcli wallet list 2>/dev/null | grep -q "$WALLET_NAME"; then
    echo "⚠️  Wallet '$WALLET_NAME' not found!"
    echo ""
    echo "You have two options:"
    echo "  1. Copy wallet from local machine:"
    echo "     scp -r ~/.bittensor/wallets/$WALLET_NAME root@$DROPLET_IP:~/.bittensor/wallets/"
    echo ""
    echo "  2. Create new wallet on VPS:"
    echo "     btcli wallet create --name $WALLET_NAME"
    echo ""
    read -p "Press Enter after you've set up your wallet..."
fi

echo ""
echo "🔍 Step 7: Checking registration on subnet 36..."
REGISTERED=$(btcli wallet overview --netuid 36 --wallet.name "$WALLET_NAME" --wallet.hotkey "$HOTKEY_NAME" 2>/dev/null | grep -c "UID:" || echo "0")

if [ "$REGISTERED" -eq "0" ]; then
    echo "⚠️  Not registered on subnet 36!"
    echo ""
    echo "You need to register first:"
    echo "   btcli subnet register --netuid 36 --wallet.name $WALLET_NAME --wallet.hotkey $HOTKEY_NAME"
    echo ""
    echo "⚠️  This requires TAO tokens for registration fees."
    echo ""
    read -p "Press Enter after you've registered (or Ctrl+C to exit)..."
else
    echo "✅ Wallet is registered on subnet 36"
    btcli wallet overview --netuid 36 --wallet.name "$WALLET_NAME" --wallet.hotkey "$HOTKEY_NAME" | grep "UID:"
fi

echo ""
echo "🔥 Step 8: Configuring firewall..."
ufw allow 22/tcp
ufw allow 8080/tcp  # API port
ufw allow $AXON_PORT/tcp  # Axon port
ufw --force enable
echo "✅ Firewall configured (SSH: 22, API: 8080, Axon: $AXON_PORT)"

echo ""
echo "⚙️  Step 9: Creating API service..."
WORK_DIR=$(pwd)
cat > /etc/systemd/system/autoppia-api.service << EOF
[Unit]
Description=Autoppia API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$WORK_DIR
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/usr/bin/python3 $WORK_DIR/api.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "⚙️  Step 10: Creating miner service..."
cat > /etc/systemd/system/autoppia-miner.service << EOF
[Unit]
Description=Autoppia Bittensor Miner
After=network.target autoppia-api.service
Requires=autoppia-api.service

[Service]
Type=simple
User=root
WorkingDirectory=$WORK_DIR
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/usr/bin/python3 $WORK_DIR/miner.py --wallet.name $WALLET_NAME --wallet.hotkey $HOTKEY_NAME --network $NETWORK --axon.port $AXON_PORT
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "🚀 Step 11: Starting services..."
systemctl daemon-reload

# Start API first
echo "   Starting API service..."
systemctl enable autoppia-api
systemctl start autoppia-api
sleep 3

# Check API is running
if systemctl is-active --quiet autoppia-api; then
    echo "✅ API service is running!"
else
    echo "❌ API service failed to start. Checking logs..."
    journalctl -u autoppia-api -n 30
    echo ""
    echo "⚠️  Please check the logs above and fix any issues."
    exit 1
fi

# Start miner
echo "   Starting miner service..."
systemctl enable autoppia-miner
systemctl start autoppia-miner

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

if systemctl is-active --quiet autoppia-miner; then
    echo "✅ Miner service is running!"
else
    echo "❌ Miner service failed to start. Checking logs..."
    journalctl -u autoppia-miner -n 30
    echo ""
    echo "⚠️  Please check the logs above and fix any issues."
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        ✅ MINER DEPLOYMENT COMPLETE! ✅                        ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Your Configuration:"
echo "   IP: $DROPLET_IP"
echo "   API Port: 8080"
echo "   Axon Port: $AXON_PORT"
echo "   Wallet: $WALLET_NAME"
echo "   Hotkey: $HOTKEY_NAME"
echo "   Network: $NETWORK"
echo ""
echo "🌐 Endpoints:"
echo "   API: http://$DROPLET_IP:8080"
echo "   Miner Axon: $DROPLET_IP:$AXON_PORT"
echo ""
echo "📝 Useful Commands:"
echo "   API logs: journalctl -u autoppia-api -f"
echo "   Miner logs: journalctl -u autoppia-miner -f"
echo "   API status: systemctl status autoppia-api"
echo "   Miner status: systemctl status autoppia-miner"
echo "   Restart API: systemctl restart autoppia-api"
echo "   Restart Miner: systemctl restart autoppia-miner"
echo ""
echo "🔍 Check Miner Status:"
echo "   btcli wallet overview --netuid 36 --wallet.name $WALLET_NAME --wallet.hotkey $HOTKEY_NAME"
echo ""
echo "🔥 IMPORTANT: Configure DigitalOcean Firewall:"
echo "   1. Go to: https://cloud.digitalocean.com/networking/firewalls"
echo "   2. Create/Edit firewall"
echo "   3. Add rules:"
echo "      - Custom TCP (8080) - Allow from All IPv4 (for API)"
echo "      - Custom TCP ($AXON_PORT) - Allow from All IPv4 (for Miner)"
echo "   4. Apply to your droplet"
echo ""
echo "✅ Your services are now running 24/7:"
echo "   - API server on port 8080 (processes IWA tasks)"
echo "   - Miner connected to Bittensor subnet 36"
echo "   - Miner forwards validator requests to local API"
echo "   - Earn TAO rewards based on performance"
echo ""
echo "🧪 Test your API:"
echo "   curl http://localhost:8080/health"
echo "   curl http://$DROPLET_IP:8080/health"
echo ""

