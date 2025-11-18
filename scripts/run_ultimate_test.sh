#!/bin/bash
# Ultimate End-to-End Test Runner
# Tests the entire miner flow from validator request to response

set -e

API_URL="${1:-http://localhost:8080}"

echo "🚀 ULTIMATE END-TO-END TEST SUITE"
echo "=================================="
echo "API URL: $API_URL"
echo ""

# Check if API is running
echo "📡 Checking API availability..."
if ! curl -s -f "$API_URL/health" > /dev/null; then
    echo "❌ API is not running at $API_URL"
    echo "   Start the API with: python3 -m api.server"
    exit 1
fi
echo "✅ API is running"
echo ""

# Run ultimate test suite
echo "🧪 Running Ultimate Test Suite..."
python3 tests/test_ultimate.py "$API_URL"

echo ""
echo "✅ Ultimate test suite complete!"
echo ""
echo "📊 Review the results above for compliance verification."

