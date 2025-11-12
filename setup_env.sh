#!/bin/bash
# Setup script to create .env file with Chutes API key

echo "Setting up Autoppia Worker environment..."

# Create .env file from env.example
if [ ! -f .env ]; then
    cp env.example .env
    echo "✓ Created .env file from env.example"
else
    echo "⚠ .env file already exists, skipping creation"
    echo "  To update it, edit .env manually or delete it and run this script again"
fi

# Verify Chutes API key is set
if grep -q "CHUTES_API_KEY=cpk_" .env 2>/dev/null; then
    echo "✓ Chutes API key is configured in .env"
else
    echo "⚠ Chutes API key not found in .env"
fi

echo ""
echo "Setup complete! Next steps:"
echo "1. Review and edit .env file if needed"
echo "2. Install dependencies: pip install -r requirements.txt"
echo "3. Test the worker: python example_usage.py"
echo "4. Run the API server: python api.py"

