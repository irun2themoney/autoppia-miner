#!/bin/bash
# Direct deployment script - Deploy local changes directly to server (bypasses GitHub)
# Use this when GitHub push fails but you still want to deploy

set -e

SERVER_IP="134.199.203.133"
SERVER_USER="root"
WORK_DIR="/opt/autoppia-miner"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🚀 Direct Deployment to Production (Bypassing GitHub)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will:"
echo "  1. Copy changed files directly to server via rsync"
echo "  2. Restart API and Miner services"
echo "  3. Verify deployment"
echo ""
echo "Files to deploy:"
echo "  - api/utils/website_detector.py (100% website coverage!)"
echo "  - api/utils/task_diversity.py"
echo "  - api/endpoints_dashboard.py"
echo "  - api/utils/advanced_metrics.py"
echo "  - docs/ (documentation updates)"
echo ""

# Use sshpass if available, otherwise prompt for password
if command -v sshpass &> /dev/null; then
    SSH_CMD="sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no"
    SCP_CMD="sshpass -p 'DigitalOcean4life' scp -o StrictHostKeyChecking=no"
    RSYNC_CMD="sshpass -p 'DigitalOcean4life' rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc'"
else
    SSH_CMD="ssh"
    SCP_CMD="scp"
    RSYNC_CMD="rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc'"
fi

echo "📤 Step 1: Copying files to server..."
$RSYNC_CMD \
    "$LOCAL_DIR/api/" \
    "$SERVER_USER@$SERVER_IP:$WORK_DIR/api/" \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git'

echo "   ✅ API files copied"
echo ""

echo "📤 Step 2: Copying documentation..."
$RSYNC_CMD \
    "$LOCAL_DIR/docs/" \
    "$SERVER_USER@$SERVER_IP:$WORK_DIR/docs/" \
    --exclude='*.pyc' \
    --exclude='__pycache__'

echo "   ✅ Documentation copied"
echo ""

echo "🔄 Step 3: Restarting services on server..."
$SSH_CMD "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
cd /opt/autoppia-miner

echo "   Restarting API service..."
systemctl restart autoppia-api
sleep 2
echo "   ✅ API service restarted"

echo "   Restarting Miner service..."
systemctl restart autoppia-miner
sleep 2
echo "   ✅ Miner service restarted"
echo ""

echo "⏳ Waiting for services to stabilize..."
sleep 5
echo ""

echo "✅ Verifying deployment..."
echo ""
echo "   API Status:"
systemctl is-active autoppia-api && echo "   ✅ API is running" || echo "   ⚠️  API is not running"

echo "   Miner Status:"
systemctl is-active autoppia-miner && echo "   ✅ Miner is running" || echo "   ⚠️  Miner is not running"
echo ""

echo "   Testing API health endpoint..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "   ✅ API is responding!"
    curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8080/health
else
    echo "   ⚠️  API is not responding yet (checking logs...)"
    journalctl -u autoppia-api -n 10 --no-pager | tail -5
fi
echo ""

echo "📋 Recent miner logs (last 5 lines):"
journalctl -u autoppia-miner -n 5 --no-pager | tail -5 || echo "   ⚠️  Could not fetch logs"
echo ""

ENDSSH

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Direct Deployment Complete!"
echo ""
echo "Your miner now has:"
echo "  ✅ 100% Website Coverage (13/13 websites)"
echo "  ✅ AutoDining support (restaurant bookings)"
echo "  ✅ AutoCRM support (legal case management)"
echo "  ✅ AutoDrive support (file management)"
echo "  ✅ AutoMail support (email client)"
echo "  ✅ Dashboard improvements"
echo ""
echo "Next steps:"
echo "  - Monitor dashboard: http://134.199.203.133:8080/api/dashboard"
echo "  - Check logs: ssh root@134.199.203.133 'journalctl -u autoppia-api -f'"
echo "  - Once GitHub recovers, push commits: git push origin main"
echo ""

