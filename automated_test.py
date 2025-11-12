#!/usr/bin/env python3
"""
Automated testing and documentation generator for deployed Autoppia Worker
Run this with your Render URL to test everything and generate documentation
"""

import sys
import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List

def test_endpoint(url: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Test an endpoint and return results"""
    try:
        start_time = time.time()
        if method == "GET":
            response = requests.get(url, timeout=30)
        else:
            response = requests.post(url, json=data, timeout=30, headers={"Content-Type": "application/json"})
        elapsed = time.time() - start_time
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response_time": round(elapsed, 2),
            "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            "error": None
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "status_code": None,
            "response_time": None,
            "data": None,
            "error": "Request timeout (service might be spinning up)"
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": None,
            "response_time": None,
            "data": None,
            "error": str(e)
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 automated_test.py <your-render-url>")
        print("Example: python3 automated_test.py https://autoppia-miner.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    print(f"🧪 Testing Autoppia Worker at: {base_url}")
    print("=" * 60)
    print()
    
    results = {
        "url": base_url,
        "tested_at": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Test 1: Health Check
    print("1️⃣ Testing Health Endpoint...")
    health_result = test_endpoint(f"{base_url}/health")
    results["tests"]["health"] = health_result
    if health_result["success"]:
        print(f"   ✅ Health check passed ({health_result['response_time']}s)")
        print(f"   Status: {health_result['data'].get('status', 'unknown')}")
    else:
        print(f"   ❌ Health check failed: {health_result.get('error', 'Unknown error')}")
    print()
    
    # Test 2: Metadata
    print("2️⃣ Testing Metadata Endpoint...")
    metadata_result = test_endpoint(f"{base_url}/metadata")
    results["tests"]["metadata"] = metadata_result
    if metadata_result["success"]:
        print(f"   ✅ Metadata endpoint working ({metadata_result['response_time']}s)")
        if isinstance(metadata_result["data"], dict):
            print(f"   Worker: {metadata_result['data'].get('name', 'unknown')}")
            print(f"   Version: {metadata_result['data'].get('version', 'unknown')}")
    else:
        print(f"   ❌ Metadata failed: {metadata_result.get('error', 'Unknown error')}")
    print()
    
    # Test 3: Process Task
    print("3️⃣ Testing Process Task...")
    process_result = test_endpoint(
        f"{base_url}/process",
        method="POST",
        data={"task": "process", "input_data": {"data": ["test1", "test2", "test3"]}}
    )
    results["tests"]["process_task"] = process_result
    if process_result["success"]:
        print(f"   ✅ Process task working ({process_result['response_time']}s)")
        if isinstance(process_result["data"], dict) and process_result["data"].get("success"):
            print(f"   Processed: {process_result['data'].get('result', {}).get('processed_count', 0)} items")
    else:
        print(f"   ❌ Process task failed: {process_result.get('error', 'Unknown error')}")
    print()
    
    # Test 4: Mine Task
    print("4️⃣ Testing Mine Task...")
    mine_result = test_endpoint(
        f"{base_url}/process",
        method="POST",
        data={"task": "mine", "input_data": {"source": "test_source", "pattern": "test_pattern"}}
    )
    results["tests"]["mine_task"] = mine_result
    if mine_result["success"]:
        print(f"   ✅ Mine task working ({mine_result['response_time']}s)")
    else:
        print(f"   ❌ Mine task failed: {mine_result.get('error', 'Unknown error')}")
    print()
    
    # Test 5: Generate Task
    print("5️⃣ Testing Generate Task...")
    generate_result = test_endpoint(
        f"{base_url}/process",
        method="POST",
        data={"task": "generate", "input_data": {"prompt": "Hello, world!"}}
    )
    results["tests"]["generate_task"] = generate_result
    if generate_result["success"]:
        print(f"   ✅ Generate task working ({generate_result['response_time']}s)")
    else:
        print(f"   ❌ Generate task failed: {generate_result.get('error', 'Unknown error')}")
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for test in results["tests"].values() if test["success"])
    total = len(results["tests"])
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    print()
    
    # Save results
    results_file = "deployment_test_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Results saved to: {results_file}")
    
    # Generate documentation
    generate_docs(base_url, results)
    
    if passed == total:
        print()
        print("🎉 All tests passed! Your worker is fully operational!")
    else:
        print()
        print("⚠️  Some tests failed. Check the results above.")
        print("   Note: If this is your first request, Render free tier may take ~30s to spin up.")

def generate_docs(base_url: str, results: Dict):
    """Generate usage documentation"""
    docs = f"""# 🚀 Your Deployed Autoppia Worker

## Worker URL
**{base_url}**

## Test Results
Tested at: {results['tested_at']}
Tests Passed: {sum(1 for t in results['tests'].values() if t['success'])}/{len(results['tests'])}

## Quick Start

### Health Check
```bash
curl {base_url}/health
```

### Process Data
```bash
curl -X POST {base_url}/process \\
  -H "Content-Type: application/json" \\
  -d '{{"task": "process", "input_data": {{"data": ["item1", "item2"]}}}}'
```

### Python Example
```python
import requests

response = requests.post(
    "{base_url}/process",
    json={{
        "task": "process",
        "input_data": {{"data": ["test1", "test2"]}}
    }}
)
print(response.json())
```

## Available Endpoints

- `GET /health` - Health check
- `GET /metadata` - Worker metadata
- `POST /process` - Process tasks (mine, process, generate)
- `GET /metrics` - Worker metrics

## Status
✅ Worker is deployed and operational!
"""
    
    with open("DEPLOYED_WORKER_INFO.md", "w") as f:
        f.write(docs)
    print("✅ Documentation generated: DEPLOYED_WORKER_INFO.md")

if __name__ == "__main__":
    main()

