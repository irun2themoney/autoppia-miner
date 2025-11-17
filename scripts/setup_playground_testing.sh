#!/bin/bash
# Setup script for IWA Playground testing on the server
# This sets up cloudflared tunnel and runs official tests

set -e

SERVER_IP="134.199.203.133"
SERVER_USER="root"

echo "🚀 Setting Up IWA Playground Testing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "1️⃣  Installing cloudflared on server..."
sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'EOF'
    if ! command -v cloudflared &> /dev/null; then
        echo "   Installing cloudflared..."
        curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
        chmod +x /usr/local/bin/cloudflared
        echo "   ✅ cloudflared installed"
    else
        echo "   ✅ cloudflared already installed"
    fi
EOF

echo ""
echo "2️⃣  Running official tests on server..."
sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'EOF'
    cd /opt/autoppia-miner
    git pull origin main
    echo ""
    echo "   Running official test suite..."
    python3 tests/test_official.py http://localhost:8080
EOF

echo ""
echo "3️⃣  Setting up HTTPS tunnel..."
echo "   Starting cloudflared tunnel in background..."
echo ""
echo "   ⚠️  IMPORTANT: The tunnel will run in a screen session"
echo "   To view the tunnel URL, run: ssh root@$SERVER_IP 'screen -r tunnel'"
echo ""

sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'EOF'
    # Kill any existing tunnel
    pkill cloudflared || true
    
    # Start tunnel in screen session
    screen -dmS tunnel bash -c 'cloudflared tunnel --url http://localhost:8080 2>&1 | tee /tmp/cloudflared.log'
    
    # Wait a moment for tunnel to start
    sleep 3
    
    # Extract tunnel URL from log
    if [ -f /tmp/cloudflared.log ]; then
        TUNNEL_URL=$(grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared.log | head -1)
        if [ -n "$TUNNEL_URL" ]; then
            echo "   ✅ Tunnel URL: $TUNNEL_URL"
            echo "$TUNNEL_URL" > /tmp/tunnel_url.txt
        else
            echo "   ⚠️  Tunnel starting... Check with: screen -r tunnel"
        fi
    fi
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo ""
echo "Next Steps:"
echo ""
echo "1. Get your HTTPS tunnel URL:"
echo "   ssh root@$SERVER_IP 'cat /tmp/tunnel_url.txt 2>/dev/null || screen -r tunnel'"
echo ""
echo "2. Test on IWA Playground:"
echo "   - Go to: https://infinitewebarena.autoppia.com/playground"
echo "   - Enter endpoint: $SERVER_IP:8080 (or use HTTPS tunnel URL)"
echo "   - Select projects and use cases"
echo "   - Click 'Run Benchmark'"
echo ""
echo "3. Monitor logs:"
echo "   ssh root@$SERVER_IP 'journalctl -u autoppia-api -f'"
echo ""

