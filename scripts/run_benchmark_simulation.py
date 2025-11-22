#!/usr/bin/env python3
"""
Simulate benchmark tests to verify API is ready
This simulates what the playground benchmark will do
"""
import requests
import json
import time
from typing import Dict, Any, List

API_ENDPOINT = "https://134.199.203.133:8443/solve_task"

# Simulate benchmark test cases (based on actual benchmark format)
BENCHMARK_TESTS = [
    {
        "id": "benchmark-test-1",
        "prompt": "Book a consultation whose name contains 'ah M.' and whose rate does not contain 'iqj' and whose role is not equal to 'Data Scientist' and whose country is not equal to 'Poland' and whose rating equals 4.6",
        "url": ""
    },
    {
        "id": "benchmark-test-2",
        "prompt": "Book a consultation whose country is NOT 'Sweden' and whose role is equal to 'Backend Developer' and whose name is NOT 'Quentin R.' and whose jobs is NOT equal to '76'",
        "url": ""
    },
    {
        "id": "benchmark-test-3",
        "prompt": "Book a consultation",
        "url": ""
    }
]

def test_benchmark_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Test a single benchmark task"""
    start_time = time.time()
    try:
        response = requests.post(
            API_ENDPOINT,
            json=task,
            headers={"Content-Type": "application/json"},
            timeout=90,
            verify=False
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            actions = data.get("actions", [])
            return {
                "success": len(actions) > 0,
                "time": round(elapsed, 3),
                "actions_count": len(actions),
                "status_code": 200,
                "has_actions": len(actions) > 0
            }
        else:
            return {
                "success": False,
                "time": round(elapsed, 3),
                "actions_count": 0,
                "status_code": response.status_code,
                "error": response.text[:200]
            }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "success": False,
            "time": round(elapsed, 3),
            "actions_count": 0,
            "error": str(e)
        }

def main():
    print("🧪 Benchmark Simulation - Testing API Readiness")
    print("=" * 60)
    print(f"\n📋 Testing {len(BENCHMARK_TESTS)} benchmark scenarios")
    print(f"🎯 API Endpoint: {API_ENDPOINT}")
    print()
    
    results = []
    for i, task in enumerate(BENCHMARK_TESTS, 1):
        print(f"Test {i}/{len(BENCHMARK_TESTS)}: {task['prompt'][:60]}...")
        result = test_benchmark_task(task)
        result["task_id"] = task["id"]
        result["prompt"] = task["prompt"]
        results.append(result)
        
        if result["success"]:
            print(f"   ✅ SUCCESS - {result['actions_count']} actions in {result['time']}s")
        else:
            print(f"   ❌ FAILED - {result.get('error', 'No actions')}")
        print()
    
    # Summary
    print("=" * 60)
    print("📊 Benchmark Simulation Results")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r["success"])
    total_tests = len(results)
    success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
    avg_time = sum(r["time"] for r in results) / total_tests if total_tests > 0 else 0
    
    print(f"\n✅ Success Rate: {success_count}/{total_tests} ({success_rate:.1f}%)")
    print(f"⏱️  Average Time: {avg_time:.3f}s")
    print(f"📋 Total Actions Generated: {sum(r['actions_count'] for r in results)}")
    
    print("\n📋 Detailed Results:")
    for i, result in enumerate(results, 1):
        status = "✅" if result["success"] else "❌"
        print(f"   {status} Test {i}: {result['actions_count']} actions, {result['time']}s")
    
    print("\n" + "=" * 60)
    if success_rate >= 50:
        print("✅ API IS READY FOR BENCHMARK!")
        print("   Your API should pass benchmark tests on the playground.")
    else:
        print("⚠️  API may need more fixes")
        print("   Some tests failed - check errors above")
    
    print("\n🎯 Next Steps:")
    print("   1. Go to: https://infinitewebarena.autoppia.com/playground")
    print("   2. Configure benchmark:")
    print("      - Projects: Autoppia Work")
    print("      - Use Cases: BOOK_A_CONSULTATION")
    print("      - Runs: 5-10")
    print("      - Endpoint: 134.199.203.133:8443")
    print("   3. Click 'Run Benchmark'")
    print("   4. Monitor dashboard: http://134.199.203.133:8080/dashboard")
    print()

if __name__ == "__main__":
    main()

