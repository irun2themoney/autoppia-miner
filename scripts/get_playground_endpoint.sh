#!/bin/bash
# Get the correct endpoint for IWA Playground

SERVER_IP="134.199.203.133"
SERVER_USER="root"

echo "🔍 Finding Playground Endpoint..."
echo ""

# Try to get HTTPS tunnel URL
TUNNEL_URL=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared.log 2>/dev/null | head -1")

if [ -z "$TUNNEL_URL" ]; then
    echo "⚠️  HTTPS tunnel not found. Starting tunnel..."
    sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'EOF'
        pkill cloudflared || true
        screen -dmS tunnel bash -c 'cloudflared tunnel --url http://localhost:8080 2>&1 | tee /tmp/cloudflared.log'
        sleep 8
EOF
    TUNNEL_URL=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared.log 2>/dev/null | head -1")
fi

if [ -n "$TUNNEL_URL" ]; then
    TUNNEL_HOST=$(echo "$TUNNEL_URL" | sed 's|https://||')
    echo "✅ HTTPS Tunnel Found!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📝 Use this in IWA Playground:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "   $TUNNEL_HOST"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Testing tunnel..."
    if curl -s "$TUNNEL_URL/health" > /dev/null 2>&1; then
        echo "✅ Tunnel is accessible"
    else
        echo "⚠️  Tunnel may still be starting. Wait a few seconds and try again."
    fi
else
    echo "❌ Could not get tunnel URL"
    echo ""
    echo "Try manually:"
    echo "  ssh root@$SERVER_IP 'screen -r tunnel'"
    echo ""
    echo "Or use direct IP (may not work due to HTTPS mixed content):"
    echo "  $SERVER_IP:8080"
fi

