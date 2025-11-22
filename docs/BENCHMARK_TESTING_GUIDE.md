# 🧪 Benchmark Testing Guide - Step by Step

**Goal**: Test your miner on the official IWA benchmark to enable validator grading

---

## ✅ **Pre-Test Checklist**

Before running the benchmark, verify:

1. ✅ **API is accessible** from the internet
2. ✅ **API responds correctly** to `/solve_task` requests
3. ✅ **Actions are in correct format** (IWA BaseAction)
4. ✅ **CORS is enabled** (for playground)
5. ✅ **Miner is registered** on the metagraph

---

## 🚀 **Step 1: Verify API is Working**

### **Test 1: Health Check**
```bash
curl http://134.199.203.133:8080/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "..."
}
```

### **Test 2: Solve Task Endpoint**
```bash
curl -X POST http://134.199.203.133:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-123",
    "prompt": "Click the button",
    "url": "https://example.com"
  }'
```

**Expected Response**:
```json
{
  "actions": [
    {
      "action_type": "click",
      "selector": {
        "type": "cssSelector",
        "value": "button"
      }
    }
  ],
  "web_agent_id": "test-123",
  "recording": "",
  "id": "test-123"
}
```

---

## 🎯 **Step 2: Test on IWA Playground**

### **2.1. Open the Playground**
1. Go to: **https://infinitewebarena.autoppia.com/playground**
2. Wait for the page to load

### **2.2. Enter Your API Endpoint**
1. Find the input field for "API Endpoint" or "Agent URL"
2. Enter: `134.199.203.133:8080`
   - **Note**: Don't include `http://` - just the IP and port
   - Alternative: `http://134.199.203.133:8080` (if it requires full URL)

### **2.3. Configure Benchmark Settings** (if available)
- **Number of tasks**: Start with 5-10 tasks
- **Task types**: Leave default (or select "All")
- **Timeout**: Should be 90 seconds (default)

### **2.4. Run the Benchmark**
1. Click **"Run Benchmark"** or **"Start Test"** button
2. **Monitor your API logs** (see Step 3)
3. Wait for benchmark to complete

---

## 📊 **Step 3: Monitor During Benchmark**

### **3.1. Watch API Logs** (Real-time)
```bash
# SSH into your server
ssh root@134.199.203.133

# Watch API logs
journalctl -u autoppia-api -f | grep solve_task
```

**What to Look For**:
- ✅ `POST /solve_task` requests coming in
- ✅ Response status `200 OK`
- ✅ Response times (should be < 90 seconds)
- ❌ Any errors or timeouts

### **3.2. Watch Miner Logs** (Real-time)
```bash
# In another terminal
journalctl -u autoppia-miner -f
```

**What to Look For**:
- ✅ `VALIDATOR_CONNECTION` logs
- ✅ Synapse processing
- ❌ Any errors

### **3.3. Check Dashboard** (Real-time)
- Open: **http://134.199.203.133:8080/dashboard**
- Watch for:
  - ✅ New requests coming in
  - ✅ Success rate updates
  - ✅ Response time metrics

---

## ✅ **Step 4: Verify Benchmark Results**

### **4.1. Check Playground Results**
After benchmark completes, you should see:
- ✅ **Success rate** (should be > 50%)
- ✅ **Average response time** (should be < 90s)
- ✅ **Tasks completed** (should match number of tasks)
- ✅ **Score** (if displayed)

### **4.2. Check Your Logs**
```bash
# Count successful requests
journalctl -u autoppia-api --since '10 minutes ago' | grep "200" | wc -l

# Check for errors
journalctl -u autoppia-api --since '10 minutes ago' | grep -i error
```

### **4.3. Check Dashboard Metrics**
- Go to: **http://134.199.203.133:8080/dashboard**
- Verify:
  - ✅ Total requests increased
  - ✅ Success rate is good (> 50%)
  - ✅ No errors shown

---

## 🎯 **Step 5: Verify R/T/I Scores**

### **5.1. Check Metagraph**
After benchmark passes, wait 1-2 hours, then check:

```bash
# Check your UID's R/T/I scores
btcli subnet metagraph --netuid 36 | grep YOUR_UID
```

**Look for**:
- **Rank**: Should be > 0
- **Trust**: Should be > 0
- **Incentive**: Should be > 0

### **5.2. Check Dashboard**
- Go to: **http://134.199.203.133:8080/dashboard**
- Look at "Wallet" section:
  - **Rank**: Should show a number > 0
  - **Trust**: Should show a number > 0
  - **Incentive**: Should show a number > 0

---

## ❌ **Troubleshooting**

### **Problem: API Not Accessible**
**Symptoms**:
- Playground shows "Connection failed"
- Can't reach API from browser

**Solutions**:
1. Check firewall: `ufw status`
2. Verify port 8080 is open: `netstat -tlnp | grep 8080`
3. Check API is running: `systemctl status autoppia-api`
4. Test from server: `curl http://localhost:8080/health`

### **Problem: Benchmark Times Out**
**Symptoms**:
- Requests take > 90 seconds
- Playground shows timeout errors

**Solutions**:
1. Check API response times: `journalctl -u autoppia-api | grep "response_time"`
2. Optimize slow endpoints
3. Check server resources: `htop`
4. Verify timeout is set to 90s in settings

### **Problem: Actions Format Error**
**Symptoms**:
- Playground shows "Invalid action format"
- Validator rejects actions

**Solutions**:
1. Verify actions match IWA BaseAction format
2. Check `api/actions/generator.py` output
3. Test with simple task: `{"id":"test","prompt":"click button","url":"https://example.com"}`
4. Review action structure in logs

### **Problem: CORS Error**
**Symptoms**:
- Browser console shows CORS errors
- Playground can't call API

**Solutions**:
1. Verify CORS is enabled in `api/server.py`
2. Check CORS middleware configuration
3. Test with: `curl -H "Origin: https://infinitewebarena.autoppia.com" ...`

### **Problem: R/T/I Still = 0 After Benchmark**
**Symptoms**:
- Benchmark completes successfully
- But R/T/I scores remain 0

**Solutions**:
1. Wait 1-2 hours (scores update periodically)
2. Verify benchmark actually passed (check playground results)
3. Check if validators are actually grading (not just playground calls)
4. Contact Dr. Riiveer on Discord for specific issues

---

## 📋 **Quick Test Commands**

### **Full Test Sequence**
```bash
# 1. Health check
curl http://134.199.203.133:8080/health

# 2. Test solve_task
curl -X POST http://134.199.203.133:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id":"test","prompt":"click button","url":"https://example.com"}'

# 3. Check logs
ssh root@134.199.203.133 "journalctl -u autoppia-api --since '5 minutes ago' | tail -20"
```

---

## ✅ **Success Criteria**

**Benchmark Passes If**:
- ✅ API responds to all requests
- ✅ Actions are in correct format
- ✅ Success rate > 50%
- ✅ No critical errors
- ✅ Response times < 90 seconds

**R/T/I Scores Update If**:
- ✅ Benchmark passes
- ✅ Validators start grading
- ✅ Wait 1-2 hours for scores to update
- ✅ Check metagraph or dashboard

---

## 🚀 **Next Steps After Benchmark**

1. **Monitor R/T/I Scores**:
   - Check every hour for first 24 hours
   - Scores should start increasing

2. **Monitor Validator Activity**:
   - Watch for actual validator grading (not playground)
   - Check dashboard for new requests

3. **Optimize Performance**:
   - If success rate < 70%, optimize actions
   - If response time > 10s, optimize speed
   - If errors occur, fix issues

4. **Engage with Community**:
   - Report benchmark results on Discord
   - Ask for feedback from Dr. Riiveer
   - Share your experience

---

**Status**: ✅ **READY TO TEST** - Follow steps above to run benchmark!

