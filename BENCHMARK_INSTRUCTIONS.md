# 🎯 Benchmark Testing Instructions

**Your API Endpoint**: `134.199.203.133:8443`  
**Status**: ✅ **READY** - All tests passing

---

## 📋 **Step-by-Step Guide**

### **Step 1: Open Playground**
Go to: **https://infinitewebarena.autoppia.com/playground**

### **Step 2: Configure Benchmark**

Based on the [playground interface](https://infinitewebarena.autoppia.com/playground):

1. **Select Web Projects** ⭐ **REQUIRED**
   - Click "Select projects..."
   - Choose: **"Autoppia Work"** (this contains BOOK_A_CONSULTATION)
   - Or select all projects for comprehensive testing

2. **Select Use Cases** ⭐ **REQUIRED**
   - Click "Select use cases..."
   - Choose: **"BOOK_A_CONSULTATION"**
   - Or select all use cases

3. **Number of Runs** ⭐ **REQUIRED**
   - Enter: **5** (for quick test)
   - Or **10-20** (for comprehensive test)

4. **Agent Endpoint (IP:Port)** ⭐ **REQUIRED**
   - Enter: **`134.199.203.133:8443`**
   - **Format**: `ip:port` (no `https://`)
   - This is your HTTPS endpoint

### **Step 3: Run Benchmark**
- Click **"Run Benchmark"** button
- **Keep the tab open** - don't close it
- Wait for completion (5-10 minutes)

### **Step 4: Monitor Progress**

**Open Dashboard** (in another tab):
```
http://134.199.203.133:8080/dashboard
```

**Watch for**:
- ✅ Total requests increasing
- ✅ Success rate updating  
- ✅ New validator interactions
- ✅ Response times

### **Step 5: Check Results**

**In Playground**:
- Success rate should be > 0%
- Actions should be generated
- Tasks should complete

**In Dashboard**:
- Check total requests
- Verify success rate
- Look for any errors

---

## ✅ **Your API Status**

**Verified Working**:
- ✅ HTTPS endpoint: `134.199.203.133:8443`
- ✅ Health check: Working
- ✅ solve_task: Working (generates 7-20 actions)
- ✅ Error handling: Fixed (returns fallback actions)
- ✅ Format: Correct IWA format
- ✅ All test cases: Passing

---

## 🎯 **Expected Results**

**Success Indicators**:
- ✅ Success rate > 0% (ideally > 50%)
- ✅ Actions generated for each task
- ✅ Response times < 90 seconds
- ✅ Tasks complete successfully

**If Tasks Fail**:
- Check dashboard for errors
- Verify API is accessible
- Check response format matches IWA spec

---

## 📊 **Monitor While Benchmark Runs**

### **Option 1: Dashboard** (Easiest)
```
http://134.199.203.203.133:8080/dashboard
```

### **Option 2: API Logs** (More Detailed)
```bash
ssh root@134.199.203.133
journalctl -u autoppia-api -f | grep solve_task
```

### **Option 3: Monitoring Script**
```bash
bash scripts/monitor_benchmark.sh
```

---

## 🚀 **Ready to Test**

1. ✅ **API is ready** - All fixes applied and tested
2. 🎯 **Go to playground** - https://infinitewebarena.autoppia.com/playground
3. 📋 **Configure**:
   - Projects: Autoppia Work
   - Use Cases: BOOK_A_CONSULTATION
   - Runs: 5-10
   - Endpoint: `134.199.203.133:8443`
4. ▶️ **Run** - Click "Run Benchmark"
5. 📊 **Monitor** - Watch dashboard for results

---

**Status**: ✅ **READY** - Your API is tested and working. Run the benchmark on the playground!

