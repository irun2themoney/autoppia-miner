#!/bin/bash
# Quick HTTPS Tunnel Setup for IWA Playground
# Run this on your DigitalOcean droplet

set -e

echo "🔒 Setting up HTTPS tunnel for IWA Playground..."
echo ""

# Option 1: Cloudflare Tunnel (Recommended - Free, No Signup)
echo "📦 Installing Cloudflare Tunnel..."

# Download cloudflared
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    ARCH="amd64"
elif [ "$ARCH" = "aarch64" ]; then
    ARCH="arm64"
fi

curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${ARCH} -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

echo "✅ Cloudflared installed"
echo ""

# Create tunnel
echo "🚇 Creating tunnel..."
cloudflared tunnel create autoppia-api || echo "Tunnel already exists"

# Get tunnel ID
TUNNEL_ID=$(cloudflared tunnel list | grep autoppia-api | awk '{print $1}' | head -1)

if [ -z "$TUNNEL_ID" ]; then
    echo "❌ Could not find tunnel ID"
    exit 1
fi

echo "✅ Tunnel ID: $TUNNEL_ID"
echo ""

# Create config directory
mkdir -p ~/.cloudflared

# Create config file
cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_ID
credentials-file: /root/.cloudflared/${TUNNEL_ID}.json

ingress:
  - hostname: autoppia-api-${TUNNEL_ID:0:8}.trycloudflare.com
    service: http://localhost:8080
  - service: http_status:404
EOF

echo "✅ Config created"
echo ""

# Start tunnel in background
echo "🚀 Starting tunnel..."
cloudflared tunnel run autoppia-api &
TUNNEL_PID=$!

sleep 3

# Get the public URL
echo ""
echo "✅ Tunnel started!"
echo ""
echo "📋 Your HTTPS URL:"
echo "   https://autoppia-api-${TUNNEL_ID:0:8}.trycloudflare.com"
echo ""
echo "🎯 Use this URL in the IWA Playground:"
echo "   https://infinitewebarena.autoppia.com/playground"
echo ""
echo "💡 To stop the tunnel: kill $TUNNEL_PID"
echo "💡 To run in background permanently, see SETUP_HTTPS_TUNNEL.md"

