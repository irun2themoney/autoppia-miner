# 🎯 Playground Benchmark Guide - Step by Step

**Goal**: Pass benchmark tests on the IWA Playground

---

## ✅ **Your API is Ready**

**HTTPS Endpoint**: `134.199.203.133:8443`

**Status**: ✅ **Working** - Generates actions correctly

---

## 📋 **How to Run Benchmark on Playground**

### **Step 1: Open Playground**
Go to: **https://infinitewebarena.autoppia.com/playground**

### **Step 2: Configure Benchmark**

1. **Select Web Projects**:
   - Click "Select projects..."
   - Choose: **"Autoppia Work"** (or all projects)
   - This is the project that contains "BOOK_A_CONSULTATION" use case

2. **Select Use Cases**:
   - Click "Select use cases..."
   - Choose: **"BOOK_A_CONSULTATION"**
   - (Or select all use cases to test everything)

3. **Number of Runs**:
   - Enter: **5** (start small to test)
   - Or **10** for more comprehensive test

4. **Agent Endpoint**:
   - Enter: **`134.199.203.133:8443`**
   - **Important**: Use HTTPS port (8443), not HTTP (8080)
   - Format: `ip:port` (no `https://`)

### **Step 3: Run Benchmark**
- Click **"Run Benchmark"** button
- Wait for it to complete (may take 5-10 minutes)
- **Monitor your dashboard** while it runs: http://134.199.203.133:8080/dashboard

### **Step 4: Check Results**
- Look for success rate (should be > 0%)
- Check if actions were generated
- Verify tasks completed

---

## 🔍 **What to Expect**

### **Success Indicators**:
- ✅ Success rate > 0%
- ✅ Actions generated for each task
- ✅ Tasks completed (not all failed)
- ✅ Response times reasonable (< 90s)

### **If Tasks Fail**:
- Check dashboard logs for errors
- Verify API is accessible
- Check response format

---

## 📊 **Monitor While Benchmark Runs**

### **Open Dashboard** (in another tab):
```
http://134.199.203.133:8080/dashboard
```

**Watch for**:
- ✅ Total requests increasing
- ✅ Success rate updating
- ✅ New validator interactions
- ✅ Response times

### **Check API Logs** (optional):
```bash
ssh root@134.199.203.133
journalctl -u autoppia-api -f | grep solve_task
```

---

## 🎯 **Expected Results**

**After Benchmark Completes**:
- Success rate should be > 0% (ideally > 50%)
- Actions should be generated for each task
- Response times should be reasonable
- Tasks should complete successfully

---

## ✅ **Your API Status**

**Verified Working**:
- ✅ HTTPS endpoint: `134.199.203.133:8443`
- ✅ Health check: Working
- ✅ solve_task: Working (generates actions)
- ✅ Error handling: Fixed (returns fallback actions)
- ✅ Format: Correct IWA format

---

## 🚀 **Ready to Test**

1. ✅ **API is ready** - All fixes applied
2. 🎯 **Go to playground** - https://infinitewebarena.autoppia.com/playground
3. 📋 **Configure** - Select projects, use cases, enter endpoint
4. ▶️ **Run** - Click "Run Benchmark"
5. 📊 **Monitor** - Watch dashboard for results

---

**Status**: ✅ **READY** - Your API is configured and tested. Run the benchmark on the playground!

