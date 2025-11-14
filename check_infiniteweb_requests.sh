#!/bin/bash
# Check what requests InfiniteWeb Arena is making

echo "=== Recent API Requests from InfiniteWeb Arena ==="
journalctl -u autoppia-api -n 200 --no-pager | grep -E "Received task|Task prompt|Task URL|actions|Error|error|Exception|Classified" | tail -100

echo ""
echo "=== Testing with InfiniteWeb Arena-like request ==="
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-iwa",
    "prompt": "First, authenticate with username test and password password123 to log in successfully.",
    "url": ""
  }' -v 2>&1 | grep -A 50 "< HTTP"

