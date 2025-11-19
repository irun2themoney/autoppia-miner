#!/bin/bash
# Final fixed deployment script - removes untracked files blocking merge

set -e

SERVER="root@134.199.203.133"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Deploying Validator Visibility Fixes (Final Fix)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will deploy all validator visibility fixes to production."
echo ""
read -p "Press Enter to continue..."
echo ""

# Do everything in one SSH session
echo "🔧 Deploying to $SERVER..."
ssh "$SERVER" << 'ENDSSH'
set -e

cd /opt/autoppia-miner

echo "📥 Step 1: Cleaning up conflicting files..."
rm -f api/utils/website_error_handler.py scripts/stake_tao.py
echo "   ✅ Conflicting files removed"
echo ""

echo "📥 Step 2: Pulling latest code..."
git pull origin main
echo "   ✅ Code pulled successfully"
echo ""

echo "🔧 Step 3: Configuring wallet..."
if grep -q "WALLET_NAME" .env 2>/dev/null; then
    echo "   ℹ️  Wallet config already exists"
else
    echo "" >> .env
    echo "# Wallet Configuration" >> .env
    echo "WALLET_NAME=default" >> .env
    echo "WALLET_HOTKEY=default" >> .env
    echo "   ✅ Wallet config added"
fi
echo ""

echo "📦 Step 4: Installing systemd services..."
sudo cp scripts/deploy/autoppia-api.service /etc/systemd/system/
sudo cp scripts/deploy/autoppia-miner.service /etc/systemd/system/
sudo systemctl daemon-reload
echo "   ✅ Services installed"
echo ""

echo "🔄 Step 5: Restarting services..."
sudo systemctl restart autoppia-api
sudo systemctl restart autoppia-miner
echo "   ✅ Services restarted"
echo ""

echo "⏳ Waiting 5 seconds for services to start..."
sleep 5
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Checking Registration Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./scripts/utils/check_registration.sh
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Verifying Visibility"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./scripts/utils/verify_visibility.sh

ENDSSH

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Your miner is now configured for validator visibility!"
echo ""
echo "What happens next:"
echo "  ⏱️  0-2 min: Services restart with new configuration"
echo "  ⏱️  2-5 min: Metagraph syncs, validators discover your miner"
echo "  ⏱️  5-10 min: First validator requests should appear"
echo ""
echo "Monitor validator activity:"
echo "  ssh $SERVER 'journalctl -u autoppia-miner -f | grep Processing'"
echo ""
echo "Check dashboard:"
echo "  http://134.199.203.133:8080/dashboard"
echo ""
