#!/bin/bash
# Wrapper script to start miner with environment variables from .env
set -e

# Load environment variables from .env
if [ -f /opt/autoppia-miner/.env ]; then
    export $(cat /opt/autoppia-miner/.env | grep -v '^#' | xargs)
fi

# Start miner with proper arguments
cd /opt/autoppia-miner
exec /opt/autoppia-miner/venv/bin/python3 -m miner.miner \
    --wallet.name "${WALLET_NAME:-default}" \
    --wallet.hotkey "${WALLET_HOTKEY:-default}" \
    --netuid "${SUBNET_UID:-36}" \
    --subtensor.network "${NETWORK:-finney}" \
    --axon.port "${AXON_PORT:-8091}"
