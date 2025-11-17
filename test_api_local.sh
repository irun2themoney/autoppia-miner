#!/bin/bash
# Test the API locally to see Chutes/Qwen in action

echo "🧪 Testing Autoppia API with Chutes/Qwen..."
echo "=" | head -c 60 && echo ""

# Test 1: Health check
echo "1️⃣  Health Check:"
curl -s http://134.199.203.133:8080/health | python3 -m json.tool
echo ""

# Test 2: Simple task
echo "2️⃣  Simple Task (Click login button):"
curl -s -X POST http://134.199.203.133:8080/solve_task \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "test-1",
    "prompt": "Click the login button",
    "url": "https://example.com"
  }' | python3 -m json.tool | head -30
echo ""

# Test 3: Complex task
echo "3️⃣  Complex Task (Navigate and fill form):"
curl -s -X POST http://134.199.203.133:8080/solve_task \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "test-2",
    "prompt": "Navigate to https://example.com, fill in username field with testuser, and click submit",
    "url": "https://example.com"
  }' | python3 -m json.tool | head -40
echo ""

echo "✅ Tests complete!"
echo ""
echo "💡 Note: If you see template-style actions (lots of ScreenshotActions),"
echo "   the Chutes API might be rate-limited. Wait a few minutes and try again."

