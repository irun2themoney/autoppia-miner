#!/bin/bash
# Quick Playground Test Script

API_ENDPOINT="http://134.199.203.133:8080/solve_task"

echo "🧪 Quick Playground Test"
echo "======================="
echo ""

# Test the exact playground scenario
TASK_ID="4318e05c-000d-4cef-8064-dbc5a81c5cb7"
URL="https://autobooks.autoppia.com"
PROMPT="First, authenticate with username 'user<web_agent_id>' and password 'PASSWORD'. Then, register a book with a rating equal to 0.5, a page count less than or equal to 450, and an author whose name contains 'rebel'."

echo "📋 Test Details:"
echo "  Task ID: $TASK_ID"
echo "  URL: $URL"
echo "  Prompt: ${PROMPT:0:80}..."
echo ""

# Make request
echo "🚀 Sending request..."
RESPONSE=$(curl -s -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"$TASK_ID\",
    \"url\": \"$URL\",
    \"prompt\": \"$PROMPT\"
  }")

# Analyze response
echo "📊 Response Analysis:"
echo "$RESPONSE" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f\"  ✅ Status: Valid JSON\")
    print(f\"  ✅ Actions: {len(d.get('actions', []))}\")
    print(f\"  ✅ Has webAgentId: {'webAgentId' in d}\")
    print(f\"  ✅ Size: {len(json.dumps(d))} bytes\")
    print(f\"\")
    print(f\"  📋 Action Types:\")
    types = {}
    for a in d.get('actions', []):
        t = a.get('type', 'Unknown')
        types[t] = types.get(t, 0) + 1
    for t, c in types.items():
        print(f\"    {t}: {c}\")
    print(f\"\")
    if len(d.get('actions', [])) == 0:
        print(f\"  ❌ CRITICAL: Actions array is EMPTY!\")
    else:
        print(f\"  ✅ Response is valid and ready for playground\")
except Exception as e:
    print(f\"  ❌ Error parsing response: {e}\")
    print(f\"  Raw response: {sys.stdin.read()[:200]}\")
"

echo ""
echo "💡 Next Steps:"
echo "   1. Copy the response JSON above"
echo "   2. Test it in the IWA playground"
echo "   3. Check diagnostic report: curl http://134.199.203.133:8080/diagnostic/empty-actions"
echo "   4. Monitor logs: ssh root@134.199.203.133 'journalctl -u autoppia-api -f'"

