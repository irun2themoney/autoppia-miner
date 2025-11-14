#!/bin/bash
# Quick setup script for Bittensor Miner on VPS
# Run this on your VPS after SSH'ing in

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🚀 Setting Up Bittensor Miner 🚀                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Get wallet/hotkey names (default to 'default' if not provided)
WALLET_NAME="${1:-default}"
HOTKEY_NAME="${2:-default}"

echo "📋 Configuration:"
echo "   Wallet: $WALLET_NAME"
echo "   Hotkey: $HOTKEY_NAME"
echo "   API URL: http://134.199.201.62:8080"
echo ""

# Step 1: Install bittensor
echo "📦 Step 1: Installing bittensor..."
cd /opt/autoppia-miner
source venv/bin/activate
pip install -q bittensor>=7.0.0
echo "✅ Bittensor installed"
echo ""

# Step 2: Verify wallet exists
echo "🔐 Step 2: Checking wallet..."
if ! btcli wallet list 2>/dev/null | grep -q "$WALLET_NAME"; then
    echo "⚠️  Wallet '$WALLET_NAME' not found!"
    echo ""
    echo "You need to copy your wallet to the VPS first:"
    echo "   From your LOCAL machine, run:"
    echo "   scp -r ~/.bittensor/wallets/$WALLET_NAME root@134.199.201.62:~/.bittensor/wallets/"
    echo ""
    exit 1
fi
echo "✅ Wallet found"
echo ""

# Step 3: Verify registration
echo "🔍 Step 3: Verifying registration on subnet 36..."
REGISTERED=$(btcli wallet overview --netuid 36 --wallet.name "$WALLET_NAME" --wallet.hotkey "$HOTKEY_NAME" 2>/dev/null | grep -c "UID:" || echo "0")

if [ "$REGISTERED" -eq "0" ]; then
    echo "⚠️  Not registered on subnet 36!"
    echo "   Please register first with:"
    echo "   btcli subnet register --netuid 36 --wallet.name $WALLET_NAME --wallet.hotkey $HOTKEY_NAME"
    exit 1
else
    echo "✅ Registered on subnet 36"
    btcli wallet overview --netuid 36 --wallet.name "$WALLET_NAME" --wallet.hotkey "$HOTKEY_NAME" | grep "UID:"
fi
echo ""

# Step 4: Verify .env
echo "⚙️  Step 4: Verifying .env configuration..."
if ! grep -q "API_URL=http://134.199.201.62:8080" /opt/autoppia-miner/.env; then
    echo "⚠️  API_URL not set correctly in .env"
    echo "   Updating .env..."
    sed -i 's|API_URL=.*|API_URL=http://134.199.201.62:8080|' /opt/autoppia-miner/.env
    echo "✅ Updated API_URL"
else
    echo "✅ API_URL configured correctly"
fi
echo ""

# Step 5: Open port 8091
echo "🔥 Step 5: Opening port 8091..."
sudo ufw allow 8091/tcp 2>/dev/null || true
sudo ufw reload 2>/dev/null || true
echo "✅ Port 8091 opened"
echo ""

# Step 6: Create miner service
echo "⚙️  Step 6: Creating miner service..."
sudo tee /etc/systemd/system/autoppia-miner.service > /dev/null <<EOF
[Unit]
Description=Autoppia Bittensor Miner
After=network.target autoppia-api.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/autoppia-miner
Environment="PATH=/opt/autoppia-miner/venv/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/opt/autoppia-miner/venv/bin/python3 /opt/autoppia-miner/miner.py --wallet.name $WALLET_NAME --wallet.hotkey $HOTKEY_NAME --network finney --axon.port 8091
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
echo "✅ Service file created"
echo ""

# Step 7: Start miner
echo "🚀 Step 7: Starting miner service..."
sudo systemctl daemon-reload
sudo systemctl enable autoppia-miner
sudo systemctl start autoppia-miner

echo ""
echo "⏳ Waiting for service to start..."
sleep 5

# Step 8: Check status
echo ""
echo "📊 Step 8: Checking service status..."
if systemctl is-active --quiet autoppia-miner; then
    echo "✅ Miner service is running!"
else
    echo "❌ Service failed to start. Checking logs..."
    sudo journalctl -u autoppia-miner -n 30 --no-pager
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        ✅ MINER SETUP COMPLETE! ✅                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Miner Status:"
systemctl status autoppia-miner --no-pager | head -15
echo ""
echo "📝 Useful Commands:"
echo "   View logs: sudo journalctl -u autoppia-miner -f"
echo "   Check status: sudo systemctl status autoppia-miner"
echo "   Restart: sudo systemctl restart autoppia-miner"
echo ""
echo "🔍 Recent Logs:"
sudo journalctl -u autoppia-miner -n 20 --no-pager | tail -15

