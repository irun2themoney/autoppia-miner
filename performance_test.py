#!/usr/bin/env python3
"""
Performance testing script for Autoppia Worker
Tests response times, throughput, and concurrent request handling
"""

import sys
import time
import requests
import concurrent.futures
from statistics import mean, median, stdev
from datetime import datetime
from typing import List, Dict, Any
import json

class PerformanceTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.results = {
            "url": base_url,
            "tested_at": datetime.now().isoformat(),
            "tests": {}
        }
    
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, iterations: int = 10) -> Dict[str, Any]:
        """Test an endpoint multiple times and collect metrics"""
        print(f"📊 Testing {endpoint} ({iterations} requests)...")
        
        times = []
        successes = 0
        errors = []
        
        for i in range(iterations):
            try:
                start = time.time()
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
                else:
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data,
                        timeout=30,
                        headers={"Content-Type": "application/json"}
                    )
                elapsed = time.time() - start
                
                if response.status_code == 200:
                    times.append(elapsed)
                    successes += 1
                else:
                    errors.append(f"HTTP {response.status_code}")
                    
            except requests.exceptions.Timeout:
                errors.append("Timeout")
            except Exception as e:
                errors.append(str(e))
        
        if times:
            return {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "successes": successes,
                "failures": len(errors),
                "success_rate": f"{(successes/iterations*100):.1f}%",
                "response_times": {
                    "min": round(min(times), 3),
                    "max": round(max(times), 3),
                    "mean": round(mean(times), 3),
                    "median": round(median(times), 3),
                    "stdev": round(stdev(times), 3) if len(times) > 1 else 0
                },
                "errors": errors[:5] if errors else None
            }
        else:
            return {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "successes": 0,
                "failures": iterations,
                "success_rate": "0%",
                "response_times": None,
                "errors": errors[:5]
            }
    
    def test_concurrent(self, endpoint: str, method: str = "GET", data: Dict = None, 
                       concurrent_requests: int = 5, total_requests: int = 20) -> Dict[str, Any]:
        """Test concurrent request handling"""
        print(f"⚡ Testing concurrent requests ({concurrent_requests} concurrent, {total_requests} total)...")
        
        times = []
        successes = 0
        errors = []
        
        def make_request():
            try:
                start = time.time()
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
                else:
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data,
                        timeout=30,
                        headers={"Content-Type": "application/json"}
                    )
                elapsed = time.time() - start
                
                if response.status_code == 200:
                    return {"success": True, "time": elapsed}
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        start_total = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(total_requests)]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result["success"]:
                    times.append(result["time"])
                    successes += 1
                else:
                    errors.append(result.get("error", "Unknown"))
        total_time = time.time() - start_total
        
        if times:
            return {
                "concurrent_requests": concurrent_requests,
                "total_requests": total_requests,
                "successes": successes,
                "failures": len(errors),
                "success_rate": f"{(successes/total_requests*100):.1f}%",
                "total_time": round(total_time, 2),
                "requests_per_second": round(total_requests / total_time, 2),
                "response_times": {
                    "min": round(min(times), 3),
                    "max": round(max(times), 3),
                    "mean": round(mean(times), 3),
                    "median": round(median(times), 3)
                },
                "errors": errors[:5] if errors else None
            }
        else:
            return {
                "concurrent_requests": concurrent_requests,
                "total_requests": total_requests,
                "successes": 0,
                "failures": total_requests,
                "success_rate": "0%",
                "errors": errors[:5]
            }
    
    def run_all_tests(self):
        """Run comprehensive performance tests"""
        print("🚀 Starting Performance Tests")
        print("=" * 60)
        print()
        
        # Test 1: Health endpoint (baseline)
        self.results["tests"]["health"] = self.test_endpoint("/health", iterations=10)
        self.print_results(self.results["tests"]["health"])
        print()
        
        # Test 2: Metadata endpoint
        self.results["tests"]["metadata"] = self.test_endpoint("/metadata", iterations=10)
        self.print_results(self.results["tests"]["metadata"])
        print()
        
        # Test 3: Process task
        self.results["tests"]["process_task"] = self.test_endpoint(
            "/process",
            method="POST",
            data={"task": "process", "input_data": {"data": ["test1", "test2", "test3"]}},
            iterations=10
        )
        self.print_results(self.results["tests"]["process_task"])
        print()
        
        # Test 4: Concurrent requests (health)
        self.results["tests"]["concurrent_health"] = self.test_concurrent(
            "/health",
            concurrent_requests=5,
            total_requests=20
        )
        self.print_concurrent_results(self.results["tests"]["concurrent_health"])
        print()
        
        # Test 5: Concurrent requests (process)
        self.results["tests"]["concurrent_process"] = self.test_concurrent(
            "/process",
            method="POST",
            data={"task": "process", "input_data": {"data": ["test"]}},
            concurrent_requests=3,
            total_requests=15
        )
        self.print_concurrent_results(self.results["tests"]["concurrent_process"])
        print()
        
        # Save results
        results_file = "performance_test_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"✅ Results saved to: {results_file}")
        
        # Generate summary
        self.print_summary()
    
    def print_results(self, result: Dict):
        """Print test results"""
        if result["response_times"]:
            rt = result["response_times"]
            print(f"   ✅ Success Rate: {result['success_rate']}")
            print(f"   ⏱️  Response Times:")
            print(f"      Min: {rt['min']}s")
            print(f"      Max: {rt['max']}s")
            print(f"      Mean: {rt['mean']}s")
            print(f"      Median: {rt['median']}s")
            if rt['stdev'] > 0:
                print(f"      Std Dev: {rt['stdev']}s")
        else:
            print(f"   ❌ All requests failed")
            if result.get("errors"):
                print(f"   Errors: {', '.join(result['errors'][:3])}")
    
    def print_concurrent_results(self, result: Dict):
        """Print concurrent test results"""
        if result.get("response_times"):
            rt = result["response_times"]
            print(f"   ✅ Success Rate: {result['success_rate']}")
            print(f"   📈 Throughput: {result['requests_per_second']} req/s")
            print(f"   ⏱️  Response Times:")
            print(f"      Min: {rt['min']}s")
            print(f"      Max: {rt['max']}s")
            print(f"      Mean: {rt['mean']}s")
            print(f"      Median: {rt['median']}s")
        else:
            print(f"   ❌ All requests failed")
    
    def print_summary(self):
        """Print performance summary"""
        print("=" * 60)
        print("📊 Performance Summary")
        print("=" * 60)
        
        if "health" in self.results["tests"]:
            health = self.results["tests"]["health"]
            if health.get("response_times"):
                print(f"\n🏥 Health Endpoint:")
                print(f"   Average Response: {health['response_times']['mean']}s")
                print(f"   Success Rate: {health['success_rate']}")
        
        if "process_task" in self.results["tests"]:
            process = self.results["tests"]["process_task"]
            if process.get("response_times"):
                print(f"\n⚙️  Process Task:")
                print(f"   Average Response: {process['response_times']['mean']}s")
                print(f"   Success Rate: {process['success_rate']}")
        
        if "concurrent_health" in self.results["tests"]:
            concurrent = self.results["tests"]["concurrent_health"]
            if concurrent.get("requests_per_second"):
                print(f"\n⚡ Concurrent Performance:")
                print(f"   Throughput: {concurrent['requests_per_second']} req/s")
                print(f"   Success Rate: {concurrent['success_rate']}")
        
        print("\n" + "=" * 60)
        print("✅ Performance testing complete!")
        print("=" * 60)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 performance_test.py <your-render-url>")
        print("Example: python3 performance_test.py https://autoppia-miner.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1]
    tester = PerformanceTester(base_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main()

