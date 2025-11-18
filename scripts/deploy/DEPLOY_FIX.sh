#!/bin/bash
# Quick deployment script for the axon serving fix
# Run this on your server to deploy the fix

set -e

echo "🔧 Deploying Miner Fix - Axon Serving"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're in the right directory
if [ ! -f "miner/miner.py" ]; then
    echo "❌ Error: miner/miner.py not found"
    echo "   Please run this script from /opt/autoppia-miner"
    exit 1
fi

WORK_DIR="/opt/autoppia-miner"
cd "$WORK_DIR"

echo "1️⃣  Pulling latest code..."
git pull origin main || {
    echo "⚠️  Git pull failed, but continuing..."
}
echo ""

echo "2️⃣  Verifying the fix is present..."
if grep -q "serve_axon" miner/miner.py; then
    echo "   ✅ Fix found in miner.py"
else
    echo "   ❌ Fix not found! Please check the code."
    exit 1
fi
echo ""

echo "3️⃣  Checking services status..."
if systemctl is-active --quiet autoppia-api; then
    echo "   ✅ API service is running"
else
    echo "   ⚠️  API service is not running, starting it..."
    systemctl start autoppia-api
fi

if systemctl is-active --quiet autoppia-miner; then
    echo "   ✅ Miner service is running"
    echo "   🔄 Restarting miner to apply fix..."
    systemctl restart autoppia-miner
else
    echo "   ⚠️  Miner service is not running, starting it..."
    systemctl start autoppia-miner
fi
echo ""

echo "4️⃣  Waiting for services to start..."
sleep 5
echo ""

echo "5️⃣  Checking service status..."
if systemctl is-active --quiet autoppia-miner; then
    echo "   ✅ Miner service is running"
else
    echo "   ❌ Miner service failed to start!"
    echo "   Check logs: journalctl -u autoppia-miner -n 50"
    exit 1
fi
echo ""

echo "6️⃣  Checking recent miner logs for success indicators..."
echo "   Looking for 'Axon served to subtensor network'..."
sleep 3
if journalctl -u autoppia-miner -n 20 --no-pager | grep -q "Axon served to subtensor network"; then
    echo "   ✅ SUCCESS! Axon is being served to the network!"
elif journalctl -u autoppia-miner -n 20 --no-pager | grep -q "Failed to serve axon"; then
    echo "   ❌ ERROR: Failed to serve axon"
    echo "   Check logs: journalctl -u autoppia-miner -n 50"
    exit 1
else
    echo "   ⚠️  Could not find confirmation in logs"
    echo "   Check logs manually: journalctl -u autoppia-miner -f"
fi
echo ""

echo "7️⃣  Verifying port 8091 is open..."
if ss -tlnp | grep -q ":8091"; then
    echo "   ✅ Port 8091 is listening"
else
    echo "   ⚠️  Port 8091 is not listening"
    echo "   Check firewall: ufw allow 8091/tcp"
fi
echo ""

echo "8️⃣  Verifying API is accessible..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo "   ✅ API is responding"
else
    echo "   ⚠️  API is not responding"
    echo "   Check API logs: journalctl -u autoppia-api -n 50"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Deployment Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Fix deployed!"
echo ""
echo "📋 Next Steps:"
echo "   1. Monitor logs: journalctl -u autoppia-miner -f"
echo "   2. Look for: 'Axon served to subtensor network'"
echo "   3. Watch for validator requests"
echo ""
echo "🔍 To check for validator activity:"
echo "   bash CHECK_VALIDATOR_ACTIVITY.sh"
echo ""
echo "📝 Recent miner logs:"
journalctl -u autoppia-miner -n 10 --no-pager | tail -5
echo ""

