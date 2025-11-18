#!/bin/bash
# Deploy to DigitalOcean server

set -e

SERVER_IP="134.199.203.133"
SERVER_USER="root"
PROJECT_DIR="/opt/autoppia-miner"

echo "🚀 Deploying to server: $SERVER_IP"

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo "Installing sshpass..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install hudochenkov/sshpass/sshpass
    else
        sudo apt-get install -y sshpass
    fi
fi

# Deploy files
echo "📦 Uploading files..."
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
    --exclude '.git' --exclude '*.log' \
    -e "sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no" \
    ./ $SERVER_USER@$SERVER_IP:$PROJECT_DIR/

# Run deployment on server
echo "🔧 Running deployment on server..."
sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no \
    $SERVER_USER@$SERVER_IP << 'ENDSSH'
cd /opt/autoppia-miner
chmod +x scripts/*.sh
./scripts/deploy.sh
ENDSSH

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "  - Check status: ssh root@$SERVER_IP 'systemctl status autoppia-api'"
echo "  - View logs: ssh root@$SERVER_IP 'journalctl -u autoppia-api -f'"
echo "  - Test API: curl http://$SERVER_IP:8080/health"

