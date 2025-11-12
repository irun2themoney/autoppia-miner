#!/usr/bin/env python3
"""Test script to explore Chutes API endpoints"""

import asyncio
import httpx
import json
from dotenv import load_dotenv
import os

load_dotenv()

CHUTES_API_KEY = os.getenv("CHUTES_API_KEY")
CHUTES_API_URL = os.getenv("CHUTES_API_URL", "https://api.chutes.ai")

async def test_endpoints():
    """Test different Chutes API endpoints"""
    
    headers = {
        "Authorization": f"Bearer {CHUTES_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(base_url=CHUTES_API_URL, headers=headers, timeout=10.0) as client:
        # Test 1: Root endpoint
        print("=" * 60)
        print("Test 1: Root endpoint (/)")
        print("=" * 60)
        try:
            r = await client.get("/")
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text[:500]}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 2: List chutes
        print("\n" + "=" * 60)
        print("Test 2: List chutes (/chutes/)")
        print("=" * 60)
        try:
            r = await client.get("/chutes/")
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text[:500]}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 3: Chat completions
        print("\n" + "=" * 60)
        print("Test 3: Chat completions (/v1/chat/completions)")
        print("=" * 60)
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        try:
            r = await client.post("/v1/chat/completions", json=payload)
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text[:500]}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 4: Health endpoint
        print("\n" + "=" * 60)
        print("Test 4: Health endpoint (/health)")
        print("=" * 60)
        try:
            r = await client.get("/health")
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text[:500]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if not CHUTES_API_KEY:
        print("ERROR: CHUTES_API_KEY not found in environment")
        exit(1)
    
    print(f"Testing Chutes API at: {CHUTES_API_URL}")
    print(f"API Key: {CHUTES_API_KEY[:30]}...")
    print()
    
    asyncio.run(test_endpoints())

