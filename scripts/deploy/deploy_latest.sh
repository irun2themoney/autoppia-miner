#!/bin/bash
# Quick deploy script - Pull latest code and restart services
# Run this from your local machine to deploy to the server

set -e

SERVER_IP="134.199.203.133"
SERVER_USER="root"
WORK_DIR="/opt/autoppia-miner"

echo "🚀 Deploying Latest Changes to Production"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will:"
echo "  1. Pull latest code from GitHub"
echo "  2. Install/update dependencies"
echo "  3. Restart API and Miner services"
echo "  4. Verify deployment"
echo ""
echo "You'll be prompted for your SSH password."
echo ""

# Run all commands in one SSH session
ssh "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
cd /opt/autoppia-miner

echo "📥 Step 1: Pulling latest code from GitHub..."
git pull origin main
echo "   ✅ Code pulled"
echo ""

echo "🔧 Step 2: Installing/updating dependencies..."
if [ -d venv ]; then
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo "   ✅ Dependencies updated"
else
    echo "   ⚠️  Virtual environment not found, creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo "   ✅ Virtual environment created and dependencies installed"
fi
echo ""

echo "🔄 Step 3: Restarting services..."
systemctl restart autoppia-api
echo "   ✅ API service restarted"
systemctl restart autoppia-miner
echo "   ✅ Miner service restarted"
echo ""

echo "⏳ Step 4: Waiting for services to start..."
sleep 5
echo ""

echo "✅ Step 5: Verifying deployment..."
echo ""
echo "   API Status:"
systemctl status autoppia-api --no-pager | head -5 || echo "   ⚠️  API service check failed"
echo ""
echo "   Miner Status:"
systemctl status autoppia-miner --no-pager | head -5 || echo "   ⚠️  Miner service check failed"
echo ""

echo "   Testing API health endpoint..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo "   ✅ API is responding!"
    curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8080/health
else
    echo "   ⚠️  API is not responding yet (may need a moment)"
fi
echo ""

echo "📋 Recent miner logs (last 20 lines):"
journalctl -u autoppia-miner -n 20 --no-pager | tail -10 || echo "   ⚠️  Could not fetch logs"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Deployment Complete!"
echo ""
echo "Next steps:"
echo "  - Monitor logs: journalctl -u autoppia-api -f"
echo "  - Check dashboard: http://134.199.203.133:8080/dashboard"
echo "  - Run tests: ./scripts/run_ultimate_test.sh"
echo ""
ENDSSH

echo ""
echo "🎉 Deployment finished!"
echo ""
echo "Your miner now has:"
echo "  ✅ Multi-Agent Ensemble Voting"
echo "  ✅ Advanced Semantic Caching"
echo "  ✅ Validator Behavior Learning"
echo "  ✅ Chutes removed (cleanup)"
echo ""

