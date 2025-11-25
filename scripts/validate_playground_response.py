#!/usr/bin/env python3
"""
Validate API Response for Playground Compatibility

This script validates that the API response matches exactly what the playground expects.
"""

import requests
import json
import sys
from typing import Dict, Any, List

API_ENDPOINT = "http://134.199.203.133:8080/solve_task"

def validate_response(response_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate response format matches playground expectations"""
    errors = []
    
    # Check required fields
    required_fields = ["actions", "webAgentId", "recording"]
    for field in required_fields:
        if field not in response_data:
            errors.append(f"Missing required field: {field}")
    
    # Check actions is not empty
    actions = response_data.get("actions", [])
    if not isinstance(actions, list):
        errors.append(f"Actions must be a list, got {type(actions)}")
    elif len(actions) == 0:
        errors.append("Actions array is empty")
    
    # Validate each action
    for i, action in enumerate(actions):
        if not isinstance(action, dict):
            errors.append(f"Action {i} is not a dictionary")
            continue
        
        # Check action type
        action_type = action.get("type")
        if not action_type:
            errors.append(f"Action {i} missing 'type' field")
        
        # Check camelCase fields
        if action_type == "WaitAction":
            if "timeSeconds" not in action:
                errors.append(f"Action {i} (WaitAction) missing 'timeSeconds' field")
            if "time_seconds" in action or "duration" in action:
                errors.append(f"Action {i} (WaitAction) has snake_case field (should be camelCase)")
        
        # Check selectors
        if "selector" in action:
            selector = action["selector"]
            if isinstance(selector, dict):
                if "caseSensitive" not in selector:
                    errors.append(f"Action {i} selector missing 'caseSensitive' field")
                if "case_sensitive" in selector:
                    errors.append(f"Action {i} selector has snake_case 'case_sensitive' (should be 'caseSensitive')")
    
    # Check for extra fields that might confuse playground
    allowed_fields = {"actions", "webAgentId", "web_agent_id", "recording"}
    extra_fields = set(response_data.keys()) - allowed_fields
    if extra_fields:
        errors.append(f"Extra fields that might confuse playground: {extra_fields}")
    
    return len(errors) == 0, errors


def test_playground_scenario():
    """Test the exact playground scenario"""
    payload = {
        "id": "4318e05c-000d-4cef-8064-dbc5a81c5cb7",
        "url": "https://autobooks.autoppia.com",
        "prompt": "First, authenticate with username 'user<web_agent_id>' and password 'PASSWORD'. Then, register a book with a rating equal to 0.5, a page count less than or equal to 450, and an author whose name contains 'rebel'."
    }
    
    print("🧪 Testing Playground Scenario")
    print("=" * 60)
    print(f"Task ID: {payload['id']}")
    print(f"URL: {payload['url']}")
    print(f"Prompt: {payload['prompt'][:80]}...")
    print()
    
    try:
        response = requests.post(API_ENDPOINT, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
        
        data = response.json()
        
        print("✅ Response Received")
        print(f"  Status: {response.status_code}")
        print(f"  Actions: {len(data.get('actions', []))}")
        print(f"  Response size: {len(response.text)} bytes")
        print()
        
        # Validate response
        is_valid, errors = validate_response(data)
        
        if is_valid:
            print("✅ Response Validation: PASSED")
            print()
            print("📋 Response Summary:")
            print(f"  Actions count: {len(data.get('actions', []))}")
            print(f"  Has webAgentId: {'webAgentId' in data}")
            print(f"  Has web_agent_id: {'web_agent_id' in data}")
            print(f"  Has recording: {'recording' in data}")
            print()
            print("📋 Action Types:")
            action_types = {}
            for action in data.get('actions', []):
                action_type = action.get('type', 'Unknown')
                action_types[action_type] = action_types.get(action_type, 0) + 1
            for action_type, count in action_types.items():
                print(f"  {action_type}: {count}")
            print()
            print("✅ Response is playground-ready!")
            return True
        else:
            print("❌ Response Validation: FAILED")
            print()
            print("Errors:")
            for error in errors:
                print(f"  - {error}")
            print()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_playground_scenario()
    sys.exit(0 if success else 1)

