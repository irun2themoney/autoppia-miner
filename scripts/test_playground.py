#!/usr/bin/env python3
"""
Automated IWA Playground Test Script

Tests the miner's API endpoint with various scenarios and validates:
1. camelCase compliance (timeSeconds, caseSensitive)
2. IWA action format correctness
3. Response structure
4. Action sequence quality
"""

import requests
import json
import sys
import time
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Configuration
API_ENDPOINT = "http://134.199.203.133:8080/solve_task"
HEALTH_ENDPOINT = "http://134.199.203.133:8080/health"

# Test scenarios
TEST_SCENARIOS = [
    {
        "name": "Simple Navigation",
        "id": "test-nav-1",
        "url": "https://example.com",
        "prompt": "Navigate to example.com and take a screenshot"
    },
    {
        "name": "Click Action",
        "id": "test-click-1",
        "url": "https://example.com",
        "prompt": "Click the 'More information...' link"
    },
    {
        "name": "Form Submission",
        "id": "test-form-1",
        "url": "https://example.com",
        "prompt": "Fill in the form with name 'John Doe' and email 'john@example.com', then submit"
    },
    {
        "name": "Search Task",
        "id": "test-search-1",
        "url": "https://example.com",
        "prompt": "Search for 'test query' in the search box"
    },
    {
        "name": "Wait Action",
        "id": "test-wait-1",
        "url": "https://example.com",
        "prompt": "Wait 2 seconds then take a screenshot"
    },
    {
        "name": "Complex Multi-Step",
        "id": "test-complex-1",
        "url": "https://example.com",
        "prompt": "Navigate to the page, wait for it to load, click a button, fill a form, and submit"
    }
]

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(70)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text: str):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_info(text: str):
    """Print info message"""
    print(f"{BLUE}ℹ️  {text}{RESET}")


def check_health() -> bool:
    """Check if API server is healthy"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"API Health Check: {data.get('status', 'unknown')}")
            return True
        else:
            print_error(f"API Health Check failed: Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"API Health Check failed: {e}")
        return False


def validate_camelcase(response_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate that response uses camelCase (not snake_case)"""
    errors = []
    response_str = json.dumps(response_data)
    
    # Check for snake_case fields that should be camelCase
    snake_case_fields = ["time_seconds", "case_sensitive", "web_agent_id"]
    for field in snake_case_fields:
        if field in response_str:
            # web_agent_id is allowed in response root, but not in actions
            if field == "web_agent_id":
                continue
            errors.append(f"Found snake_case field '{field}' in response (should be camelCase)")
    
    # Check that camelCase fields exist
    camelcase_fields = ["timeSeconds", "caseSensitive"]
    has_camelcase = any(field in response_str for field in camelcase_fields)
    
    if errors:
        return False, errors
    
    return True, []


def validate_iwa_format(actions: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """Validate IWA action format"""
    errors = []
    valid_action_types = ["NavigateAction", "ClickAction", "TypeAction", "WaitAction", "ScreenshotAction"]
    valid_selector_types = ["tagContainsSelector", "attributeValueSelector", "cssSelector", "xpathSelector"]
    
    for i, action in enumerate(actions):
        # Check action type
        action_type = action.get("type")
        if not action_type:
            errors.append(f"Action {i}: Missing 'type' field")
        elif action_type not in valid_action_types:
            errors.append(f"Action {i}: Invalid action type '{action_type}' (must be one of {valid_action_types})")
        
        # Validate WaitAction
        if action_type == "WaitAction":
            if "timeSeconds" not in action:
                errors.append(f"Action {i}: WaitAction missing 'timeSeconds' field")
            elif not isinstance(action["timeSeconds"], (int, float)):
                errors.append(f"Action {i}: WaitAction 'timeSeconds' must be a number")
        
        # Validate NavigateAction
        if action_type == "NavigateAction":
            if "url" not in action:
                errors.append(f"Action {i}: NavigateAction missing 'url' field")
        
        # Validate ClickAction and TypeAction (require selector)
        if action_type in ["ClickAction", "TypeAction"]:
            if "selector" not in action:
                errors.append(f"Action {i}: {action_type} missing 'selector' field")
            elif isinstance(action["selector"], dict):
                selector_type = action["selector"].get("type")
                if selector_type not in valid_selector_types:
                    errors.append(f"Action {i}: Invalid selector type '{selector_type}' (must be one of {valid_selector_types})")
                # Check caseSensitive
                if "caseSensitive" not in action["selector"]:
                    errors.append(f"Action {i}: Selector missing 'caseSensitive' field")
                elif not isinstance(action["selector"]["caseSensitive"], bool):
                    errors.append(f"Action {i}: Selector 'caseSensitive' must be a boolean")
        
        # Validate TypeAction (requires text)
        if action_type == "TypeAction":
            if "text" not in action:
                errors.append(f"Action {i}: TypeAction missing 'text' field")
    
    return len(errors) == 0, errors


def validate_response_structure(response_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate response structure matches IWA format"""
    errors = []
    
    # Check required top-level fields
    required_fields = ["actions", "web_agent_id", "recording"]
    for field in required_fields:
        if field not in response_data:
            errors.append(f"Missing required field '{field}' in response")
    
    # Check actions is a list
    if "actions" in response_data:
        if not isinstance(response_data["actions"], list):
            errors.append("'actions' must be a list")
        elif len(response_data["actions"]) == 0:
            errors.append("'actions' list is empty (must have at least one action)")
    
    return len(errors) == 0, errors


def test_scenario(scenario: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Test a single scenario"""
    print_info(f"Testing: {scenario['name']}")
    print(f"   ID: {scenario['id']}")
    print(f"   URL: {scenario['url']}")
    print(f"   Prompt: {scenario['prompt'][:60]}...")
    
    try:
        # Make request
        start_time = time.time()
        response = requests.post(
            API_ENDPOINT,
            json={
                "id": scenario["id"],
                "url": scenario["url"],
                "prompt": scenario["prompt"]
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response_time = time.time() - start_time
        
        # Check HTTP status
        if response.status_code != 200:
            print_error(f"HTTP {response.status_code}: {response.text[:200]}")
            return False, {"error": f"HTTP {response.status_code}"}
        
        # Parse JSON
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print_error(f"Invalid JSON response: {e}")
            return False, {"error": "Invalid JSON"}
        
        # Validate response structure
        structure_ok, structure_errors = validate_response_structure(data)
        if not structure_ok:
            for error in structure_errors:
                print_error(f"Structure: {error}")
            return False, {"errors": structure_errors}
        
        # Validate camelCase
        camelcase_ok, camelcase_errors = validate_camelcase(data)
        if not camelcase_ok:
            for error in camelcase_errors:
                print_error(f"camelCase: {error}")
            return False, {"errors": camelcase_errors}
        
        # Validate IWA format
        iwa_ok, iwa_errors = validate_iwa_format(data["actions"])
        if not iwa_ok:
            for error in iwa_errors[:5]:  # Limit to first 5 errors
                print_error(f"IWA Format: {error}")
            return False, {"errors": iwa_errors}
        
        # Success metrics
        action_count = len(data["actions"])
        action_types = [a.get("type", "Unknown") for a in data["actions"]]
        
        print_success(f"Response time: {response_time:.2f}s")
        print_success(f"Actions: {action_count} ({', '.join(set(action_types))})")
        print_success(f"camelCase: ✅ Valid")
        print_success(f"IWA Format: ✅ Valid")
        
        return True, {
            "response_time": response_time,
            "action_count": action_count,
            "action_types": action_types,
            "data": data
        }
        
    except requests.exceptions.Timeout:
        print_error("Request timeout (>30s)")
        return False, {"error": "Timeout"}
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False, {"error": str(e)}


def main():
    """Run all tests"""
    print_header("IWA Playground Automated Test Suite")
    
    # Check health
    print_info("Checking API health...")
    if not check_health():
        print_error("API server is not healthy. Exiting.")
        sys.exit(1)
    
    # Run tests
    print_header("Running Test Scenarios")
    
    results = []
    passed = 0
    failed = 0
    
    for scenario in TEST_SCENARIOS:
        success, result = test_scenario(scenario)
        results.append({
            "scenario": scenario["name"],
            "success": success,
            "result": result
        })
        
        if success:
            passed += 1
        else:
            failed += 1
        
        time.sleep(0.5)  # Small delay between requests
    
    # Summary
    print_header("Test Summary")
    
    print(f"{BOLD}Total Tests: {len(TEST_SCENARIOS)}{RESET}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    
    # Calculate average response time
    successful_results = [r for r in results if r["success"]]
    if successful_results:
        avg_time = sum(r["result"].get("response_time", 0) for r in successful_results) / len(successful_results)
        print_info(f"Average Response Time: {avg_time:.2f}s")
        
        # Action count stats
        avg_actions = sum(r["result"].get("action_count", 0) for r in successful_results) / len(successful_results)
        print_info(f"Average Actions per Response: {avg_actions:.1f}")
    
    # Detailed results
    print_header("Detailed Results")
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} - {result['scenario']}")
        if result["success"]:
            print(f"   Response Time: {result['result'].get('response_time', 0):.2f}s")
            print(f"   Actions: {result['result'].get('action_count', 0)}")
        else:
            error = result["result"].get("error", "Unknown error")
            print(f"   Error: {error}")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"playground_test_results_{timestamp}.json"
    
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "total_tests": len(TEST_SCENARIOS),
            "passed": passed,
            "failed": failed,
            "results": results
        }, f, indent=2)
    
    print_info(f"Results saved to: {results_file}")
    
    # Exit code
    if failed > 0:
        print_error("\nSome tests failed. Review the output above.")
        sys.exit(1)
    else:
        print_success("\nAll tests passed! ✅")
        sys.exit(0)


if __name__ == "__main__":
    main()

