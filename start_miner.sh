#!/bin/bash

# Quick start script for Bittensor miner
# Usage: ./start_miner.sh [wallet_name] [hotkey_name]

WALLET_NAME=${1:-"default"}
HOTKEY_NAME=${2:-"default"}
NETWORK=${3:-"finney"}
PORT=${4:-"8091"}

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🚀 STARTING BITTENSOR MINER 🚀                        ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Wallet: $WALLET_NAME"
echo "Hotkey: $HOTKEY_NAME"
echo "Network: $NETWORK"
echo "Port: $PORT"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "   Creating from env.example..."
    cp env.example .env
    echo "   Please edit .env and set your CHUTES_API_KEY and API_URL"
    echo ""
fi

# Check if bittensor is installed
if ! python3 -c "import bittensor" 2>/dev/null; then
    echo "⚠️  Bittensor not installed!"
    echo "   Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Check if wallet exists
if ! btcli wallet list | grep -q "$WALLET_NAME"; then
    echo "⚠️  Wallet '$WALLET_NAME' not found!"
    echo "   Create it with: btcli wallet create --name $WALLET_NAME"
    echo ""
    exit 1
fi

# Check registration
echo "🔍 Checking registration on subnet 36..."
REGISTERED=$(btcli wallet overview --netuid 36 --wallet.name "$WALLET_NAME" --wallet.hotkey "$HOTKEY_NAME" 2>/dev/null | grep -c "UID:" || echo "0")

if [ "$REGISTERED" -eq "0" ]; then
    echo "⚠️  Not registered on subnet 36!"
    echo "   Register with:"
    echo "   btcli subnet register --netuid 36 --wallet.name $WALLET_NAME --wallet.hotkey $HOTKEY_NAME"
    echo ""
    read -p "Do you want to register now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        btcli subnet register --netuid 36 --wallet.name "$WALLET_NAME" --wallet.hotkey "$HOTKEY_NAME"
    else
        echo "Exiting. Please register first."
        exit 1
    fi
fi

echo ""
echo "🚀 Starting miner..."
echo ""

# Start miner
python3 miner.py \
    --wallet.name "$WALLET_NAME" \
    --wallet.hotkey "$HOTKEY_NAME" \
    --network "$NETWORK" \
    --axon.port "$PORT"

