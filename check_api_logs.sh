#!/bin/bash
# Check API logs to diagnose empty actions issue

echo "=== Recent API Logs ==="
journalctl -u autoppia-api -n 100 --no-pager | grep -E "Received task|Classified|actions|Error|error|Exception" | tail -50

echo ""
echo "=== Testing API with sample request ==="
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-001",
    "prompt": "Login with username test and password test123",
    "url": "https://example.com"
  }' | python3 -m json.tool

