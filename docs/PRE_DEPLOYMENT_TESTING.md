# Pre-Deployment Testing Guide - Official Procedures

**Based on Official Autoppia IWA Documentation**

## 🎯 Official Testing Methods

### Method 1: IWA Playground (Primary Official Tool)

**URL**: https://infinitewebarena.autoppia.com/playground

**This is the official testing tool provided by Autoppia.**

#### Setup Steps:

1. **Ensure API is Running**
   ```bash
   curl http://localhost:8080/health
   ```

2. **Set Up HTTPS Tunnel** (Required for Playground)
   ```bash
   # On your server
   cloudflared tunnel --url http://localhost:8080
   ```
   Copy the HTTPS URL (e.g., `https://abc123.trycloudflare.com`)

3. **Test on Playground**:
   - Go to: https://infinitewebarena.autoppia.com/playground
   - Enter endpoint: `IP:PORT` format (e.g., `134.199.203.133:8080`)
   - Or use HTTPS tunnel URL (without `https://`)
   - Select projects and use cases
   - Click "Run Benchmark"
   - Monitor results

#### What the Playground Tests:
- ✅ API connectivity
- ✅ Action generation
- ✅ Task execution
- ✅ Success rates
- ✅ Response times

### Method 2: Official Test Suite

**Location**: `tests/test_official.py`

**Run Tests**:
```bash
# Local
python3 tests/test_official.py

# Remote
python3 tests/test_official.py http://134.199.203.133:8080
```

**Or use the script**:
```bash
bash scripts/test_official.sh http://134.199.203.133:8080
```

### Method 3: Manual API Testing

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

## 📋 Official Pre-Deployment Checklist

### API Requirements (From Official Docs)
- [ ] **Endpoint**: `POST /solve_task` exists
- [ ] **Request Format**: `{id, prompt, url}` accepted
- [ ] **Response Format**: `{actions, web_agent_id, recording}` returned
- [ ] **Action Format**: IWA BaseAction format
- [ ] **CORS**: Enabled for cross-origin
- [ ] **Response Time**: < 2s (recommended)

### Miner Requirements
- [ ] **Registered**: On subnet 36
- [ ] **Axon Serving**: Port 8091
- [ ] **API Accessible**: Port 8080
- [ ] **Metagraph Sync**: Working
- [ ] **Services Running**: systemd active

### Testing Requirements
- [ ] **Playground Test**: Passes on IWA Playground
- [ ] **Test Suite**: All tests pass
- [ ] **Manual Tests**: API responds correctly
- [ ] **Logs Clean**: No critical errors

## 🔍 Official Resources

### Documentation
- **Official Docs**: https://luxit.gitbook.io/autoppia-docs
- **IWA Playground**: https://infinitewebarena.autoppia.com/playground
- **GitHub**: https://github.com/autoppia/autoppia_web_agents_subnet

### Discord
- **Official Discord**: https://discord.gg/autoppia
- **Channels to Check**:
  - #miners - Miner discussions
  - #announcements - Official updates
  - #support - Help and troubleshooting

## ✅ Testing Procedure

### Step 1: Local Testing
```bash
# Run official test suite
python3 tests/test_official.py

# Or use script
bash scripts/test_official.sh
```

### Step 2: Playground Testing
1. Set up HTTPS tunnel
2. Go to playground
3. Enter endpoint
4. Run benchmark
5. Review results

### Step 3: Production Verification
```bash
# Check health
curl http://134.199.203.133:8080/health

# Check metrics
curl http://134.199.203.133:8080/metrics

# Monitor logs
journalctl -u autoppia-api -f
```

## 🎯 Success Criteria

### Must Pass
- ✅ Health endpoint returns 200
- ✅ solve_task accepts requests
- ✅ Actions generated in correct format
- ✅ CORS headers present
- ✅ Playground connects successfully

### Should Pass
- ✅ Response time < 2s
- ✅ Tasks complete successfully
- ✅ Success rate > 50%
- ✅ No errors in logs

## 📊 Testing Results

After running tests, you should see:
- ✅ All official tests pass
- ✅ Playground connects
- ✅ Actions generated
- ✅ Tasks execute
- ✅ No critical errors

## 🚀 Next Steps

1. **If All Tests Pass**:
   - ✅ Deploy to production
   - ✅ Monitor validator activity
   - ✅ Optimize based on feedback

2. **If Tests Fail**:
   - ❌ Fix identified issues
   - ❌ Re-run tests
   - ❌ Verify fixes

---

**Key Point**: The IWA Playground is the official testing tool. Always test there before considering deployment complete!

