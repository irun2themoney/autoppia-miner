#!/bin/bash
# Run official tests on the remote server

SERVER_IP="134.199.203.133"
SERVER_USER="root"

echo "🧪 Running Official Tests on Server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'EOF'
    cd /opt/autoppia-miner
    git pull origin main
    
    echo ""
    echo "Running official test suite..."
    echo ""
    python3 tests/test_official.py http://localhost:8080
EOF

