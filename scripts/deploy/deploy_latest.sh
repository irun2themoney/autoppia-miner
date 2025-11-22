#!/bin/bash

# 🚀 Autoppia Miner - Deploy Latest Fixes
# Deploys all critical fixes to production server

set -e

echo "🚀 Starting Autoppia Miner Deployment..."

# Server details
SERVER="134.199.203.133"
REMOTE_PATH="/opt/autoppia-miner"

echo "📡 Deploying to server: $SERVER"

# Push latest code to server
echo "🔄 Pushing latest code..."
git add .
git commit -m "Deploy latest fixes: improved selectors, round processing, browser automation" || echo "No changes to commit"
git push

# Deploy to server
echo "📦 Deploying to production server..."
ssh -o StrictHostKeyChecking=no root@$SERVER << EOF
    echo "🔄 Updating code on server..."
    cd $REMOTE_PATH
    git pull
    git reset --hard origin/main

    echo "📦 Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt

    echo "🔧 Installing Playwright browsers..."
    playwright install chromium

    echo "🔄 Restarting services..."
    systemctl restart autoppia-api
    systemctl restart autoppia-miner

    echo "⏳ Waiting for services to start..."
    sleep 10

    echo "✅ Checking service status..."
    systemctl status autoppia-api --no-pager -l
    systemctl status autoppia-miner --no-pager -l
EOF

echo "🔍 Testing deployment..."

# Test API endpoint
echo "🧪 Testing API endpoint..."
API_RESPONSE=$(curl -s -k -X POST https://$SERVER:8443/solve_task \
    -H "Content-Type: application/json" \
    -d '{"id":"deploy-test","prompt":"click button","url":"https://example.com"}')

if [[ $API_RESPONSE == *"actions"* ]]; then
    echo "✅ API endpoint working"
else
    echo "❌ API endpoint failed"
    exit 1
fi

# Check for improved selectors
if [[ $API_RESPONSE == *"cssSelector"* ]]; then
    echo "✅ Improved selectors deployed"
else
    echo "⚠️  Old selectors still in use"
fi

echo "📊 Deployment Summary:"
echo "  - API URL: https://$SERVER:8443/solve_task"
echo "  - Miner UID: 160 (Subnet 36)"
echo "  - Status: Deployed and tested"

echo "🎯 Next Steps:"
echo "1. Check IWA platform for round activity"
echo "2. Monitor validator requests"
echo "3. Verify scoring improvements"

echo "✅ Deployment Complete!"
