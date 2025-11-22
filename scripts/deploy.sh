#!/bin/bash

# Unified Deployment Script for Autoppia Miner
# Usage: ./scripts/deploy.sh [option]
# Options:
#   --all       Deploy everything (API, Miner, Dashboard, Live Analysis)
#   --dashboard Only deploy dashboard updates
#   --miner     Only deploy miner updates
#   --help      Show this help message

set -e

# Configuration
SERVER_IP="134.199.203.133"
USER="root"
MINER_DIR="/opt/autoppia-miner"

function show_help {
    echo "Usage: ./scripts/deploy.sh [option]"
    echo "Options:"
    echo "  --all       Deploy everything (API, Miner, Dashboard, Live Analysis)"
    echo "  --dashboard Only deploy dashboard updates"
    echo "  --miner     Only deploy miner updates"
    echo "  --help      Show this help message"
}

function deploy_all {
    echo "🚀 Deploying ALL components..."
    
    # 1. Push changes
    echo "📤 Pushing local changes..."
    git add .
    git commit -m "Deployment $(date +%Y-%m-%d_%H-%M-%S)" || true
    git push

    # 2. Execute remote update
    echo "🔄 Updating server..."
    ssh $USER@$SERVER_IP "cd $MINER_DIR && \
        git pull && \
        pip install -r requirements.txt && \
        python3 -m playwright install chromium || echo '⚠️  Playwright browsers already installed or installation failed' && \
        sudo systemctl restart autoppia-api autoppia-miner"
        
    echo "✅ Deployment Complete!"
}

function deploy_dashboard {
    echo "🚀 Deploying Dashboard..."
    ssh $USER@$SERVER_IP "cd $MINER_DIR && \
        git pull && \
        sudo systemctl restart autoppia-api"
    echo "✅ Dashboard Deployed!"
}

# Main logic
if [ "$1" == "--all" ]; then
    deploy_all
elif [ "$1" == "--dashboard" ]; then
    deploy_dashboard
elif [ "$1" == "--help" ]; then
    show_help
else
    # Default interactive mode
    echo "Select deployment type:"
    echo "1) Deploy Everything (Recommended)"
    echo "2) Deploy Dashboard Only"
    read -p "Enter choice [1]: " choice
    choice=${choice:-1}
    
    if [ "$choice" == "1" ]; then
        deploy_all
    elif [ "$choice" == "2" ]; then
        deploy_dashboard
    else
        echo "Invalid choice"
        exit 1
    fi
fi
