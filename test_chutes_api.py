#!/usr/bin/env python3
"""Test script to determine Chutes API format"""
import asyncio
import httpx
import json
import os

CHUTES_API_KEY = "cpk_5bcbb7216ed743229e4a4ca4bd875f79.97cdedde58e45965820657bd8ec790fa.lXEjoNHFlkwgNb2wK9xTN0Ex3YmkOF8u"

async def test_chutes_api():
    """Test different Chutes API endpoints and formats"""
    client = httpx.AsyncClient(timeout=10.0)
    
    headers = {
        "Authorization": f"Bearer {CHUTES_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test URLs
    urls = [
        "https://api.chutes.ai/v1/chat/completions",
        "https://chutes.ai/api/v1/chat/completions",
        "https://api.chutes.ai/v1/completions",
        "https://chutes.ai/api/chat/completions",
    ]
    
    # Test payloads
    payloads = [
        {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 10
        },
        {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 10
        },
        {
            "prompt": "Say hello",
            "model": "gpt-4o-mini",
            "max_tokens": 10
        }
    ]
    
    print("Testing Chutes API endpoints...")
    print("=" * 60)
    
    for url in urls:
        for i, payload in enumerate(payloads):
            try:
                print(f"\nTrying: {url}")
                print(f"Payload format {i+1}: {list(payload.keys())}")
                
                response = await client.post(url, headers=headers, json=payload, timeout=10.0)
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ SUCCESS!")
                    print(f"Response keys: {list(result.keys())}")
                    print(f"Response sample: {json.dumps(result, indent=2)[:500]}")
                    return url, payload
                elif response.status_code == 401:
                    print(f"❌ Auth error - check API key")
                elif response.status_code == 404:
                    print(f"⚠️  Not found - trying next...")
                else:
                    print(f"Response: {response.text[:200]}")
                    
            except httpx.TimeoutException:
                print(f"⏱️  Timeout")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Could not find working endpoint. Check API key and documentation.")
    return None, None

if __name__ == "__main__":
    result = asyncio.run(test_chutes_api())
    if result[0]:
        print(f"\n✅ Working endpoint: {result[0]}")
        print(f"✅ Working payload format: {result[1]}")

