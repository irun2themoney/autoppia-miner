#!/bin/bash
# Fix virtual environment and restart API

set -e

echo "🔧 Fixing virtual environment..."

cd /opt/autoppia-miner

# Install python3-venv
apt install -y python3.10-venv

# Remove old venv if it exists
rm -rf venv

# Create new virtual environment
python3 -m venv venv

# Activate and install packages
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Restart API service
systemctl restart autoppia-api

# Wait a moment
sleep 3

# Check status
echo ""
echo "=== API Service Status ==="
systemctl status autoppia-api --no-pager | head -15

# Test API
echo ""
echo "=== Testing API ==="
curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8080/health

echo ""
echo "✅ Done!"

