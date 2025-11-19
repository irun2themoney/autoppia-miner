#!/bin/bash
# Quick deployment script - Run this to deploy validator visibility fixes
# This script will guide you through the deployment process

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Deploying Validator Visibility Fixes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will deploy to: root@134.199.203.133"
echo "You'll be prompted for your SSH password multiple times."
echo ""
read -p "Press Enter to continue..."
echo ""

# Step 1: Pull latest code
echo "📥 Step 1: Pulling latest code from GitHub..."
ssh root@134.199.203.133 << 'EOF'
cd /opt/autoppia-miner
git pull origin main
echo "✅ Code pulled"
EOF
echo ""

# Step 2: Add wallet configuration to .env
echo "🔧 Step 2: Adding wallet configuration to .env..."
ssh root@134.199.203.133 << 'EOF'
cd /opt/autoppia-miner
# Check if wallet config already exists
if grep -q "WALLET_NAME" .env 2>/dev/null; then
    echo "   ⚠️  Wallet config already exists in .env"
else
    echo "" >> .env
    echo "# Wallet Configuration" >> .env
    echo "WALLET_NAME=default" >> .env
    echo "WALLET_HOTKEY=default" >> .env
    echo "   ✅ Wallet config added to .env"
fi
EOF
echo ""

# Step 3: Install systemd services
echo "📦 Step 3: Installing systemd services..."
ssh root@134.199.203.133 << 'EOF'
cd /opt/autoppia-miner
sudo cp scripts/deploy/autoppia-api.service /etc/systemd/system/
sudo cp scripts/deploy/autoppia-miner.service /etc/systemd/system/
sudo systemctl daemon-reload
echo "   ✅ Systemd services installed"
EOF
echo ""

# Step 4: Restart services
echo "🔄 Step 4: Restarting services..."
ssh root@134.199.203.133 << 'EOF'
sudo systemctl restart autoppia-api
echo "   ✅ API service restarted"
sudo systemctl restart autoppia-miner
echo "   ✅ Miner service restarted"
EOF
echo ""

# Step 5: Wait for services to start
echo "⏳ Step 5: Waiting for services to start..."
sleep 5
echo ""

# Step 6: Check registration
echo "📋 Step 6: Checking registration status..."
ssh root@134.199.203.133 << 'EOF'
cd /opt/autoppia-miner
./scripts/utils/check_registration.sh
EOF
echo ""

# Step 7: Verify visibility
echo "🔍 Step 7: Verifying validator visibility..."
ssh root@134.199.203.133 << 'EOF'
cd /opt/autoppia-miner
./scripts/utils/verify_visibility.sh
EOF
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  - Monitor logs: ssh root@134.199.203.133 'journalctl -u autoppia-miner -f'"
echo "  - Check dashboard: http://134.199.203.133:8080/dashboard"
echo "  - Wait 5-10 minutes for validators to discover you"
echo ""
