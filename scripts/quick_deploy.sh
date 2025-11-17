#!/bin/bash
# Quick deploy script - prompts for password once then runs all commands

SERVER_IP="134.199.203.133"
SERVER_USER="root"
WORK_DIR="/opt/autoppia-miner"

echo "🚀 Quick Deploy to Server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will:"
echo "  1. Pull latest code"
echo "  2. Restart miner"
echo "  3. Show logs"
echo ""
echo "You'll be prompted for your SSH password once."
echo ""

# Run all commands in one SSH session
ssh "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
cd /opt/autoppia-miner
echo "📥 Pulling latest code..."
git pull origin main
echo ""
echo "🔄 Restarting miner..."
systemctl restart autoppia-miner
echo ""
echo "⏳ Waiting 5 seconds..."
sleep 5
echo ""
echo "📋 Recent logs:"
journalctl -u autoppia-miner -n 50 --no-pager | grep -E "Axon served|Failed to serve|Miner registered|UID:|ERROR|error" || journalctl -u autoppia-miner -n 20 --no-pager
echo ""
echo "✅ Done! Check above for 'Axon served to subtensor network'"
ENDSSH

