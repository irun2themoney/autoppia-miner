#!/bin/bash
# Get the current HTTPS tunnel URL from the server

SERVER_IP="134.199.203.133"
SERVER_USER="root"

echo "🔍 Getting HTTPS Tunnel URL..."
echo ""

sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'EOF'
    # Try to get URL from log file
    if [ -f /tmp/tunnel_url.txt ]; then
        echo "✅ Tunnel URL:"
        cat /tmp/tunnel_url.txt
        echo ""
    fi
    
    # Check if tunnel is running
    if pgrep -f "cloudflared tunnel" > /dev/null; then
        echo "✅ Tunnel is running"
        echo ""
        echo "To view tunnel output:"
        echo "  screen -r tunnel"
    else
        echo "❌ Tunnel is not running"
        echo ""
        echo "To start tunnel:"
        echo "  screen -dmS tunnel bash -c 'cloudflared tunnel --url http://localhost:8080'"
    fi
EOF

