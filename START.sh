#!/bin/bash
# Quick start script for Autoppia Miner

echo "🚀 Starting Autoppia Miner"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from env.example..."
    cp env.example .env
    echo "📝 Please edit .env with your configuration"
fi

echo ""
echo "✅ Ready to start!"
echo ""
echo "Start API server:"
echo "  python3 -m api.server"
echo ""
echo "Start miner (in another terminal):"
echo "  python3 -m miner.miner --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY"
