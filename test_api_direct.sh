#!/bin/bash
# Direct API test without json.tool to see raw response

echo "Testing API directly..."
echo ""

API_URL="http://localhost:8080"

echo "Test 1: Simple request"
curl -X POST ${API_URL}/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-001",
    "prompt": "Login with username test and password password123",
    "url": ""
  }' -v 2>&1 | head -50

echo ""
echo "Checking API status..."
systemctl status autoppia-api --no-pager | head -20

echo ""
echo "Recent API logs..."
journalctl -u autoppia-api -n 20 --no-pager | tail -20

