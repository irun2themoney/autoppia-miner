# Official Testing Guide - Pre-Deployment Validation

**Based on Official Autoppia IWA Documentation and Standards**

## 🎯 Official Testing Methods

### 1. IWA Playground (Official Testing Tool)

**URL**: https://infinitewebarena.autoppia.com/playground

**Purpose**: Official testing tool provided by Autoppia to test your miner before deployment

**How to Use**:

1. **Set Up HTTPS Tunnel** (Required)
   ```bash
   # On your server
   cloudflared tunnel --url http://localhost:8080
   ```
   Copy the HTTPS URL provided (e.g., `https://abc123.trycloudflare.com`)

2. **Configure Playground**:
   - Go to: https://infinitewebarena.autoppia.com/playground
   - **Agent Endpoint**: Enter your endpoint
     - Format: `IP:PORT` (e.g., `134.199.203.133:8080`)
     - Or HTTPS tunnel URL (without `https://`)
   - **Select Web Projects**: Choose projects to test
   - **Select Use Cases**: Choose specific use cases
   - **Number of Runs**: Start with 1-3 for testing

3. **Run Benchmark**:
   - Click "Run Benchmark"
   - Monitor execution
   - Review results

**What to Verify**:
- ✅ Playground connects to your API
- ✅ Tasks are sent successfully
- ✅ Actions are generated
- ✅ Tasks complete (even if not 100% success)
- ✅ No errors in console

### 2. Official Test Suite

**Location**: `tests/test_official.py`

**Run Tests**:
```bash
# Test local API
python3 tests/test_official.py

# Test remote API
python3 tests/test_official.py http://134.199.203.133:8080
```

**Tests Included**:
- ✅ Health endpoint
- ✅ CORS headers
- ✅ solve_task endpoint
- ✅ Response time (< 2s)
- ✅ Action format (IWA BaseAction compliance)

### 3. Manual API Testing

**Test Health**:
```bash
curl http://localhost:8080/health
```

**Test solve_task**:
```bash
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-001",
    "prompt": "Click the login button",
    "url": "https://example.com"
  }'
```

**Expected Response**:
```json
{
  "actions": [...],
  "web_agent_id": "test-001",
  "recording": "",
  "id": "test-001",
  "task_id": "test-001"
}
```

## 📋 Pre-Deployment Checklist

### API Compliance
- [ ] Health endpoint returns 200
- [ ] solve_task endpoint accepts POST requests
- [ ] Response format matches IWA BaseAction
- [ ] CORS headers enabled
- [ ] Response time < 2s

### Action Format
- [ ] All actions have `type` field
- [ ] NavigateAction has `url`
- [ ] ClickAction has `selector`
- [ ] TypeAction has `selector` and `text`
- [ ] WaitAction has `time_seconds`
- [ ] Selectors are valid IWA selector types

### Miner Setup
- [ ] Miner registered on subnet 36
- [ ] Axon serving on port 8091
- [ ] API accessible on port 8080
- [ ] Metagraph syncing correctly
- [ ] Services running (systemd)

### Testing
- [ ] Passes official test suite
- [ ] Works on IWA Playground
- [ ] Handles various task types
- [ ] No errors in logs
- [ ] Response times acceptable

## 🔍 Official Resources

### Documentation
- **Official Docs**: https://luxit.gitbook.io/autoppia-docs
- **IWA Playground**: https://infinitewebarena.autoppia.com/playground
- **GitHub**: https://github.com/autoppia/autoppia_web_agents_subnet

### Testing Tools
- **IWA Playground**: Official testing tool
- **Official Test Suite**: `tests/test_official.py`
- **Local Testing**: `tests/test_api.py`

## 🚀 Quick Test Procedure

### Step 1: Run Official Test Suite
```bash
python3 tests/test_official.py
```

### Step 2: Test on IWA Playground
1. Set up HTTPS tunnel
2. Go to playground
3. Enter endpoint
4. Run benchmark
5. Verify results

### Step 3: Monitor Logs
```bash
journalctl -u autoppia-api -f
```

### Step 4: Verify Deployment
```bash
curl http://localhost:8080/health
curl http://localhost:8080/metrics
```

## ✅ Success Criteria

### Must Pass
- ✅ All official tests pass
- ✅ Playground connects successfully
- ✅ Actions generated correctly
- ✅ Response format compliant
- ✅ Response time < 2s

### Should Pass
- ✅ Tasks complete successfully
- ✅ Success rate > 50%
- ✅ No errors in logs
- ✅ CORS working correctly

## 📊 Testing Results Template

```
Date: [DATE]
Tester: [NAME]

Official Test Suite:
- Health Endpoint: ✅/❌
- CORS Headers: ✅/❌
- solve_task Endpoint: ✅/❌
- Response Time: ✅/❌ ([TIME]s)
- Action Format: ✅/❌

IWA Playground:
- Connection: ✅/❌
- Tasks Executed: [NUMBER]
- Success Rate: [PERCENTAGE]%
- Errors: [NONE/ERRORS]

Overall Status: ✅ READY / ❌ NEEDS FIXES
```

## 🎯 Next Steps After Testing

1. **If All Tests Pass**:
   - ✅ Deploy to production
   - ✅ Monitor validator activity
   - ✅ Optimize based on feedback

2. **If Tests Fail**:
   - ❌ Fix identified issues
   - ❌ Re-run tests
   - ❌ Verify fixes

---

**Remember**: The IWA Playground is the official testing tool. Always test there before considering deployment complete!

