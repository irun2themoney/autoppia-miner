#!/bin/bash
# Deploy fix to remote server via SSH
# This script runs from your local machine and deploys to your server

set -e

SERVER_IP="134.199.203.133"
SERVER_USER="root"
WORK_DIR="/opt/autoppia-miner"

echo "🚀 Deploying Fix to Server: $SERVER_IP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if SSH is available
if ! command -v ssh &> /dev/null; then
    echo "❌ SSH not found. Please install SSH client."
    exit 1
fi

echo "1️⃣  Testing SSH connection..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes "$SERVER_USER@$SERVER_IP" "echo 'SSH connection successful'" 2>/dev/null; then
    echo "   ✅ SSH connection works"
else
    echo "   ⚠️  SSH connection test failed"
    echo "   You may need to enter your password or set up SSH keys"
    echo "   Continuing anyway..."
fi
echo ""

echo "2️⃣  Pulling latest code on server..."
ssh "$SERVER_USER@$SERVER_IP" "cd $WORK_DIR && git pull origin main"
echo "   ✅ Code pulled"
echo ""

echo "3️⃣  Verifying fix is present..."
if ssh "$SERVER_USER@$SERVER_IP" "cd $WORK_DIR && grep -q 'serve_axon' miner/miner.py"; then
    echo "   ✅ Fix found in miner.py"
else
    echo "   ❌ Fix not found! Something went wrong."
    exit 1
fi
echo ""

echo "4️⃣  Restarting miner service..."
ssh "$SERVER_USER@$SERVER_IP" "systemctl restart autoppia-miner"
echo "   ✅ Miner restarted"
echo ""

echo "5️⃣  Waiting for service to start..."
sleep 5
echo ""

echo "6️⃣  Checking service status..."
ssh "$SERVER_USER@$SERVER_IP" "systemctl status autoppia-miner --no-pager | head -15"
echo ""

echo "7️⃣  Checking logs for success indicators..."
echo "   Looking for 'Axon served to subtensor network'..."
sleep 3
ssh "$SERVER_USER@$SERVER_IP" "journalctl -u autoppia-miner -n 30 --no-pager | grep -E 'Axon served|Failed to serve|Miner registered|UID:' || echo 'No matches found'"
echo ""

echo "8️⃣  Viewing recent logs..."
ssh "$SERVER_USER@$SERVER_IP" "journalctl -u autoppia-miner -n 20 --no-pager"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Fix deployed to server!"
echo ""
echo "🔍 To monitor logs in real-time, run:"
echo "   ssh $SERVER_USER@$SERVER_IP 'journalctl -u autoppia-miner -f'"
echo ""
echo "📋 Look for these success messages:"
echo "   ✅ 'Axon served to subtensor network!'"
echo "   ✅ 'Miner registered! UID: X'"
echo "   ✅ 'Miner is running and ready to receive validator requests!'"
echo ""

