#!/bin/bash
# Script to change axon port on production server
# Usage: ./scripts/change_axon_port.sh [new_port]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Server details
SERVER_IP="134.199.203.133"
SERVER_USER="root"
SERVER_PASS="DigitalOcean4life"

# Current port (from service file)
CURRENT_PORT="8091"

echo "=== 🔄 AXON PORT CHANGE SCRIPT ==="
echo ""

# Get new port from argument or prompt
if [ -z "$1" ]; then
    echo "Current port: $CURRENT_PORT"
    echo ""
    read -p "Enter new port (recommended: 8092): " NEW_PORT
else
    NEW_PORT="$1"
fi

# Validate port
if ! [[ "$NEW_PORT" =~ ^[0-9]+$ ]] || [ "$NEW_PORT" -lt 1024 ] || [ "$NEW_PORT" -gt 65535 ]; then
    echo -e "${RED}❌ Invalid port: $NEW_PORT${NC}"
    echo "Port must be between 1024 and 65535"
    exit 1
fi

if [ "$NEW_PORT" == "$CURRENT_PORT" ]; then
    echo -e "${YELLOW}⚠️  Port $NEW_PORT is already the current port${NC}"
    exit 0
fi

echo ""
echo "📋 Port Change Plan:"
echo "   Current: $CURRENT_PORT"
echo "   New:     $NEW_PORT"
echo ""
read -p "Continue? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🚀 Starting port change..."

# Step 1: Backup current service file
echo ""
echo "Step 1: Backing up current service file..."
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" \
    "cp /etc/systemd/system/autoppia-miner.service /etc/systemd/system/autoppia-miner.service.backup.$(date +%Y%m%d_%H%M%S)" \
    && echo -e "${GREEN}✅ Backup created${NC}" || echo -e "${RED}❌ Backup failed${NC}"

# Step 2: Update service file
echo ""
echo "Step 2: Updating systemd service file..."
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" \
    "sed -i 's/--axon.port $CURRENT_PORT/--axon.port $NEW_PORT/g' /etc/systemd/system/autoppia-miner.service" \
    && echo -e "${GREEN}✅ Service file updated${NC}" || echo -e "${RED}❌ Service file update failed${NC}"

# Step 3: Update firewall
echo ""
echo "Step 3: Updating firewall rules..."
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" \
    "ufw allow $NEW_PORT/tcp && echo 'Firewall rule added'" \
    && echo -e "${GREEN}✅ Firewall updated (port $NEW_PORT allowed)${NC}" || echo -e "${YELLOW}⚠️  Firewall update may have failed (check manually)${NC}"

# Step 4: Reload systemd
echo ""
echo "Step 4: Reloading systemd daemon..."
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" \
    "systemctl daemon-reload" \
    && echo -e "${GREEN}✅ Systemd reloaded${NC}" || echo -e "${RED}❌ Systemd reload failed${NC}"

# Step 5: Restart miner
echo ""
echo "Step 5: Restarting miner service..."
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" \
    "systemctl restart autoppia-miner && sleep 3 && systemctl is-active autoppia-miner" \
    && echo -e "${GREEN}✅ Miner restarted and active${NC}" || echo -e "${RED}❌ Miner restart failed${NC}"

# Step 6: Verify new port
echo ""
echo "Step 6: Verifying new port is listening..."
sleep 2
PORT_CHECK=$(sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" \
    "netstat -tlnp 2>/dev/null | grep -E ':$NEW_PORT ' || ss -tlnp 2>/dev/null | grep -E ':$NEW_PORT ' || echo 'NOT_FOUND'")

if echo "$PORT_CHECK" | grep -q "$NEW_PORT"; then
    echo -e "${GREEN}✅ Port $NEW_PORT is listening${NC}"
    echo "$PORT_CHECK"
else
    echo -e "${RED}❌ Port $NEW_PORT not found listening${NC}"
    echo "Checking logs..."
    sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" \
        "journalctl -u autoppia-miner --since '1 minute ago' --no-pager | tail -20"
fi

# Step 7: Check logs for axon serving
echo ""
echo "Step 7: Checking miner logs for axon serving..."
AXON_LOG=$(sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" \
    "journalctl -u autoppia-miner --since '1 minute ago' --no-pager | grep -iE 'axon|port|served' | tail -5")

if [ -n "$AXON_LOG" ]; then
    echo -e "${GREEN}✅ Axon logs found:${NC}"
    echo "$AXON_LOG"
else
    echo -e "${YELLOW}⚠️  No recent axon logs found${NC}"
fi

# Summary
echo ""
echo "=== ✅ PORT CHANGE COMPLETE ==="
echo ""
echo "📊 Summary:"
echo "   Old Port: $CURRENT_PORT"
echo "   New Port: $NEW_PORT"
echo "   Server:   $SERVER_IP"
echo ""
echo "🔍 Next Steps:"
echo "   1. Monitor logs: ssh $SERVER_USER@$SERVER_IP 'journalctl -u autoppia-miner -f'"
echo "   2. Check on-chain status: python3 scripts/check_onchain_status.py"
echo "   3. Wait 5-15 minutes for network to update"
echo "   4. Monitor for validator queries"
echo ""
echo "🔄 Rollback (if needed):"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo "   cp /etc/systemd/system/autoppia-miner.service.backup.* /etc/systemd/system/autoppia-miner.service"
echo "   systemctl daemon-reload"
echo "   systemctl restart autoppia-miner"
echo ""

