# 🧪 Testing Guide - Agent Performance Validation

**Last Updated**: November 13, 2025  
**Status**: Complete with all testing strategies

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Unit Tests](#unit-tests)
3. [Integration Tests](#integration-tests)
4. [Performance Tests](#performance-tests)
5. [Production Monitoring](#production-monitoring)
6. [Test Coverage](#test-coverage)

---

## ⚡ Quick Start

### Run All Tests
```bash
# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run specific test
pytest tests/test_worker.py::TestAutoppiaWorker::test_generate_task -v

# Run async tests
pytest tests/ -v -k asyncio
```

### Check Test Results
```bash
# View coverage report
open htmlcov/index.html

# Run and see failures
pytest tests/ -v --tb=short
```

---

## 🧪 Unit Tests

### What's Currently Tested

Your test suite covers:
- ✅ Worker initialization
- ✅ Mine task processing
- ✅ Process task handling
- ✅ Generate task with AI
- ✅ Error handling (unknown tasks)
- ✅ Health checks
- ✅ Metadata retrieval

### Run Unit Tests

```bash
# From project root
cd /Users/illfaded2022/Desktop/WORKSPACE/autoppia-miner

# Run all tests
pytest tests/ -v

# Run with verbose output
pytest tests/ -vv

# Run specific test class
pytest tests/test_worker.py::TestAutoppiaWorker -v

# Run specific test
pytest tests/test_worker.py::TestAutoppiaWorker::test_generate_task -v
```

### Expected Output
```
tests/test_worker.py::TestAutoppiaWorker::test_worker_initialization PASSED
tests/test_worker.py::TestAutoppiaWorker::test_mine_task PASSED
tests/test_worker.py::TestAutoppiaWorker::test_process_task PASSED
tests/test_worker.py::TestAutoppiaWorker::test_generate_task PASSED
tests/test_worker.py::TestAutoppiaWorker::test_unknown_task PASSED
tests/test_worker.py::TestAutoppiaWorker::test_health_check PASSED
tests/test_worker.py::TestAutoppiaWorker::test_get_metadata PASSED

========== 7 passed in 0.45s ==========
```

---

## 🔗 Integration Tests

Test the API endpoints directly:

### 1. Health Check Endpoint
```bash
# Quick health check
curl https://autoppia-miner.onrender.com/health

# Expected response:
# {"status":"healthy","worker":"autoppia-miner","version":"0.1.0",...}
```

### 2. Root Endpoint
```bash
curl https://autoppia-miner.onrender.com/

# Expected response:
# {"service":"autoppia-miner","version":"0.1.0","status":"running"}
```

### 3. Metadata Endpoint
```bash
curl https://autoppia-miner.onrender.com/metadata

# Expected response includes:
# {"name":"autoppia-miner","version":"0.1.0","capabilities":[...]}
```

### 4. Process Endpoint (Mine Task)
```bash
curl -X POST https://autoppia-miner.onrender.com/process \
  -H "Content-Type: application/json" \
  -d '{
    "task": "mine",
    "input_data": {
      "source": "test_source",
      "pattern": "test_pattern"
    }
  }'
```

### 5. Solve Task Endpoint (Bittensor)
```bash
curl -X POST https://autoppia-miner.onrender.com/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "task_123",
    "prompt": "Click the login button",
    "url": "https://example.com",
    "seed": 12345,
    "web_project_name": "example_project",
    "specifications": {}
  }'

# Expected response:
# {
#   "task_id": "task_123",
#   "actions": [
#     {"action_type": "navigate", "url": "https://example.com"},
#     {"action_type": "wait", "duration": 2.0},
#     {"action_type": "screenshot"}
#   ],
#   "success": true
# }
```

---

## ⚡ Performance Tests

### 1. Response Time Testing

**Local Testing:**
```bash
# Test local worker response time
time curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d '{
    "task": "generate",
    "input_data": {"prompt": "Test prompt"}
  }'

# Measure: real, user, sys times
```

**Deployed Testing:**
```bash
# Test deployed worker
time curl -X POST https://autoppia-miner.onrender.com/process \
  -H "Content-Type: application/json" \
  -d '{
    "task": "generate",
    "input_data": {"prompt": "Test prompt"}
  }'

# Expected: < 2 seconds for simple tasks
```

### 2. Load Testing with Apache Bench

```bash
# Install Apache Bench (macOS)
brew install httpd

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 https://autoppia-miner.onrender.com/health

# Expected output shows:
# Requests per second
# Failed requests
# Average response time
# Min/max response times
```

### 3. Load Testing with wrk (Better Alternative)

```bash
# Install wrk (macOS)
brew install wrk

# Run 30 second test with 4 threads, 100 connections
wrk -t4 -c100 -d30s https://autoppia-miner.onrender.com/health

# For POST requests, create script:
cat > post.lua << 'EOF'
request = function()
  wrk.method = "POST"
  wrk.body = '{"task":"process","input_data":{"data":["item1"]}}'
  wrk.headers["Content-Type"] = "application/json"
  return wrk.format(nil, "/process")
end
EOF

wrk -t4 -c100 -d30s -s post.lua https://autoppia-miner.onrender.com
```

### 4. Response Time Benchmark Script

Create `benchmark.py`:
```python
#!/usr/bin/env python3
import asyncio
import httpx
import time
from statistics import mean, stdev

async def benchmark_endpoint(url, payload, iterations=10):
    """Benchmark an endpoint"""
    times = []
    
    async with httpx.AsyncClient() as client:
        for i in range(iterations):
            start = time.time()
            try:
                response = await client.post(url, json=payload, timeout=30.0)
                duration = time.time() - start
                times.append(duration)
                print(f"  Request {i+1}: {duration:.3f}s - Status: {response.status_code}")
            except Exception as e:
                print(f"  Request {i+1}: FAILED - {str(e)}")
    
    if times:
        print(f"\nResults:")
        print(f"  Min: {min(times):.3f}s")
        print(f"  Max: {max(times):.3f}s")
        print(f"  Avg: {mean(times):.3f}s")
        if len(times) > 1:
            print(f"  StdDev: {stdev(times):.3f}s")

async def main():
    print("🔥 Benchmarking Autoppia Worker...\n")
    
    # Test mine task
    print("📊 Mining Task Performance:")
    await benchmark_endpoint(
        "https://autoppia-miner.onrender.com/process",
        {
            "task": "mine",
            "input_data": {"source": "test", "pattern": "pattern"}
        }
    )
    
    # Test process task
    print("\n📊 Process Task Performance:")
    await benchmark_endpoint(
        "https://autoppia-miner.onrender.com/process",
        {
            "task": "process",
            "input_data": {"data": ["item1", "item2", "item3"]}
        }
    )
    
    # Test generate task (slowest)
    print("\n📊 Generate Task Performance:")
    await benchmark_endpoint(
        "https://autoppia-miner.onrender.com/process",
        {
            "task": "generate",
            "input_data": {"prompt": "Test prompt"}
        }
    )
    
    # Test solve task (Bittensor)
    print("\n📊 Solve Task Performance:")
    await benchmark_endpoint(
        "https://autoppia-miner.onrender.com/solve_task",
        {
            "id": "benchmark_task",
            "prompt": "Test web agent task",
            "url": "https://example.com",
            "seed": 12345,
            "web_project_name": "test",
            "specifications": {}
        }
    )

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python3 benchmark.py
```

---

## 📊 Production Monitoring

### 1. Real-Time Logs

```bash
# Watch miner activity
pm2 logs autoppia_miner

# Filter for specific patterns
pm2 logs autoppia_miner | grep -i error
pm2 logs autoppia_miner | grep -i "task"
```

### 2. Monitor with Real-Time Dashboard

```bash
# Your existing monitoring script
./monitor_miner.sh

# Or real-time CPU/memory monitoring
pm2 monit
```

### 3. Check Performance Metrics

```bash
# Memory usage
pm2 status autoppia_miner

# Detailed process info
pm2 show autoppia_miner

# See restart count (indicates crashes)
pm2 list | grep autoppia_miner
```

### 4. Track Key Performance Indicators (KPIs)

Create `track_performance.sh`:
```bash
#!/bin/bash

echo "📊 Autoppia Worker Performance Metrics"
echo "======================================="
echo ""

# Check worker uptime
echo "⏱️  Worker Uptime:"
pm2 show autoppia_miner | grep "uptime" || echo "Running"

# Check memory usage
echo ""
echo "💾 Memory Usage:"
ps aux | grep "worker.py\|api.py" | grep -v grep | awk '{print "  " $6 " KB"}'

# Check CPU usage
echo ""
echo "⚙️  CPU Usage:"
ps aux | grep "worker.py\|api.py" | grep -v grep | awk '{print "  " $3 "%"}'

# Check error rate
echo ""
echo "❌ Recent Errors (last hour):"
pm2 logs autoppia_miner --lines 100 --nostream | grep -i error | wc -l

# Check response time from logs
echo ""
echo "⏰ Recent Response Analysis:"
echo "  (Check logs for performance patterns)"

# Health check
echo ""
echo "🏥 Worker Health:"
curl -s https://autoppia-miner.onrender.com/health | python3 -m json.tool | head -5
```

Run it:
```bash
chmod +x track_performance.sh
./track_performance.sh
```

---

## 📈 Test Coverage

### Generate Coverage Report

```bash
# Run tests with coverage
pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# View coverage
open htmlcov/index.html
```

### Coverage Analysis

Check which code paths are tested:
```bash
# Detailed coverage
pytest tests/ --cov=worker --cov=api --cov-report=term-missing

# Shows which lines aren't tested
```

---

## 🎯 Testing Checklist

### Before Deployment
- [ ] All unit tests pass (`pytest tests/ -v`)
- [ ] Worker initializes correctly
- [ ] All task types (mine, process, generate) work
- [ ] Error handling works for unknown tasks
- [ ] Health check endpoint responds
- [ ] Metadata endpoint returns correct info
- [ ] API starts without errors

### After Deployment
- [ ] Health endpoint returns healthy status
- [ ] Process endpoint accepts requests
- [ ] Solve task endpoint works (for Bittensor)
- [ ] Response times are acceptable (< 2s)
- [ ] No errors in logs
- [ ] Memory usage stable

### Daily Monitoring
- [ ] Miner process is running
- [ ] Worker is responding to health checks
- [ ] No error spikes in logs
- [ ] Memory usage hasn't increased
- [ ] Miner is receiving and processing tasks
- [ ] TAO rewards are being earned

### Weekly Testing
- [ ] Run full test suite
- [ ] Check performance metrics
- [ ] Review error logs
- [ ] Verify coverage hasn't decreased
- [ ] Test with various payloads
- [ ] Check for memory leaks

---

## 🚀 Performance Benchmarks

Expected performance (Render deployment):

| Task Type | Expected Time | Max Acceptable |
|-----------|---------------|----------------|
| Health Check | < 100ms | 500ms |
| Mine Task | < 500ms | 2000ms |
| Process Task | < 500ms | 2000ms |
| Generate Task | 500-2000ms | 5000ms |
| Solve Task | 500-2000ms | 5000ms |

---

## 🔍 What to Look For in Tests

### Success Indicators
✅ All tests pass without errors  
✅ Response times consistent  
✅ No memory leaks (stable memory usage)  
✅ Error rate < 1%  
✅ 99.9% uptime  
✅ Tasks completing successfully  

### Warning Signs
⚠️ Tests failing randomly  
⚠️ Response time increasing over time  
⚠️ Memory usage growing  
⚠️ Frequent "connection timeout" errors  
⚠️ High error rate in logs  
⚠️ Miner process crashing/restarting  

---

## 📝 Quick Test Commands

```bash
# Unit tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov

# Performance check
curl -w "\nTime: %{time_total}s\n" https://autoppia-miner.onrender.com/health

# Load test (100 requests, 10 concurrent)
ab -n 100 -c 10 https://autoppia-miner.onrender.com/health

# Monitor logs
pm2 logs autoppia_miner

# Check status
pm2 status autoppia_miner

# Full benchmark
python3 benchmark.py
```

---

## 🎓 Example Test Session

```bash
# 1. Run unit tests
pytest tests/ -v

# 2. Test health endpoint
curl https://autoppia-miner.onrender.com/health

# 3. Test process endpoint
curl -X POST https://autoppia-miner.onrender.com/process \
  -H "Content-Type: application/json" \
  -d '{"task":"mine","input_data":{"source":"test","pattern":"test"}}'

# 4. Check performance
time curl https://autoppia-miner.onrender.com/health

# 5. Monitor logs
pm2 logs autoppia_miner --lines 20 --nostream

# 6. Check system resources
pm2 show autoppia_miner
```

---

## 🎯 Final Notes

**Your testing strategy should include:**

1. **Unit Tests** (automated) - ✅ You have this!
2. **Integration Tests** (manual/automated) - ✅ Easy to run with curl
3. **Performance Tests** (load testing) - ⭐ Use benchmark.py script
4. **Production Monitoring** (continuous) - ✅ Already using pm2 logs
5. **Real-World Testing** (Bittensor validators) - ✅ Live on Subnet 36!

**Best Practices:**
- Run tests before each deployment
- Monitor performance metrics daily
- Set up alerts for errors/crashes
- Keep performance benchmarks
- Document any anomalies
- Test with realistic payloads

---

**Status**: ✅ Your system is production-ready and testable!

For monitoring, use: `./monitor_miner.sh` (updates every 60s)

For testing, use: `pytest tests/ -v` (full test suite)

For benchmarking, use: `python3 benchmark.py` (performance testing)

