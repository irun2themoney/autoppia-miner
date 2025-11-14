#!/usr/bin/env python3
"""Quick test script for API"""

import requests
import json

API_URL = "http://localhost:8080"

def test_solve_task(prompt: str, url: str = "https://example.com"):
    """Test solve_task endpoint"""
    response = requests.post(
        f"{API_URL}/solve_task",
        json={
            "id": "test-123",
            "prompt": prompt,
            "url": url
        }
    )
    
    print(f"\n📝 Prompt: {prompt}")
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        actions = data.get("actions", [])
        print(f"✅ Actions: {len(actions)}")
        
        # Show first click action if exists
        click_action = next((a for a in actions if a.get("type") == "ClickAction"), None)
        if click_action:
            selector = click_action.get("selector", {})
            print(f"   ClickAction selector: {selector.get('type')} -> {selector.get('value')}")
        
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

if __name__ == "__main__":
    print("🧪 Testing IWA API\n")
    
    # Test cases
    tests = [
        ("Switch to month view in the calendar", "https://example.com"),
        ("Click the login button", "https://example.com"),
        ("Search for products", "https://example.com"),
        ("Fill in email field", "https://example.com"),
    ]
    
    results = []
    for prompt, url in tests:
        results.append(test_solve_task(prompt, url))
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} passed")

