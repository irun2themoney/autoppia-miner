#!/bin/bash
# Script to investigate StartRoundSynapse errors in miner logs

echo "🔍 Investigating StartRoundSynapse Errors"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SERVER_IP="134.199.203.133"
SERVER_USER="root"

# Check if sshpass is available
if command -v sshpass &> /dev/null; then
    SSH_CMD="sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no"
else
    SSH_CMD="ssh"
fi

echo "1️⃣  Checking for StartRoundSynapse errors in logs..."
echo ""
$SSH_CMD "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
echo "Recent StartRoundSynapse errors (last 50 lines):"
journalctl -u autoppia-miner -n 200 --no-pager | grep -i "StartRoundSynapse\|UnknownSynapse" | tail -10
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "2️⃣  Checking synapse handling in code..."
echo ""
cd /opt/autoppia-miner
if grep -q "StartRoundSynapse\|TaskSynapse" miner/protocol.py 2>/dev/null; then
    echo "✅ Synapse types found in protocol.py"
    grep -n "class.*Synapse" miner/protocol.py
else
    echo "❌ No custom synapse types found"
fi
echo ""
if grep -q "process_start_round\|StartRoundSynapse" miner/miner.py 2>/dev/null; then
    echo "✅ StartRoundSynapse handler found in miner.py"
else
    echo "❌ No StartRoundSynapse handler found"
fi
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "3️⃣  Checking if miner is handling synapses correctly..."
echo ""
echo "Current synapse processing function:"
grep -A 5 "async def process_task" miner/miner.py | head -10
ENDSSH

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Analysis:"
echo ""
echo "If you see StartRoundSynapse errors:"
echo "  - Validators are trying to send StartRoundSynapse"
echo "  - Our miner needs to handle this synapse type"
echo "  - We've added protocol.py with synapse definitions"
echo "  - Need to update miner to use these types"
echo ""
echo "Next steps:"
echo "  1. Deploy updated miner with synapse type support"
echo "  2. Monitor logs to see if errors stop"
echo "  3. Verify validators can communicate properly"
echo ""

