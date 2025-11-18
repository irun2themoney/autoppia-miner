#!/bin/bash
# Deploy Chutes API integration to server

SERVER="root@134.199.203.133"
PASSWORD="DigitalOcean4life"
MINER_DIR="/opt/autoppia-miner"

echo "🚀 Deploying Chutes API integration..."
echo ""

# Pull latest code
echo "📥 Pulling latest code..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" "cd $MINER_DIR && git pull origin main"

# Update .env with Chutes API key
echo "🔑 Updating .env with Chutes API key..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" "cd $MINER_DIR && cat >> .env << 'EOF'

# Chutes API Configuration
AGENT_TYPE=chutes
CHUTES_API_KEY=cpk_5bcbb7216ed743229e4a4ca4bd875f79.97cdedde58e45965820657bd8ec790fa.lXEjoNHFlkwgNb2wK9xTN0Ex3YmkOF8u
CHUTES_API_URL=https://api.chutes.ai/chat/completions
EOF
"

# Install any new dependencies
echo "📦 Installing dependencies..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" "cd $MINER_DIR && pip3 install -q httpx 2>/dev/null || true"

# Restart API service
echo "🔄 Restarting API service..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" "systemctl restart autoppia-api"

# Wait for service to start
sleep 3

# Check status
echo "✅ Checking API status..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" "systemctl status autoppia-api --no-pager | head -10"

echo ""
echo "📊 Checking API logs..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" "journalctl -u autoppia-api --since '30 seconds ago' --no-pager | tail -20"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "💡 Note: If Chutes API auth fails, the agent will fallback to template mode."
echo "   Check logs for Chutes API errors and adjust authentication if needed."

