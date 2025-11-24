#!/usr/bin/env python3
"""
Comprehensive end-to-end test script for the miner
Tests everything from startup to validator responses
"""
import sys
import os
import asyncio
import time
import json
import subprocess
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestRunner:
    """Comprehensive test runner"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name: str, func):
        """Run a test"""
        print(f"\n{Colors.BLUE}🔍 TEST: {name}{Colors.RESET}")
        try:
            result = func()
            if result:
                print(f"{Colors.GREEN}✅ PASSED: {name}{Colors.RESET}")
                self.passed += 1
                return True
            else:
                print(f"{Colors.RED}❌ FAILED: {name}{Colors.RESET}")
                self.failed += 1
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ FAILED: {name} - {e}{Colors.RESET}")
            import traceback
            traceback.print_exc()
            self.failed += 1
            return False
    
    async def async_test(self, name: str, func):
        """Run an async test"""
        print(f"\n{Colors.BLUE}🔍 TEST: {name}{Colors.RESET}")
        try:
            result = await func()
            if result:
                print(f"{Colors.GREEN}✅ PASSED: {name}{Colors.RESET}")
                self.passed += 1
                return True
            else:
                print(f"{Colors.RED}❌ FAILED: {name}{Colors.RESET}")
                self.failed += 1
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ FAILED: {name} - {e}{Colors.RESET}")
            import traceback
            traceback.print_exc()
            self.failed += 1
            return False
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}📊 TEST SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}❌ Failed: {self.failed}{Colors.RESET}")
        total = self.passed + self.failed
        if total > 0:
            success_rate = (self.passed / total) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  SOME TESTS FAILED{Colors.RESET}")


async def main():
    """Run all tests"""
    runner = TestRunner()
    
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}🧪 COMPREHENSIVE MINER TEST SUITE{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")
    
    # Test 1: Environment
    runner.test("Python version", lambda: sys.version_info >= (3, 10))
    
    # Test 2: Imports
    def test_imports():
        from config.settings import settings
        from api.server import app
        from api.actions.generator import ActionGenerator
        from api.utils.action_optimizer import ActionOptimizer
        from api.utils.response_quality import ResponseQualityEnhancer
        from miner.protocol import StartRoundSynapse, TaskSynapse
        return True
    
    runner.test("Import all modules", test_imports)
    
    # Test 3: API Server
    from fastapi.testclient import TestClient
    from api.server import app
    
    client = TestClient(app)
    runner.test("API server starts", lambda: client.get("/health").status_code == 200)
    runner.test("Health endpoint", lambda: client.get("/health").json()["status"] == "healthy")
    
    # Test 4: API Endpoints
    test_request = {
        "id": "test-001",
        "prompt": "Navigate to example.com",
        "url": "https://example.com"
    }
    
    def test_solve_task():
        response = client.post("/solve_task", json=test_request)
        if response.status_code != 200:
            return False
        data = response.json()
        return "actions" in data and len(data["actions"]) > 0
    
    runner.test("Solve task endpoint", test_solve_task)
    
    # Test 5: Action Generation
    async def test_action_generation():
        from api.actions.generator import ActionGenerator
        generator = ActionGenerator()
        actions = await generator.generate("Navigate to example.com", "https://example.com", "test-001")
        return actions is not None and len(actions) > 0
    
    await runner.async_test("Action generation", test_action_generation)
    
    # Test 6: Performance Optimizations
    from api.utils.action_optimizer import ActionOptimizer
    from api.utils.response_quality import ResponseQualityEnhancer
    
    def test_optimizer():
        optimizer = ActionOptimizer()
        actions = [
            {"type": "WaitAction", "time_seconds": 1.0},
            {"type": "WaitAction", "time_seconds": 0.5}
        ]
        optimized = optimizer.optimize_action_sequence(actions)
        return len(optimized) <= len(actions)
    
    def test_quality():
        enhancer = ResponseQualityEnhancer()
        actions = [{"type": "NavigateAction", "url": "https://example.com"}]
        score = enhancer.calculate_quality_score(actions)
        return 0.0 <= score <= 1.0
    
    runner.test("Action optimizer", test_optimizer)
    runner.test("Quality enhancer", test_quality)
    
    # Test 7: Validator Synapses
    def test_synapses():
        from miner.protocol import StartRoundSynapse, TaskSynapse
        
        start_round = StartRoundSynapse(round_id="test", task_type="test")
        assert start_round.round_id == "test"
        
        task = TaskSynapse()
        task.prompt = "test"
        assert task.prompt == "test"
        
        return True
    
    runner.test("Validator synapses", test_synapses)
    
    # Test 8: IWA Format
    def test_iwa_format():
        response = client.post("/solve_task", json=test_request)
        data = response.json()
        
        if "actions" not in data or len(data["actions"]) == 0:
            return False
        
        for action in data["actions"]:
            if "type" not in action:
                return False
            if action["type"] not in ["NavigateAction", "ClickAction", "TypeAction", "WaitAction", "ScreenshotAction", "ScrollAction"]:
                return False
        
        return True
    
    runner.test("IWA format compliance", test_iwa_format)
    
    # Test 9: Error Handling
    def test_error_handling():
        # Invalid request
        invalid = {"id": "test"}
        response = client.post("/solve_task", json=invalid)
        if response.status_code != 200:
            return False
        
        data = response.json()
        if "actions" not in data or len(data["actions"]) == 0:
            return False
        
        return True
    
    runner.test("Error handling", test_error_handling)
    
    # Test 10: Full Flow
    async def test_full_flow():
        response = client.post("/solve_task", json={
            "id": "full-flow-test",
            "prompt": "Navigate to https://example.com and take a screenshot",
            "url": "https://example.com"
        })
        
        if response.status_code != 200:
            return False
        
        data = response.json()
        if "actions" not in data or len(data["actions"]) == 0:
            return False
        
        # Check quality
        enhancer = ResponseQualityEnhancer()
        score = enhancer.calculate_quality_score(data["actions"])
        if score < 0.5:
            return False
        
        return True
    
    await runner.async_test("Full request flow", test_full_flow)
    
    # Print summary
    runner.print_summary()
    
    return runner.failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

