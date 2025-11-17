#!/usr/bin/env python3
"""Final test for Chutes API"""
import asyncio
import httpx
import json

CHUTES_API_KEY = "cpk_5bcbb7216ed743229e4a4ca4bd875f79.97cdedde58e45965820657bd8ec790fa.lXEjoNHFlkwgNb2wK9xTN0Ex3YmkOF8u"

async def test():
    client = httpx.AsyncClient(timeout=10.0)
    
    url = "https://api.chutes.ai/chat/completions"
    
    # Try different auth formats
    auth_configs = [
        {"X-API-Key": CHUTES_API_KEY},
        {"Authorization": f"Bearer {CHUTES_API_KEY}"},
        {"Authorization": f"Token {CHUTES_API_KEY}"},
        {"api-key": CHUTES_API_KEY},
    ]
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10
    }
    
    print("Testing Chutes API authentication...")
    print("=" * 60)
    
    for i, headers in enumerate(auth_configs):
        headers["Content-Type"] = "application/json"
        auth_type = list(headers.keys())[0]
        
        try:
            print(f"\nTrying {auth_type}...")
            response = await client.post(url, headers=headers, json=payload, timeout=10.0)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS with {auth_type}!")
                print(f"Response: {json.dumps(result, indent=2)}")
                return url, headers
            elif response.status_code == 401:
                print(f"❌ Auth failed")
            elif response.status_code == 429:
                print(f"⚠️  Rate limited (but endpoint works!)")
                print(f"Response: {response.text[:200]}")
                # This might be the right format, just rate limited
                return url, headers
            else:
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    return None, None

if __name__ == "__main__":
    result = asyncio.run(test())
    if result[0]:
        print(f"\n✅ Working endpoint: {result[0]}")
        print(f"✅ Working headers: {list(result[1].keys())[0]}")

