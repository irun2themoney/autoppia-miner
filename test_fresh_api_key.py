#!/usr/bin/env python3
"""Test if API key is actually rate limited or if there's another issue"""
import httpx
import asyncio
import os
import time
from dotenv import load_dotenv

load_dotenv()

async def test():
    api_key = os.getenv("CHUTES_API_KEY")
    print(f"Testing Chutes API with fresh request...")
    print(f"API Key: {api_key[:30]}...")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    client = httpx.AsyncClient(timeout=30.0)
    
    try:
        # Make a single test request
        print("Making test request...")
        resp = await client.post(
            "https://api.chutes.ai/v1/chat/completions",
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            },
            json={
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "messages": [{"role": "user", "content": "Say hello"}],
                "max_tokens": 10
            }
        )
        
        print(f"Status: {resp.status_code}")
        print(f"Response Headers:")
        for key, value in resp.headers.items():
            if key.lower() in ['retry-after', 'x-ratelimit', 'content-type']:
                print(f"  {key}: {value}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"\n✅ SUCCESS!")
            print(f"Response: {data.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
        elif resp.status_code == 429:
            print(f"\n❌ RATE LIMITED")
            print(f"Response: {resp.text[:200]}")
            print(f"\nThis suggests:")
            print(f"  1. Account-level rate limiting (not just API key)")
            print(f"  2. IP-based rate limiting (server IP is blocked)")
            print(f"  3. API key is used elsewhere and account is rate limited")
            print(f"  4. Rate limit hasn't reset yet (check dashboard)")
        elif resp.status_code == 401:
            print(f"\n❌ AUTHENTICATION FAILED")
            print(f"Check API key is correct")
        else:
            print(f"\n❌ ERROR: {resp.status_code}")
            print(f"Response: {resp.text[:200]}")
        
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test())

