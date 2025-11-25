#!/bin/bash
# Manual version - prompts for SSH password
# Usage: ./scripts/change_axon_port_manual.sh [new_port]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SERVER_IP="134.199.203.133"
SERVER_USER="root"
CURRENT_PORT="8091"

echo "=== 🔄 AXON PORT CHANGE (Manual SSH) ==="
echo ""

if [ -z "$1" ]; then
    echo "Current port: $CURRENT_PORT"
    read -p "Enter new port (recommended: 8092): " NEW_PORT
else
    NEW_PORT="$1"
fi

if ! [[ "$NEW_PORT" =~ ^[0-9]+$ ]] || [ "$NEW_PORT" -lt 1024 ] || [ "$NEW_PORT" -gt 65535 ]; then
    echo -e "${RED}❌ Invalid port${NC}"
    exit 1
fi

if [ "$NEW_PORT" == "$CURRENT_PORT" ]; then
    echo -e "${YELLOW}⚠️  Already using port $NEW_PORT${NC}"
    exit 0
fi

echo ""
echo "📋 Changing port: $CURRENT_PORT → $NEW_PORT"
echo ""
echo "You will be prompted for SSH password"
echo ""

# Commands to run on server
COMMANDS="
set -e
echo 'Step 1: Backing up service file...'
cp /etc/systemd/system/autoppia-miner.service /etc/systemd/system/autoppia-miner.service.backup.\$(date +%Y%m%d_%H%M%S)

echo 'Step 2: Updating service file...'
sed -i 's/--axon.port $CURRENT_PORT/--axon.port $NEW_PORT/g' /etc/systemd/system/autoppia-miner.service

echo 'Step 3: Updating firewall...'
ufw allow $NEW_PORT/tcp

echo 'Step 4: Reloading systemd...'
systemctl daemon-reload

echo 'Step 5: Restarting miner...'
systemctl restart autoppia-miner
sleep 3

echo 'Step 6: Checking status...'
systemctl is-active autoppia-miner && echo '✅ Miner is active' || echo '❌ Miner failed to start'

echo 'Step 7: Verifying port...'
netstat -tlnp 2>/dev/null | grep -E ':$NEW_PORT ' || ss -tlnp 2>/dev/null | grep -E ':$NEW_PORT ' || echo '⚠️  Port not found'

echo 'Step 8: Recent logs...'
journalctl -u autoppia-miner --since '1 minute ago' --no-pager | grep -iE 'axon|port|served' | tail -5
"

# Execute on server
ssh "$SERVER_USER@$SERVER_IP" "$COMMANDS"

echo ""
echo -e "${GREEN}=== ✅ PORT CHANGE COMPLETE ===${NC}"
echo ""
echo "New port: $NEW_PORT"
echo "Monitor: ssh $SERVER_USER@$SERVER_IP 'journalctl -u autoppia-miner -f'"
echo ""

