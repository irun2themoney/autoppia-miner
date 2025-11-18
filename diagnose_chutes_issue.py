#!/usr/bin/env python3
"""Comprehensive Chutes API diagnostic"""
import httpx
import asyncio
import os
import time
from dotenv import load_dotenv

load_dotenv()

async def diagnose():
    api_key = os.getenv("CHUTES_API_KEY")
    
    print("🔍 Chutes API Comprehensive Diagnostic")
    print("=" * 50)
    print()
    
    if not api_key:
        print("❌ CHUTES_API_KEY not found in environment")
        return
    
    print(f"✅ API Key: {api_key[:30]}...")
    print(f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    client = httpx.AsyncClient(timeout=30.0)
    
    # Test 1: Basic API call
    print("Test 1: Basic API Call")
    print("-" * 50)
    try:
        resp = await client.post(
            "https://api.chutes.ai/v1/chat/completions",
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            },
            json={
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            }
        )
        
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        
        if resp.status_code == 429:
            print("\n❌ RATE LIMITED")
            print("\nPossible Causes:")
            print("  1. Account-level rate limiting")
            print("  2. IP-based rate limiting (server IP blocked)")
            print("  3. API key used elsewhere")
            print("  4. Rate limit hasn't reset")
            print("\nNext Steps:")
            print("  1. Check Chutes dashboard for account usage")
            print("  2. Contact Chutes support (see contact_chutes_support.md)")
            print("  3. Try generating a new API key")
            print("  4. Test from different IP")
        elif resp.status_code == 200:
            print("\n✅ SUCCESS - API is working!")
        elif resp.status_code == 401:
            print("\n❌ AUTHENTICATION FAILED")
            print("Check API key is correct")
        else:
            print(f"\n❌ ERROR: {resp.status_code}")
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
    
    print()
    
    # Test 2: Check if it's IP-based
    print("Test 2: Checking Response Headers")
    print("-" * 50)
    try:
        resp = await client.post(
            "https://api.chutes.ai/v1/chat/completions",
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            },
            json={
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            }
        )
        
        print("Response Headers:")
        rate_limit_headers = []
        for key, value in resp.headers.items():
            if 'rate' in key.lower() or 'retry' in key.lower() or 'limit' in key.lower():
                rate_limit_headers.append(f"  {key}: {value}")
        
        if rate_limit_headers:
            for header in rate_limit_headers:
                print(header)
        else:
            print("  ❌ No rate limit headers found")
            print("  (Chutes doesn't provide Retry-After or X-RateLimit-* headers)")
        
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    print()
    print("=" * 50)
    print("📋 Summary:")
    print("=" * 50)
    print()
    print("If you're getting 429 errors:")
    print("  1. Check Chutes dashboard: ./check_chutes_dashboard.sh")
    print("  2. Contact support: See contact_chutes_support.md")
    print("  3. Try new API key: Generate in Chutes dashboard")
    print("  4. Test from different IP: Try from local machine")
    print()
    
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(diagnose())

