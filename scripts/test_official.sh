#!/bin/bash
# Official testing script for Autoppia IWA miner
# Based on official Autoppia testing procedures

set -e

API_URL="${1:-http://localhost:8080}"
echo "Testing miner at: $API_URL"
echo ""

# Test 1: Health endpoint
echo "Test 1: Health Endpoint"
if curl -s -f "$API_URL/health" > /dev/null; then
    echo "✅ Health endpoint: PASS"
else
    echo "❌ Health endpoint: FAIL"
    exit 1
fi
echo ""

# Test 2: CORS headers
echo "Test 2: CORS Headers"
CORS_RESPONSE=$(curl -s -X OPTIONS "$API_URL/solve_task" \
    -H "Origin: https://infinitewebarena.autoppia.com" \
    -H "Access-Control-Request-Method: POST" \
    -i | grep -i "access-control")
if [ -n "$CORS_RESPONSE" ]; then
    echo "✅ CORS headers: PASS"
else
    echo "❌ CORS headers: FAIL"
    exit 1
fi
echo ""

# Test 3: solve_task endpoint
echo "Test 3: solve_task Endpoint"
TASK_RESPONSE=$(curl -s -X POST "$API_URL/solve_task" \
    -H "Content-Type: application/json" \
    -d '{"id":"test-001","prompt":"Click button","url":"https://example.com"}')
if echo "$TASK_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); assert 'actions' in data and 'web_agent_id' in data" 2>/dev/null; then
    ACTION_COUNT=$(echo "$TASK_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['actions']))")
    echo "✅ solve_task endpoint: PASS (generated $ACTION_COUNT actions)"
else
    echo "❌ solve_task endpoint: FAIL"
    exit 1
fi
echo ""

# Test 4: Response time
echo "Test 4: Response Time"
START_TIME=$(date +%s.%N)
curl -s -X POST "$API_URL/solve_task" \
    -H "Content-Type: application/json" \
    -d '{"id":"test-speed","prompt":"Navigate","url":"https://example.com"}' > /dev/null
END_TIME=$(date +%s.%N)
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)
if (( $(echo "$ELAPSED < 2.0" | bc -l) )); then
    echo "✅ Response time: PASS (${ELAPSED}s)"
else
    echo "❌ Response time: FAIL (${ELAPSED}s - too slow)"
    exit 1
fi
echo ""

# Test 5: Action format
echo "Test 5: Action Format"
FORMAT_CHECK=$(curl -s -X POST "$API_URL/solve_task" \
    -H "Content-Type: application/json" \
    -d '{"id":"test-format","prompt":"Login with username:test password:test","url":"https://example.com"}' | \
    python3 -c "
import sys, json
data = json.load(sys.stdin)
actions = data.get('actions', [])
for action in actions:
    assert 'type' in action, 'Missing type'
    if action['type'] == 'NavigateAction':
        assert 'url' in action, 'NavigateAction missing url'
    elif action['type'] == 'ClickAction':
        assert 'selector' in action, 'ClickAction missing selector'
    elif action['type'] == 'TypeAction':
        assert 'selector' in action and 'text' in action, 'TypeAction missing fields'
print('OK')
" 2>&1)
if [ "$FORMAT_CHECK" = "OK" ]; then
    echo "✅ Action format: PASS"
else
    echo "❌ Action format: FAIL"
    echo "$FORMAT_CHECK"
    exit 1
fi
echo ""

echo "=========================================="
echo "✅ ALL OFFICIAL TESTS PASSED"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test on IWA Playground: https://infinitewebarena.autoppia.com/playground"
echo "2. Set up HTTPS tunnel if needed"
echo "3. Monitor validator activity"
echo ""

