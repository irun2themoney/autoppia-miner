# Quick Testing Guide - Server & Playground

## 🚀 Quick Start

### Step 1: Test on Server
```bash
# Run official tests on your server
bash scripts/test_on_server.sh
```

### Step 2: Set Up HTTPS Tunnel (for Playground)
```bash
# Install cloudflared and start tunnel
bash scripts/setup_playground_testing.sh
```

### Step 3: Get Tunnel URL
```bash
# Get your HTTPS tunnel URL
bash scripts/get_tunnel_url.sh
```

### Step 4: Test on IWA Playground
1. Go to: https://infinitewebarena.autoppia.com/playground
2. Enter endpoint: `134.199.203.133:8080` (or HTTPS tunnel URL)
3. Select projects and use cases
4. Click "Run Benchmark"
5. Monitor results

## 📋 Testing Checklist

### Local Testing (Already Done ✅)
- [x] Official test suite: 5/5 tests passed
- [x] Health endpoint: Working
- [x] CORS headers: Working
- [x] solve_task endpoint: Working
- [x] Response time: < 2s
- [x] Action format: Valid

### Server Testing
- [ ] Run official tests on server
- [ ] Verify API is accessible
- [ ] Check logs for errors

### Playground Testing
- [ ] Set up HTTPS tunnel
- [ ] Get tunnel URL
- [ ] Test on IWA Playground
- [ ] Verify tasks execute
- [ ] Check success rates

## 🔧 Manual Server Commands

### SSH to Server
```bash
ssh root@134.199.203.133
```

### Run Tests
```bash
cd /opt/autoppia-miner
python3 tests/test_official.py http://localhost:8080
```

### Start HTTPS Tunnel
```bash
# Install cloudflared (if needed)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Start tunnel in screen session
screen -dmS tunnel bash -c 'cloudflared tunnel --url http://localhost:8080'

# View tunnel output
screen -r tunnel
```

### Monitor Logs
```bash
# API logs
journalctl -u autoppia-api -f

# Miner logs
journalctl -u autoppia-miner -f

# Check for validator activity
journalctl -u autoppia-api -f | grep solve_task
```

## ✅ Success Indicators

### Tests Pass
- ✅ All 5 official tests pass
- ✅ Health endpoint returns 200
- ✅ Actions generated correctly
- ✅ Response time < 2s

### Playground Works
- ✅ Playground connects to API
- ✅ Tasks are sent successfully
- ✅ Actions are generated
- ✅ Tasks execute (even if not 100% success)

## 🎯 Next Steps After Testing

1. **If All Tests Pass**:
   - ✅ Monitor validator activity
   - ✅ Optimize based on feedback
   - ✅ Track performance metrics

2. **If Tests Fail**:
   - ❌ Check logs for errors
   - ❌ Verify services are running
   - ❌ Fix issues and re-test

---

**Remember**: The IWA Playground is the official testing tool. Always test there before considering deployment complete!

