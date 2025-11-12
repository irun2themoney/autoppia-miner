#!/bin/bash
# Test script for deployed Autoppia Worker

# Get URL from user or use default
WORKER_URL="${1:-}"

if [ -z "$WORKER_URL" ]; then
    echo "Usage: ./test_deployed_worker.sh <your-render-url>"
    echo "Example: ./test_deployed_worker.sh https://autoppia-miner.onrender.com"
    exit 1
fi

echo "🧪 Testing Autoppia Worker at: $WORKER_URL"
echo ""

# Test 1: Health Check
echo "1️⃣ Health Check:"
echo "   GET $WORKER_URL/health"
HEALTH_RESPONSE=$(curl -s "$WORKER_URL/health")
echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""

# Test 2: Metadata
echo "2️⃣ Metadata:"
echo "   GET $WORKER_URL/metadata"
METADATA_RESPONSE=$(curl -s "$WORKER_URL/metadata")
echo "$METADATA_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$METADATA_RESPONSE"
echo ""

# Test 3: Process Task
echo "3️⃣ Process Task:"
echo "   POST $WORKER_URL/process"
PROCESS_RESPONSE=$(curl -s -X POST "$WORKER_URL/process" \
  -H "Content-Type: application/json" \
  -d '{"task": "process", "input_data": {"data": ["test1", "test2", "test3"]}}')
echo "$PROCESS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$PROCESS_RESPONSE"
echo ""

# Test 4: Mine Task
echo "4️⃣ Mine Task:"
echo "   POST $WORKER_URL/process"
MINE_RESPONSE=$(curl -s -X POST "$WORKER_URL/process" \
  -H "Content-Type: application/json" \
  -d '{"task": "mine", "input_data": {"source": "test_source", "pattern": "test_pattern"}}')
echo "$MINE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$MINE_RESPONSE"
echo ""

# Test 5: Generate Task
echo "5️⃣ Generate Task:"
echo "   POST $WORKER_URL/process"
GENERATE_RESPONSE=$(curl -s -X POST "$WORKER_URL/process" \
  -H "Content-Type: application/json" \
  -d '{"task": "generate", "input_data": {"prompt": "Hello, world!"}}')
echo "$GENERATE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$GENERATE_RESPONSE"
echo ""

echo "✅ Testing complete!"
echo ""
echo "💡 Your worker is live at: $WORKER_URL"
echo "📚 API Documentation: See README.md"
echo "🔗 Share this URL with others to use your worker!"

