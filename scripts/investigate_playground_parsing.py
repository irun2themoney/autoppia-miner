#!/usr/bin/env python3
"""
Investigate Playground Response Parsing Logic

This script simulates how the playground might parse responses and identifies
potential issues that could cause empty actions arrays.
"""

import json
import sys
from typing import Dict, Any, List, Optional

def simulate_pydantic_validation(response_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Simulate strict Pydantic validation that the playground might use.
    
    Based on Bittensor/Autoppia patterns, validators often use strict Pydantic
    models that reject unexpected fields or require exact field names.
    """
    errors = []
    
    # Scenario 1: Strict validation - only allow specific fields
    allowed_fields = {"actions", "web_agent_id", "recording"}
    extra_fields = set(response_data.keys()) - allowed_fields
    
    if extra_fields:
        errors.append(f"Strict validation: Unexpected fields found: {extra_fields}")
        # Some validators reject responses with unexpected fields
        if "webAgentId" in extra_fields:
            errors.append("CRITICAL: 'webAgentId' field is not allowed (only 'web_agent_id' expected)")
    
    # Scenario 2: Check if actions field exists and is valid
    if "actions" not in response_data:
        errors.append("Missing required field: 'actions'")
        return False, errors
    
    actions = response_data.get("actions", [])
    if not isinstance(actions, list):
        errors.append(f"'actions' must be a list, got {type(actions)}")
        return False, errors
    
    if len(actions) == 0:
        errors.append("'actions' array is empty")
        return False, errors
    
    # Scenario 3: Validate action structure
    for i, action in enumerate(actions):
        if not isinstance(action, dict):
            errors.append(f"Action {i} is not a dictionary")
            continue
        
        if "type" not in action:
            errors.append(f"Action {i} missing required field: 'type'")
    
    return len(errors) == 0, errors


def simulate_field_name_conflict(response_data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Simulate what happens when both webAgentId and web_agent_id are present.
    
    Some parsers might:
    1. Use the first field they find
    2. Use the last field they find
    3. Reject the response entirely
    4. Use webAgentId and ignore web_agent_id (causing mismatch)
    """
    has_camel = "webAgentId" in response_data
    has_snake = "web_agent_id" in response_data
    
    if has_camel and has_snake:
        # Check if values match
        camel_val = response_data.get("webAgentId")
        snake_val = response_data.get("web_agent_id")
        
        if camel_val != snake_val:
            return False, f"Field value mismatch: webAgentId='{camel_val}' != web_agent_id='{snake_val}'"
        
        # If values match, parser might still reject due to duplicate fields
        return False, "Both webAgentId and web_agent_id present - parser may reject or use wrong field"
    
    if has_camel and not has_snake:
        return False, "Only webAgentId present - playground expects web_agent_id"
    
    if has_snake and not has_camel:
        return True, "Only web_agent_id present - correct format"
    
    return False, "Neither webAgentId nor web_agent_id present"


def simulate_json_parsing_issues(response_json: str) -> tuple[bool, List[str]]:
    """
    Simulate potential JSON parsing issues that could cause empty actions.
    """
    errors = []
    
    try:
        parsed = json.loads(response_json)
    except json.JSONDecodeError as e:
        errors.append(f"JSON parsing error: {e}")
        return False, errors
    
    # Check for common issues
    if not isinstance(parsed, dict):
        errors.append(f"Root element is not a dictionary: {type(parsed)}")
        return False, errors
    
    # Check if actions field exists
    if "actions" not in parsed:
        errors.append("Missing 'actions' field in parsed JSON")
        return False, errors
    
    # Check if actions is actually empty after parsing
    actions = parsed.get("actions", [])
    if not isinstance(actions, list):
        errors.append(f"'actions' is not a list after parsing: {type(actions)}")
        return False, errors
    
    if len(actions) == 0:
        errors.append("'actions' array is empty after JSON parsing")
        return False, errors
    
    return True, errors


def investigate_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive investigation of response parsing issues.
    """
    results = {
        "response_keys": list(response_data.keys()),
        "has_webAgentId": "webAgentId" in response_data,
        "has_web_agent_id": "web_agent_id" in response_data,
        "actions_count": len(response_data.get("actions", [])),
        "actions_empty": len(response_data.get("actions", [])) == 0,
    }
    
    # Test 1: Pydantic validation
    pydantic_valid, pydantic_errors = simulate_pydantic_validation(response_data)
    results["pydantic_validation"] = {
        "valid": pydantic_valid,
        "errors": pydantic_errors
    }
    
    # Test 2: Field name conflict
    field_conflict_valid, field_conflict_msg = simulate_field_name_conflict(response_data)
    results["field_name_conflict"] = {
        "valid": field_conflict_valid,
        "message": field_conflict_msg
    }
    
    # Test 3: JSON serialization/parsing
    try:
        response_json = json.dumps(response_data)
        json_valid, json_errors = simulate_json_parsing_issues(response_json)
        results["json_parsing"] = {
            "valid": json_valid,
            "errors": json_errors,
            "json_size": len(response_json)
        }
    except Exception as e:
        results["json_parsing"] = {
            "valid": False,
            "errors": [f"JSON serialization error: {e}"]
        }
    
    # Test 4: Check if actions are actually valid
    actions = response_data.get("actions", [])
    if actions:
        first_action = actions[0]
        results["first_action"] = {
            "type": first_action.get("type"),
            "keys": list(first_action.keys()),
            "has_timeSeconds": "timeSeconds" in first_action,
            "has_time_seconds": "time_seconds" in first_action,
            "has_selector": "selector" in first_action,
        }
        if "selector" in first_action:
            selector = first_action["selector"]
            if isinstance(selector, dict):
                results["first_action"]["selector"] = {
                    "keys": list(selector.keys()),
                    "has_caseSensitive": "caseSensitive" in selector,
                    "has_case_sensitive": "case_sensitive" in selector,
                }
    
    return results


def main():
    """Test with actual API response"""
    import requests
    
    API_ENDPOINT = "http://134.199.203.133:8080/solve_task"
    
    payload = {
        "id": "investigation-test",
        "url": "https://autobooks.autoppia.com",
        "prompt": "Register with username testuser and password PASSWORD"
    }
    
    print("🔍 Investigating Playground Response Parsing Logic")
    print("=" * 70)
    print()
    
    try:
        response = requests.post(API_ENDPOINT, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return
        
        response_data = response.json()
        
        print("📋 API Response Summary:")
        print(f"  Status: {response.status_code}")
        print(f"  Response keys: {list(response_data.keys())}")
        print(f"  Actions count: {len(response_data.get('actions', []))}")
        print(f"  Has webAgentId: {'webAgentId' in response_data}")
        print(f"  Has web_agent_id: {'web_agent_id' in response_data}")
        print()
        
        # Investigate
        investigation = investigate_response(response_data)
        
        print("🔬 Investigation Results:")
        print("=" * 70)
        print()
        
        # Pydantic validation
        print("1. Pydantic Validation (Strict):")
        pydantic = investigation["pydantic_validation"]
        if pydantic["valid"]:
            print("   ✅ PASSED - Response would pass strict Pydantic validation")
        else:
            print("   ❌ FAILED - Response would be rejected:")
            for error in pydantic["errors"]:
                print(f"      - {error}")
        print()
        
        # Field name conflict
        print("2. Field Name Conflict:")
        field_conflict = investigation["field_name_conflict"]
        if field_conflict["valid"]:
            print(f"   ✅ PASSED - {field_conflict['message']}")
        else:
            print(f"   ❌ FAILED - {field_conflict['message']}")
        print()
        
        # JSON parsing
        print("3. JSON Parsing:")
        json_parsing = investigation["json_parsing"]
        if json_parsing["valid"]:
            print(f"   ✅ PASSED - JSON parsing successful ({json_parsing.get('json_size', 0)} bytes)")
        else:
            print("   ❌ FAILED - JSON parsing issues:")
            for error in json_parsing.get("errors", []):
                print(f"      - {error}")
        print()
        
        # Actions validation
        print("4. Actions Validation:")
        if investigation["actions_empty"]:
            print("   ❌ FAILED - Actions array is empty")
        else:
            print(f"   ✅ PASSED - {investigation['actions_count']} actions found")
            if "first_action" in investigation:
                fa = investigation["first_action"]
                print(f"      First action type: {fa.get('type')}")
                print(f"      Has timeSeconds: {fa.get('has_timeSeconds')}")
                print(f"      Has time_seconds: {fa.get('has_time_seconds')}")
                if fa.get("has_selector"):
                    sel = fa.get("selector", {})
                    print(f"      Selector has caseSensitive: {sel.get('has_caseSensitive')}")
                    print(f"      Selector has case_sensitive: {sel.get('has_case_sensitive')}")
        print()
        
        # Summary
        print("=" * 70)
        print("📊 Summary:")
        print()
        
        all_passed = (
            pydantic["valid"] and
            field_conflict["valid"] and
            json_parsing["valid"] and
            not investigation["actions_empty"]
        )
        
        if all_passed:
            print("✅ All checks passed - Response should work with playground")
        else:
            print("❌ Some checks failed - Response may be rejected by playground")
            print()
            print("🔧 Recommended Fixes:")
            if not pydantic["valid"]:
                print("   1. Remove 'webAgentId' field - only keep 'web_agent_id'")
            if not field_conflict["valid"]:
                print("   2. Ensure only 'web_agent_id' is present (not 'webAgentId')")
            if investigation["actions_empty"]:
                print("   3. Ensure actions array is never empty")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

