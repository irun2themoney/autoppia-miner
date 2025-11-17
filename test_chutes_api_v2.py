#!/usr/bin/env python3
"""Test Chutes API with different authentication methods"""
import asyncio
import httpx
import json

CHUTES_API_KEY = "cpk_5bcbb7216ed743229e4a4ca4bd875f79.97cdedde58e45965820657bd8ec790fa.lXEjoNHFlkwgNb2wK9xTN0Ex3YmkOF8u"

async def test():
    client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)
    
    # Try different auth header formats
    auth_formats = [
        {"Authorization": f"Bearer {CHUTES_API_KEY}"},
        {"Authorization": f"Token {CHUTES_API_KEY}"},
        {"X-API-Key": CHUTES_API_KEY},
        {"api-key": CHUTES_API_KEY},
        {"x-api-key": CHUTES_API_KEY},
    ]
    
    # Try different base URLs
    base_urls = [
        "https://api.chutes.ai",
        "https://chutes.ai",
        "https://chutesapi.com",
        "https://api.chutesapi.com",
    ]
    
    endpoints = [
        "/v1/chat/completions",
        "/chat/completions",
        "/v1/completions",
        "/completions",
        "/api/v1/chat/completions",
        "/api/chat/completions",
    ]
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10
    }
    
    print("Testing Chutes API with different formats...")
    print("=" * 70)
    
    for base_url in base_urls:
        for endpoint in endpoints:
            for auth_name, auth_headers in [("Bearer", auth_formats[0]), ("X-API-Key", auth_formats[2])]:
                url = f"{base_url}{endpoint}"
                headers = {
                    "Content-Type": "application/json",
                    **auth_headers
                }
                
                try:
                    response = await client.post(url, headers=headers, json=payload, timeout=5.0)
                    
                    if response.status_code != 404:
                        print(f"\n🔍 {url}")
                        print(f"   Auth: {auth_name}")
                        print(f"   Status: {response.status_code}")
                        if response.status_code == 200:
                            result = response.json()
                            print(f"   ✅ SUCCESS!")
                            print(f"   Response: {json.dumps(result, indent=2)[:300]}")
                            return url, auth_headers
                        else:
                            print(f"   Response: {response.text[:150]}")
                            
                except Exception as e:
                    pass  # Skip errors, just try next
    
    print("\n" + "=" * 70)
    print("⚠️  Could not find working endpoint.")
    print("\n💡 Suggestions:")
    print("   1. Check Chutes documentation for correct endpoint")
    print("   2. Verify API key is active")
    print("   3. Try using OpenAI-compatible proxy service")
    return None, None

if __name__ == "__main__":
    result = asyncio.run(test())

