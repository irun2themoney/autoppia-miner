#!/bin/bash
# Monitor miner logs from your local Mac
# This script SSHs into your server and shows the logs

SERVER_IP="134.199.203.133"
SERVER_USER="root"

echo "🔍 Monitoring Miner Logs (Press Ctrl+C to stop)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Use sshpass if available, otherwise prompt for password
if command -v sshpass &> /dev/null; then
    sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "journalctl -u autoppia-miner -f"
else
    ssh "$SERVER_USER@$SERVER_IP" "journalctl -u autoppia-miner -f"
fi

