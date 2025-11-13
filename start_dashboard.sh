#!/usr/bin/env bash
# Quick start script for the Autoppia Miner Dashboard
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Autoppia Miner Dashboard..."
echo ""

# Check if virtual environment exists
if [ ! -d "test_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv test_env
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source test_env/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi; import uvicorn" 2>/dev/null; then
    echo "📚 Installing dashboard dependencies..."
    pip install -q fastapi uvicorn pydantic
fi

# Verify dashboard file exists
if [ ! -f "dashboard.py" ]; then
    echo "❌ dashboard.py not found in $(pwd)"
    echo "Available files:"
    ls -la *.py 2>/dev/null || echo "No Python files found"
    exit 1
fi

# Start dashboard with error handling
echo ""
echo "📊 Dashboard starting on http://localhost:8090"
echo "📖 Press Ctrl+C to stop"
echo ""

trap 'echo "Shutting down..."; exit 0' INT TERM

python dashboard.py 2>&1 || {
    EXIT_CODE=$?
    echo "❌ Dashboard failed with exit code $EXIT_CODE"
    exit $EXIT_CODE
}

