"""Official testing procedures based on Autoppia IWA standards"""
import requests
import json
from typing import Dict, Any


def test_health_endpoint(base_url: str = "http://localhost:8080"):
    """Test health endpoint"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ Health endpoint: PASS")
        return True
    except Exception as e:
        print(f"❌ Health endpoint: FAIL - {e}")
        return False


def test_solve_task_endpoint(base_url: str = "http://localhost:8080"):
    """Test solve_task endpoint with official format"""
    try:
        # Official task format (from task.clean_task())
        task = {
            "id": "test-task-001",
            "prompt": "Click the login button",
            "url": "https://example.com"
        }
        
        response = requests.post(
            f"{base_url}/solve_task",
            json=task,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response format (official IWA format)
        assert "actions" in data
        assert "web_agent_id" in data
        assert isinstance(data["actions"], list)
        
        # Verify actions are in IWA BaseAction format
        if data["actions"]:
            action = data["actions"][0]
            assert "type" in action
            assert action["type"] in [
                "NavigateAction", "ClickAction", "TypeAction",
                "WaitAction", "ScreenshotAction", "ScrollAction"
            ]
        
        print("✅ solve_task endpoint: PASS")
        print(f"   Generated {len(data['actions'])} actions")
        return True
    except Exception as e:
        print(f"❌ solve_task endpoint: FAIL - {e}")
        return False


def test_cors_headers(base_url: str = "http://localhost:8080"):
    """Test CORS headers (required for playground)"""
    try:
        response = requests.options(
            f"{base_url}/solve_task",
            headers={
                "Origin": "https://infinitewebarena.autoppia.com",
                "Access-Control-Request-Method": "POST"
            },
            timeout=5
        )
        
        assert response.status_code == 200
        headers = response.headers
        
        # Check CORS headers
        assert "Access-Control-Allow-Origin" in headers
        assert "Access-Control-Allow-Methods" in headers
        
        print("✅ CORS headers: PASS")
        return True
    except Exception as e:
        print(f"❌ CORS headers: FAIL - {e}")
        return False


def test_response_time(base_url: str = "http://localhost:8080"):
    """Test response time (should be < 2s for good performance)"""
    try:
        task = {
            "id": "test-speed",
            "prompt": "Navigate to example.com",
            "url": "https://example.com"
        }
        
        import time
        start = time.time()
        response = requests.post(
            f"{base_url}/solve_task",
            json=task,
            timeout=30
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"Response time {elapsed:.2f}s is too slow"
        
        print(f"✅ Response time: PASS ({elapsed:.2f}s)")
        return True
    except Exception as e:
        print(f"❌ Response time: FAIL - {e}")
        return False


def test_action_format(base_url: str = "http://localhost:8080"):
    """Test action format compliance with IWA BaseAction"""
    try:
        task = {
            "id": "test-format",
            "prompt": "Login with username:test and password:test123",
            "url": "https://example.com"
        }
        
        response = requests.post(
            f"{base_url}/solve_task",
            json=task,
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        actions = data.get("actions", [])
        
        # Verify each action has required fields
        for action in actions:
            action_type = action.get("type")
            assert action_type, "Action missing 'type' field"
            
            # Type-specific validations
            if action_type == "NavigateAction":
                assert "url" in action, "NavigateAction missing 'url'"
            elif action_type == "ClickAction":
                assert "selector" in action, "ClickAction missing 'selector'"
            elif action_type == "TypeAction":
                assert "selector" in action, "TypeAction missing 'selector'"
                assert "text" in action, "TypeAction missing 'text'"
            elif action_type == "WaitAction":
                assert "time_seconds" in action, "WaitAction missing 'time_seconds'"
        
        print("✅ Action format: PASS")
        return True
    except Exception as e:
        print(f"❌ Action format: FAIL - {e}")
        return False


def run_official_tests(base_url: str = "http://localhost:8080"):
    """Run all official tests"""
    print("=" * 60)
    print("OFFICIAL IWA MINER TESTING")
    print("=" * 60)
    print()
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("CORS Headers", test_cors_headers),
        ("solve_task Endpoint", test_solve_task_endpoint),
        ("Response Time", test_response_time),
        ("Action Format", test_action_format),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Testing: {name}...")
        result = test_func(base_url)
        results.append((name, result))
        print()
    
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Miner is ready for deployment!")
    else:
        print("⚠️  Some tests failed - Review and fix before deployment")
    
    return passed == total


if __name__ == "__main__":
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    print(f"Testing miner at: {base_url}")
    print()
    
    success = run_official_tests(base_url)
    sys.exit(0 if success else 1)

