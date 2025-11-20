#!/bin/bash

# Deployment script for Live Analysis update
# Usage: ./scripts/deploy/deploy_live_analysis.sh

set -e

echo "🚀 Deploying Live Analysis Update..."

# 1. Pull latest changes
echo "📥 Pulling latest code..."
git stash
git pull
git stash pop || true

# 2. Install new dependencies
echo "📦 Installing new dependencies (beautifulsoup4, lxml)..."
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "⚠️ No venv found, installing globally (or to user)..."
    pip install -r requirements.txt
fi

# 3. Restart services
echo "🔄 Restarting services..."
sudo systemctl restart autoppia-api
sudo systemctl restart autoppia-miner

# 4. Verify status
echo "✅ Deployment complete! Checking status..."
sudo systemctl status autoppia-miner --no-pager

echo "
🎉 Live Analysis Deployed!
Monitor logs to see it in action:
journalctl -u autoppia-miner -f | grep 'Live Analysis'
"
