#!/bin/bash
# Quick status check from your local Mac

SERVER_IP="134.199.203.133"
SERVER_USER="root"

echo "📊 Miner Status Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Use sshpass if available
if command -v sshpass &> /dev/null; then
    sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
echo "Service Status:"
systemctl status autoppia-miner --no-pager | head -10
echo ""
echo "Recent Logs (last 15 lines):"
journalctl -u autoppia-miner -n 15 --no-pager | tail -15
echo ""
echo "Looking for success indicators:"
journalctl -u autoppia-miner -n 50 --no-pager | grep -E "Axon served|Miner registered|UID:|Processing task" || echo "No recent activity"
ENDSSH
else
    ssh "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
echo "Service Status:"
systemctl status autoppia-miner --no-pager | head -10
echo ""
echo "Recent Logs (last 15 lines):"
journalctl -u autoppia-miner -n 15 --no-pager | tail -15
echo ""
echo "Looking for success indicators:"
journalctl -u autoppia-miner -n 50 --no-pager | grep -E "Axon served|Miner registered|UID:|Processing task" || echo "No recent activity"
ENDSSH
fi

