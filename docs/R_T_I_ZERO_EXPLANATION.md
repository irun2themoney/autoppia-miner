# 🚨 R/T/I = 0 Problem - Why You're Not Getting Graded

**Based on Discord conversation with Dr. Riiveer**

---

## 🔍 **What R/T/I Means**

**R/T/I** = **Rank / Trust / Incentive**

These are the **Bittensor metrics** that determine:
- ✅ Whether validators grade your miner
- ✅ Your rewards (TAO earnings)
- ✅ Your position on the leaderboard

---

## ❌ **The Problem**

**Jose's Situation** (from Discord):
- ✅ **679 `/solve_task` calls** (mostly from playground)
- ✅ **175 `StartRoundSynapse` connections**
- ❌ **R/T/I = 0** (Rank/Trust/Incentive all zero)

**What This Means**:
- Your miner is **receiving requests** ✅
- Your miner is **responding** ✅
- But validators are **NOT grading you** ❌
- Therefore, **no rewards** ❌

---

## 🎯 **Why R/T/I = 0?**

### **Dr. Riiveer's Question**: "did you test benchmark?"

This suggests that **validators require you to pass a benchmark test** before they start grading you.

**The Issue**:
- Playground calls (`/solve_task`) don't count for grading
- `StartRoundSynapse` connections don't automatically mean grading
- **You need to pass the official benchmark** for validators to start grading

---

## ✅ **What You Need to Do**

### **Step 1: Test on the Official Benchmark** 🔴 **CRITICAL**

**The benchmark is likely**:
- **IWA Playground**: https://infinitewebarena.autoppia.com/playground
- **Or**: A specific benchmark API endpoint

**How to Test**:
1. Go to: https://infinitewebarena.autoppia.com/playground
2. Enter your API endpoint: `134.199.203.133:8080`
3. Click **"Run Benchmark"**
4. **Complete the benchmark successfully**

**What This Does**:
- Validates your miner works correctly
- Signals to validators that you're ready
- Enables grading to begin

---

### **Step 2: Verify Your Miner is Accessible**

**Check Your API**:
```bash
# On your server
curl -X POST http://134.199.203.133:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id":"test","prompt":"test","url":"https://example.com"}'
```

**Should return**:
```json
{
  "actions": [...],
  "web_agent_id": "test",
  "recording": "",
  "id": "test"
}
```

---

### **Step 3: Check Your Miner's Status**

**Verify Registration**:
```bash
# Check if you're registered on the metagraph
btcli subnet metagraph --netuid 36 | grep YOUR_UID
```

**Check Axon Serving**:
```bash
# Verify your axon is being served
journalctl -u autoppia-miner | grep "Axon served"
```

---

## 🔍 **Why Playground Calls Don't Count**

**Playground calls** (`/solve_task` from playground):
- ✅ Test your API
- ✅ Verify it works
- ❌ **Don't count for grading**
- ❌ **Don't affect R/T/I**

**Only validator-graded tasks count**:
- Validators must explicitly grade your responses
- This happens **after** you pass the benchmark
- Grading determines your R/T/I scores

---

## 📊 **What Validators Look For**

### **Before Grading** (Benchmark Test):
1. ✅ API is accessible
2. ✅ API responds correctly
3. ✅ Actions are in correct format
4. ✅ Benchmark test passes

### **During Grading** (After Benchmark):
1. ✅ Task completion rate
2. ✅ Response time
3. ✅ Action quality
4. ✅ Website coverage

---

## 🚀 **Action Plan**

### **Immediate Actions**:

1. **Test on IWA Playground** 🔴 **DO THIS NOW**
   - URL: https://infinitewebarena.autoppia.com/playground
   - Enter: `134.199.203.133:8080`
   - Click: "Run Benchmark"
   - **Complete the benchmark**

2. **Verify API is Working**
   ```bash
   curl -X POST http://134.199.203.133:8080/solve_task \
     -H "Content-Type: application/json" \
     -d '{"id":"benchmark-test","prompt":"Click button","url":"https://example.com"}'
   ```

3. **Monitor for Validator Grading**
   ```bash
   # Watch for actual validator grading (not just playground calls)
   journalctl -u autoppia-api -f | grep -E "validator|grade|score"
   ```

4. **Check Your R/T/I Scores**
   - Check dashboard: http://134.199.203.133:8080/dashboard
   - Look for Rank, Trust, Incentive values
   - They should be > 0 after benchmark passes

---

## 🎯 **Expected Outcome**

### **After Passing Benchmark**:
- ✅ Validators start grading your tasks
- ✅ R/T/I scores begin to increase
- ✅ You start earning rewards
- ✅ Your rank improves

### **If R/T/I Still = 0**:
- ⚠️ Benchmark may not have passed
- ⚠️ API may not be accessible to validators
- ⚠️ Miner may not be properly registered
- ⚠️ Need to check with Dr. Riiveer for specific issues

---

## 📋 **Summary**

**The Problem**:
- You're getting requests (playground, StartRoundSynapse)
- But R/T/I = 0 (not being graded)

**The Solution**:
- **Test on the official benchmark** (IWA Playground)
- Pass the benchmark test
- Validators will then start grading you
- R/T/I scores will increase
- You'll start earning rewards

**Next Step**: 🔴 **Go to IWA Playground and run the benchmark NOW!**

---

**Status**: ⚠️ **ACTION REQUIRED** - Test on benchmark to enable grading.

