#!/bin/bash
# Check if validators are testing the miner

echo "🔍 Checking Miner Status and Validator Activity"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check miner service status
echo "1️⃣  Miner Service Status:"
if systemctl is-active --quiet autoppia-miner; then
    echo "   ✅ Miner is running"
    systemctl status autoppia-miner --no-pager | head -10
else
    echo "   ❌ Miner is NOT running"
    echo "   Start with: systemctl start autoppia-miner"
fi
echo ""

# Check recent miner logs for validator activity
echo "2️⃣  Recent Miner Logs (last 50 lines):"
echo "   Looking for validator requests, synapses, forward calls..."
echo ""
journalctl -u autoppia-miner -n 50 --no-pager | grep -E "validator|synapse|forward|process_task|UID|Axon|request" -i || echo "   No validator activity found in recent logs"
echo ""

# Check API logs for solve_task calls
echo "3️⃣  API Activity (solve_task calls):"
echo "   Checking if API is receiving requests..."
echo ""
journalctl -u autoppia-api -n 50 --no-pager | grep -E "solve_task|POST|request" -i | tail -10 || echo "   No API requests found"
echo ""

# Check miner registration
echo "4️⃣  Miner Registration Status:"
echo "   Checking if miner is registered on Subnet 36..."
cd /opt/autoppia-miner
python3 -m bittensor wallet overview --netuid 36 --wallet.name default --wallet.hotkey default 2>/dev/null | grep -E "UID|registered|balance" || echo "   Could not check registration (run manually)"
echo ""

# Check axon port
echo "5️⃣  Axon Port Status:"
echo "   Checking if miner is listening on axon port..."
ss -tlnp | grep 8091 || echo "   Port 8091 not listening"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary:"
echo ""
echo "To see full miner logs:"
echo "   journalctl -u autoppia-miner -f"
echo ""
echo "To see API logs:"
echo "   journalctl -u autoppia-api -f"
echo ""
echo "To check miner registration:"
echo "   python3 -m bittensor wallet overview --netuid 36 --wallet.name default --wallet.hotkey default"
echo ""
echo "Signs of validator activity:"
echo "   ✅ 'forward' calls in miner logs"
echo "   ✅ 'synapse' processing in logs"
echo "   ✅ solve_task requests in API logs"
echo "   ✅ Network activity on port 8091"
echo ""

