#!/usr/bin/env python3
"""Test API endpoints"""
import requests
import json
from config.settings import settings

API_URL = f"http://localhost:{settings.api_port}"

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
    
    # Test various prompts
    test_solve_task("Switch to month view in the calendar")
    test_solve_task("Click the submit button")
    test_solve_task("Type your email address")
    test_solve_task("Search for something")

