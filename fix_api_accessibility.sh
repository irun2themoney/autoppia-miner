#!/bin/bash
# 🔧 Fix API Accessibility for InfiniteWeb Arena
# Run this on your DigitalOcean VPS

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🔧 FIXING API ACCESSIBILITY FOR INFINITEWEB ARENA 🔧     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

echo "1️⃣  Checking if API service is running..."
if systemctl is-active --quiet autoppia-api; then
    echo "✅ API service is running"
else
    echo "❌ API service is NOT running. Starting it..."
    systemctl start autoppia-api
    sleep 3
    if systemctl is-active --quiet autoppia-api; then
        echo "✅ API service started successfully"
    else
        echo "❌ Failed to start API service. Checking logs..."
        journalctl -u autoppia-api -n 20
        exit 1
    fi
fi

echo ""
echo "2️⃣  Testing API locally..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ API is responding locally"
    curl -s http://localhost:8080/health | head -3
else
    echo "❌ API is not responding locally. Check logs:"
    journalctl -u autoppia-api -n 30
    exit 1
fi

echo ""
echo "3️⃣  Checking UFW firewall..."
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        echo "✅ UFW is active"
        if ufw status | grep -q "8080"; then
            echo "✅ Port 8080 is open in UFW"
        else
            echo "⚠️  Port 8080 not found in UFW rules. Adding it..."
            ufw allow 8080/tcp
            echo "✅ Port 8080 added to UFW"
        fi
    else
        echo "⚠️  UFW is not active. Enabling and opening port 8080..."
        ufw --force enable
        ufw allow 22/tcp
        ufw allow 8080/tcp
        echo "✅ UFW enabled and port 8080 opened"
    fi
else
    echo "⚠️  UFW not installed. Installing..."
    apt update && apt install -y ufw
    ufw --force enable
    ufw allow 22/tcp
    ufw allow 8080/tcp
    echo "✅ UFW installed and configured"
fi

echo ""
echo "4️⃣  Checking if port 8080 is listening..."
if netstat -tuln | grep -q ":8080"; then
    echo "✅ Port 8080 is listening"
    netstat -tuln | grep ":8080"
else
    echo "❌ Port 8080 is NOT listening. API may not be running correctly."
    echo "Checking API logs..."
    journalctl -u autoppia-api -n 30
    exit 1
fi

echo ""
echo "5️⃣  Checking DigitalOcean Firewall (manual check needed)..."
echo "⚠️  IMPORTANT: You need to check DigitalOcean Firewall manually:"
echo "   1. Go to: https://cloud.digitalocean.com/networking/firewalls"
echo "   2. Find your droplet's firewall"
echo "   3. Ensure port 8080 is open for inbound traffic"
echo "   4. If no firewall exists, create one with:"
echo "      - Inbound: Custom TCP 8080 (Allow from All IPv4)"
echo "      - Outbound: All traffic"
echo "      - Apply to your droplet"

echo ""
echo "6️⃣  Testing external accessibility..."
DROPLET_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || hostname -I | awk '{print $1}')
echo "   Your droplet IP: $DROPLET_IP"
echo "   Testing: http://$DROPLET_IP:8080/health"

if curl -s --max-time 5 "http://$DROPLET_IP:8080/health" > /dev/null 2>&1; then
    echo "✅ API is accessible externally!"
    curl -s "http://$DROPLET_IP:8080/health" | head -3
else
    echo "⚠️  API is not accessible externally. This is likely a DigitalOcean Firewall issue."
    echo "   Please check the DigitalOcean Firewall settings as mentioned above."
fi

echo ""
echo "7️⃣  Verifying CORS configuration..."
if [ -f /opt/autoppia-miner/.env ]; then
    if grep -q "CORS_ORIGINS" /opt/autoppia-miner/.env; then
        echo "✅ CORS_ORIGINS is configured"
        grep "CORS_ORIGINS" /opt/autoppia-miner/.env
    else
        echo "⚠️  CORS_ORIGINS not set. Adding default (allows all origins)..."
        echo "CORS_ORIGINS=*" >> /opt/autoppia-miner/.env
        echo "✅ CORS_ORIGINS added. Restarting API..."
        systemctl restart autoppia-api
        sleep 2
    fi
else
    echo "⚠️  .env file not found at /opt/autoppia-miner/.env"
    echo "   Checking current directory..."
    if [ -f .env ]; then
        if ! grep -q "CORS_ORIGINS" .env; then
            echo "CORS_ORIGINS=*" >> .env
            systemctl restart autoppia-api
        fi
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    SUMMARY                                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Local checks complete"
echo ""
echo "🔍 Next Steps:"
echo "   1. Check DigitalOcean Firewall (see step 5 above)"
echo "   2. Test from InfiniteWeb Arena again"
echo "   3. If still failing, check API logs:"
echo "      journalctl -u autoppia-api -f"
echo ""
echo "📋 Your endpoint should be:"
echo "   $DROPLET_IP:8080"
echo "   or"
echo "   http://$DROPLET_IP:8080"
echo ""

