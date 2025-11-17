#!/bin/bash
# Fix playground access issues

SERVER_IP="134.199.203.133"
SERVER_USER="root"

echo "🔧 Fixing Playground Access Issues"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "1️⃣  Checking HTTPS tunnel status..."
TUNNEL_RUNNING=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "ps aux | grep -c '[c]loudflared tunnel'")
if [ "$TUNNEL_RUNNING" -eq "0" ]; then
    echo "   ⚠️  Tunnel not running, starting it..."
    sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'EOF'
        pkill cloudflared || true
        screen -dmS tunnel bash -c 'cloudflared tunnel --url http://localhost:8080 2>&1 | tee /tmp/cloudflared.log'
        sleep 5
EOF
    echo "   ✅ Tunnel started"
else
    echo "   ✅ Tunnel is running"
fi

echo ""
echo "2️⃣  Getting tunnel URL..."
TUNNEL_URL=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared.log 2>/dev/null | tail -1")
if [ -z "$TUNNEL_URL" ]; then
    echo "   ⚠️  Could not find tunnel URL in log, checking screen session..."
    sleep 3
    TUNNEL_URL=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared.log 2>/dev/null | tail -1")
fi

if [ -n "$TUNNEL_URL" ]; then
    # Remove https:// prefix for playground
    TUNNEL_HOST=$(echo "$TUNNEL_URL" | sed 's|https://||')
    echo "   ✅ Tunnel URL: $TUNNEL_URL"
    echo "   📝 Use this in playground: $TUNNEL_HOST"
else
    echo "   ❌ Could not get tunnel URL"
    echo "   Try: ssh root@$SERVER_IP 'screen -r tunnel'"
fi

echo ""
echo "3️⃣  Testing tunnel accessibility..."
if [ -n "$TUNNEL_URL" ]; then
    HEALTH_CHECK=$(curl -s -w "%{http_code}" "$TUNNEL_URL/health" -o /dev/null)
    if [ "$HEALTH_CHECK" = "200" ]; then
        echo "   ✅ Tunnel is accessible"
    else
        echo "   ⚠️  Tunnel returned HTTP $HEALTH_CHECK"
    fi
fi

echo ""
echo "4️⃣  Testing CORS headers..."
if [ -n "$TUNNEL_URL" ]; then
    CORS_CHECK=$(curl -s -X OPTIONS "$TUNNEL_URL/solve_task" \
        -H "Origin: https://infinitewebarena.autoppia.com" \
        -H "Access-Control-Request-Method: POST" -I | grep -i "access-control-allow-origin")
    if [ -n "$CORS_CHECK" ]; then
        echo "   ✅ CORS headers present"
    else
        echo "   ⚠️  CORS headers not found"
    fi
fi

echo ""
echo "5️⃣  Checking firewall..."
FIREWALL_STATUS=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "ufw status | grep -c '8080/tcp' || echo '0'")
if [ "$FIREWALL_STATUS" -eq "0" ]; then
    echo "   ⚠️  Port 8080 may not be open in firewall"
    echo "   Run: ssh root@$SERVER_IP 'ufw allow 8080/tcp && ufw reload'"
else
    echo "   ✅ Port 8080 is open"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Diagnostic Complete"
echo ""
if [ -n "$TUNNEL_HOST" ]; then
    echo "📝 Use this endpoint in IWA Playground:"
    echo "   $TUNNEL_HOST"
    echo ""
    echo "Or try direct IP (may not work due to mixed content):"
    echo "   $SERVER_IP:8080"
else
    echo "⚠️  Could not determine tunnel URL"
    echo "   Check manually: ssh root@$SERVER_IP 'screen -r tunnel'"
fi
echo ""

