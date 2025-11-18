#!/usr/bin/env python3
"""Test the new Chutes API key"""
import httpx
import asyncio
import os
import time
from dotenv import load_dotenv

load_dotenv()

async def test():
    # Use the new API key directly
    api_key = "cpk_ab5e547a25144171a381d453f6561412.97cdedde58e45965820657bd8ec790fa.2kj7lx8g8tdFwjb1tJbsOVX1e8l711o1"
    
    print("🧪 Testing NEW Chutes API Key")
    print("=" * 50)
    print(f"API Key: {api_key[:30]}...")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    client = httpx.AsyncClient(timeout=30.0)
    
    try:
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
        
        if resp.status_code == 200:
            data = resp.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')
            print(f"\n✅ SUCCESS! API Key is working!")
            print(f"Response: {content}")
            return True
        elif resp.status_code == 429:
            print(f"\n❌ STILL RATE LIMITED")
            print(f"Response: {resp.text[:200]}")
            print(f"\nThis suggests account-level or IP-based rate limiting")
            return False
        elif resp.status_code == 401:
            print(f"\n❌ AUTHENTICATION FAILED")
            print(f"Check API key is correct")
            return False
        else:
            print(f"\n❌ ERROR: {resp.status_code}")
            print(f"Response: {resp.text[:200]}")
            return False
        
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        return False
    finally:
        await client.aclose()

if __name__ == "__main__":
    result = asyncio.run(test())
    exit(0 if result else 1)

