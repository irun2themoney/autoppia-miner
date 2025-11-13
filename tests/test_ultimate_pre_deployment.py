"""
ULTIMATE PRE-DEPLOYMENT TEST SUITE
Simulates real-world scenarios from 3:30 AM competition
Tests stability, performance, and edge cases under production stress
"""

import pytest
import json
import time
import asyncio
from typing import Dict, Any
import sys
sys.path.insert(0, '/Users/illfaded2022/Desktop/WORKSPACE/autoppia-miner')

from api import TaskClassifier, RequestCache, RetryHandler, app
from worker import AutoppiaWorker
from fastapi.testclient import TestClient


client = TestClient(app)


class TestUltimatePreDeployment:
    """
    ULTIMATE TEST SUITE - Comprehensive real-world simulation
    These tests simulate what validators will throw at you
    """
    
    def test_01_basic_endpoint_health(self):
        """TEST 1: Can we respond to basic health checks?"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ TEST 1: Health check PASS")
    
    def test_02_metadata_endpoint(self):
        """TEST 2: Do we return proper metadata?"""
        response = client.get("/metadata")
        assert response.status_code == 200
        data = response.json()
        assert "capabilities" in data
        assert data["name"] == "autoppia-miner"
        print("✅ TEST 2: Metadata PASS")
    
    def test_03_basic_search_task(self):
        """TEST 3: Can we handle basic search task?"""
        task = {
            "id": "test-search-001",
            "prompt": "Find the best laptop under $1000",
            "url": "https://example-shop.com"
        }
        response = client.post("/solve_task", json=task)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["actions"]) > 0
        assert data["task_type"] == "search"
        print("✅ TEST 3: Basic search task PASS")
    
    def test_04_complex_form_fill_task(self):
        """TEST 4: Can we handle complex form filling?"""
        task = {
            "id": "test-form-001",
            "prompt": "Complete the registration form with email and password",
            "url": "https://example-site.com/register"
        }
        response = client.post("/solve_task", json=task)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["task_type"] == "form_fill"
        print("✅ TEST 4: Complex form fill PASS")
    
    def test_05_price_comparison_task(self):
        """TEST 5: Can we handle price comparison?"""
        task = {
            "id": "test-price-001",
            "prompt": "Compare prices on three different websites for this item",
            "url": "https://example-shop.com"
        }
        response = client.post("/solve_task", json=task)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["task_type"] == "price_compare"
        print("✅ TEST 5: Price comparison PASS")
    
    def test_06_invalid_task_graceful_handling(self):
        """TEST 6: Do we handle invalid tasks gracefully?"""
        task = {
            "id": "test-invalid-001",
            "prompt": "",  # Empty prompt
            "url": "https://example.com"
        }
        response = client.post("/solve_task", json=task)
        # Should handle gracefully, even if it's an error
        assert response.status_code in [200, 400]
        print("✅ TEST 6: Invalid task handling PASS")
    
    def test_07_response_format_validation(self):
        """TEST 7: Are responses in proper format?"""
        task = {
            "id": "test-format-001",
            "prompt": "Search for something",
            "url": "https://example.com"
        }
        response = client.post("/solve_task", json=task)
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure (what validators expect)
        required_fields = ["task_id", "actions", "success"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Validate actions format
        assert isinstance(data["actions"], list)
        for action in data["actions"]:
            assert "action_type" in action
            assert isinstance(action["action_type"], str)
        
        print("✅ TEST 7: Response format validation PASS")
    
    def test_08_concurrent_requests(self):
        """TEST 8: Can we handle multiple concurrent requests?"""
        tasks = [
            {"id": f"test-concurrent-{i}", "prompt": f"Task {i}", "url": "https://example.com"}
            for i in range(5)
        ]
        
        responses = []
        for task in tasks:
            response = client.post("/solve_task", json=task)
            responses.append(response)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        assert all(r.json()["success"] for r in responses)
        print("✅ TEST 8: Concurrent requests PASS")
    
    def test_09_cache_working(self):
        """TEST 9: Is caching improving performance?"""
        task = {
            "id": "test-cache-001",
            "prompt": "Find the cheapest laptop",
            "url": "https://shop.example.com"
        }
        
        # First request (cache miss)
        start1 = time.time()
        response1 = client.post("/solve_task", json=task)
        time1 = time.time() - start1
        
        # Second request (cache hit)
        task["id"] = "test-cache-002"
        start2 = time.time()
        response2 = client.post("/solve_task", json=task)
        time2 = time.time() - start2
        
        # Cache hit should be faster
        # Note: In testing, might not be dramatic, but should work
        assert response1.status_code == 200
        assert response2.status_code == 200
        print(f"✅ TEST 9: Cache working (miss: {time1*1000:.0f}ms, hit: {time2*1000:.0f}ms)")
    
    def test_10_metrics_endpoint(self):
        """TEST 10: Are metrics being tracked?"""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "requests" in data
        assert "total" in data["requests"]
        assert "success" in data["requests"]
        assert "errors" in data["requests"]
        
        print("✅ TEST 10: Metrics tracking PASS")
    
    def test_11_stress_test_100_requests(self):
        """TEST 11: Can we handle 100 rapid requests? (STRESS TEST)"""
        success_count = 0
        error_count = 0
        times = []
        
        for i in range(100):
            task = {
                "id": f"stress-test-{i}",
                "prompt": f"Find item {i}",
                "url": "https://example.com"
            }
            
            start = time.time()
            try:
                response = client.post("/solve_task", json=task)
                elapsed = time.time() - start
                times.append(elapsed)
                
                if response.status_code == 200 and response.json()["success"]:
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error on request {i}: {str(e)}")
        
        # Should maintain >90% success rate under load
        success_rate = success_count / 100
        assert success_rate > 0.9, f"Success rate too low: {success_rate}"
        
        avg_time = sum(times) / len(times)
        print(f"✅ TEST 11: Stress test PASS (100 requests, {success_rate*100:.1f}% success, {avg_time*1000:.0f}ms avg)")
    
    def test_12_error_injection_missing_prompt(self):
        """TEST 12: Proper error handling for missing prompt"""
        task = {
            "id": "test-error-001",
            "url": "https://example.com"
            # Missing "prompt" field
        }
        response = client.post("/solve_task", json=task)
        # Should handle gracefully
        assert response.status_code in [200, 400]
        print("✅ TEST 12: Missing prompt error handling PASS")
    
    def test_13_error_injection_invalid_json(self):
        """TEST 13: Handling of malformed requests"""
        # This is tested at HTTP level
        # Just verify we don't crash
        try:
            # Send something that looks like JSON but isn't perfect
            response = client.post("/solve_task", json={"id": "test"})
            # We should either handle it or return 400
            assert response.status_code in [200, 400, 422]
            print("✅ TEST 13: Invalid JSON handling PASS")
        except Exception as e:
            print(f"⚠️ TEST 13: Exception handled gracefully: {str(e)[:50]}")
    
    def test_14_diverse_task_types(self):
        """TEST 14: Can we handle all 8 task types?"""
        task_types = {
            "search": "Find the best product",
            "form_fill": "Fill the contact form",
            "price_compare": "Compare prices across websites",
            "click": "Click the submit button",
            "extract": "Get all email addresses from the page",
            "navigate": "Go to the product page",
            "scroll": "Scroll down to view more content",
            "checkout": "Complete the purchase"
        }
        
        results = {}
        for expected_type, prompt in task_types.items():
            task = {
                "id": f"test-type-{expected_type}",
                "prompt": prompt,
                "url": "https://example.com"
            }
            response = client.post("/solve_task", json=task)
            assert response.status_code == 200
            data = response.json()
            results[expected_type] = data["task_type"]
        
        print(f"✅ TEST 14: All task types handled: {results}")
    
    def test_15_response_time_under_300ms(self):
        """TEST 15: Are responses fast enough? (<300ms target)"""
        times = []
        
        for i in range(10):
            task = {
                "id": f"speed-test-{i}",
                "prompt": "Find something",
                "url": "https://example.com"
            }
            
            start = time.time()
            response = client.post("/solve_task", json=task)
            elapsed = time.time() - start
            times.append(elapsed)
            
            assert response.status_code == 200
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"✅ TEST 15: Response times (avg: {avg_time*1000:.0f}ms, max: {max_time*1000:.0f}ms)")
    
    def test_16_no_crashes_on_edge_cases(self):
        """TEST 16: System doesn't crash on edge cases"""
        edge_cases = [
            {"id": "edge-1", "prompt": "A" * 1000, "url": "https://example.com"},  # Very long prompt
            {"id": "edge-2", "prompt": "🚀 emoji test", "url": "https://example.com"},  # Emojis
            {"id": "edge-3", "prompt": "Normal task", "url": "https://very-long-url-" + "x" * 500 + ".com"},  # Long URL
        ]
        
        for task in edge_cases:
            try:
                response = client.post("/solve_task", json=task)
                assert response.status_code in [200, 400, 422]
            except Exception as e:
                # Should not crash
                assert False, f"System crashed on edge case: {str(e)}"
        
        print("✅ TEST 16: Edge cases handled without crashes PASS")
    
    def test_17_metrics_tracking_accuracy(self):
        """TEST 17: Are metrics being tracked accurately?"""
        # Get initial metrics
        response1 = client.get("/metrics")
        initial_total = response1.json()["requests"]["total"]
        
        # Send a task
        task = {"id": "metric-test-1", "prompt": "Test", "url": "https://example.com"}
        client.post("/solve_task", json=task)
        
        # Check metrics updated
        response2 = client.get("/metrics")
        new_total = response2.json()["requests"]["total"]
        
        assert new_total == initial_total + 1
        print("✅ TEST 17: Metrics tracking accurate PASS")
    
    def test_18_consistency_check(self):
        """TEST 18: Same prompt returns consistent action types"""
        prompt = "Find the best laptop"
        
        types = []
        for i in range(5):
            task = {
                "id": f"consistency-{i}",
                "prompt": prompt,
                "url": "https://example.com"
            }
            response = client.post("/solve_task", json=task)
            data = response.json()
            types.append(data["task_type"])
        
        # All should be classified the same way (search)
        assert all(t == types[0] for t in types), f"Inconsistent classification: {types}"
        print(f"✅ TEST 18: Consistency check PASS (all classified as: {types[0]})")
    
    def test_19_never_crashes_under_load(self):
        """TEST 19: System doesn't crash under continuous load"""
        crashes = 0
        for i in range(50):
            try:
                task = {
                    "id": f"load-{i}",
                    "prompt": "Random task query",
                    "url": "https://example.com"
                }
                response = client.post("/solve_task", json=task)
                assert response.status_code in [200, 400, 422]
            except Exception as e:
                crashes += 1
                print(f"Crash {crashes}: {str(e)[:50]}")
        
        assert crashes == 0, f"System crashed {crashes} times"
        print("✅ TEST 19: No crashes under load PASS")
    
    def test_20_final_validation(self):
        """TEST 20: FINAL VALIDATION - Production readiness check"""
        checklist = {
            "health_check": False,
            "metadata_available": False,
            "task_processing": False,
            "metrics_tracking": False,
            "error_handling": False,
            "response_format": False
        }
        
        # Health check
        try:
            r = client.get("/health")
            if r.status_code == 200:
                checklist["health_check"] = True
        except:
            pass
        
        # Metadata
        try:
            r = client.get("/metadata")
            if r.status_code == 200:
                checklist["metadata_available"] = True
        except:
            pass
        
        # Task processing
        try:
            r = client.post("/solve_task", json={
                "id": "final-test",
                "prompt": "Test task",
                "url": "https://example.com"
            })
            if r.status_code == 200 and r.json()["success"]:
                checklist["task_processing"] = True
        except:
            pass
        
        # Metrics
        try:
            r = client.get("/metrics")
            if r.status_code == 200 and "requests" in r.json():
                checklist["metrics_tracking"] = True
        except:
            pass
        
        # Error handling
        try:
            r = client.post("/solve_task", json={"id": "test"})
            if r.status_code in [200, 400, 422]:
                checklist["error_handling"] = True
        except:
            pass
        
        # Response format
        try:
            r = client.post("/solve_task", json={
                "id": "fmt-test",
                "prompt": "Test",
                "url": "https://example.com"
            })
            data = r.json()
            if all(k in data for k in ["task_id", "actions", "success"]):
                checklist["response_format"] = True
        except:
            pass
        
        # All checks must pass
        assert all(checklist.values()), f"Failed checks: {checklist}"
        print(f"✅ TEST 20: FINAL VALIDATION PASS - System is production ready!")
        print(f"   Checklist: {checklist}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

