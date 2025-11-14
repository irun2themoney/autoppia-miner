#!/bin/bash
# Start Cloudflare Tunnel in background for IWA Playground

echo "🚇 Starting Cloudflare Tunnel..."

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared not found. Installing..."
    curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
    chmod +x /usr/local/bin/cloudflared
fi

# Start tunnel in background
nohup cloudflared tunnel --url http://localhost:8080 > /tmp/cloudflared.log 2>&1 &

sleep 3

# Get the URL from logs
TUNNEL_URL=$(grep "trycloudflare.com" /tmp/cloudflared.log | grep -oP 'https://[^\s]+' | head -1)

if [ -z "$TUNNEL_URL" ]; then
    echo "⚠️  Could not find URL in logs. Check /tmp/cloudflared.log"
    echo "   Or run: cloudflared tunnel --url http://localhost:8080"
else
    echo ""
    echo "✅ Tunnel started!"
    echo ""
    echo "📋 Your HTTPS URL:"
    echo "   $TUNNEL_URL"
    echo ""
    echo "🎯 Use this URL in the IWA Playground:"
    echo "   https://infinitewebarena.autoppia.com/playground"
    echo ""
    echo "💡 To stop: pkill cloudflared"
    echo "💡 To view logs: tail -f /tmp/cloudflared.log"
fi

