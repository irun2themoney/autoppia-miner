#!/bin/bash
# Wait for Chutes API rate limit to reset and notify when it's working

SERVER="root@134.199.203.133"
PASSWORD="DigitalOcean4life"

echo "⏳ Waiting for Chutes API rate limit to reset..."
echo "This will check every 30 seconds"
echo "Press Ctrl+C to stop"
echo ""

while true; do
    # Test Chutes API directly
    result=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER" "cd /opt/autoppia-miner && python3 << 'PYEOF'
import asyncio
import httpx

async def test():
    api_key = 'cpk_5bcbb7216ed743229e4a4ca4bd875f79.97cdedde58e45965820657bd8ec790fa.lXEjoNHFlkwgNb2wK9xTN0Ex3YmkOF8u'
    url = 'https://api.chutes.ai/v1/chat/completions'
    headers = {'X-API-Key': api_key, 'Content-Type': 'application/json'}
    payload = {'model': 'Qwen/Qwen2.5-7B-Instruct', 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 5}
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        print('OK' if response.status_code == 200 else 'RATE_LIMITED')
asyncio.run(test())
PYEOF
" 2>/dev/null)
    
    timestamp=$(date '+%H:%M:%S')
    
    if [ "$result" = "OK" ]; then
        echo ""
        echo "🎉 SUCCESS! Chutes API is now working! ($timestamp)"
        echo "   The miner will now use Qwen LLM for intelligent task solving"
        echo ""
        # Test the actual API endpoint
        echo "Testing API endpoint..."
        curl -s -X POST http://134.199.203.133:8080/solve_task \
          -H 'Content-Type: application/json' \
          -d '{"id": "test", "prompt": "Click login", "url": "https://example.com"}' \
          | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'Generated {len(data.get(\"actions\", []))} actions')" 2>/dev/null
        break
    else
        echo "[$timestamp] ⏳ Still rate limited... checking again in 30s"
    fi
    
    sleep 30
done

