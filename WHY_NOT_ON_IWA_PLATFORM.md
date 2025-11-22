# Why Your Miner Isn't Showing on IWA Platform

**Your Miner Status**: ✅ **UID 160, Registered, Active**

**Issue**: Not appearing on https://infinitewebarena.autoppia.com/subnet36/rounds/round_60

---

## ✅ **What's Working**

1. **Registration**: ✅ UID 160 on subnet 36
2. **Axon**: ✅ Served to network (134.199.203.133:8091)
3. **API**: ✅ 250 requests in last 24 hours
4. **Services**: ✅ Running and responding

---

## 🔍 **Why You're Not on the Platform**

### **1. Round Participation Requirements**

The IWA platform shows miners that:
- ✅ Are registered (you are - UID 160)
- ✅ Have been selected by validators for that specific round
- ✅ Have completed tasks in that round
- ✅ Have results to display

**Round 60** is a specific round. Your miner needs to:
1. Be selected by validators for round 60
2. Complete tasks in round 60
3. Have results evaluated

**Current Status**: You're receiving requests (250 in 24h), but these may be:
- General validator testing (not round-specific)
- Different rounds (not round 60)
- Tasks that haven't been evaluated yet

---

### **2. Validator Selection**

Not all miners appear in every round. Validators:
- Select a subset of miners for each round
- May prioritize top performers
- May rotate through miners
- May test new miners separately

**Your Status**: You're receiving requests, which means validators are testing you, but you may not have been selected for round 60 specifically.

---

### **3. Data Propagation Delay**

The IWA platform may have delays:
- Results need to be processed
- Data needs to be aggregated
- Platform may update periodically (not real-time)

**Timeline**: If you just started receiving requests, it may take time for results to appear.

---

### **4. Success Rate Requirements**

The platform may only show miners with:
- Minimum success rate
- Completed tasks
- Valid results

**Your Status**: If your success rate is low or tasks are failing, you may not appear even if you're being tested.

---

## 🎯 **What You Can Do**

### **1. Check Your Actual Performance**

```bash
# Check recent API requests and responses
ssh root@134.199.203.133
journalctl -u autoppia-api --since '1 hour ago' | grep solve_task
```

### **2. Test on Playground First**

Before appearing on rounds, test on the playground:
- **URL**: https://infinitewebarena.autoppia.com
- **Purpose**: Verify your miner works correctly
- **Result**: If playground works, rounds will work

### **3. Check Other Rounds**

Round 60 may be specific. Check:
- **Overview**: https://infinitewebarena.autoppia.com/subnet36/overview
- **All Rounds**: https://infinitewebarena.autoppia.com/subnet36/rounds
- **Agents Page**: https://infinitewebarena.autoppia.com/subnet36/agents

Your miner (UID 160) may appear in:
- Different rounds
- Agents page (all miners)
- Overview page (leaderboard)

### **4. Wait for Next Round**

If you're not in round 60:
- Validators will test you in future rounds
- Results will appear once you participate
- Platform updates periodically

---

## 📊 **Understanding IWA Platform Display**

### **Rounds Page Shows**:
- Miners selected for that specific round
- Results from that round only
- Validator-specific results

### **Agents Page Shows**:
- All registered miners
- Overall performance
- Historical data

### **Overview Page Shows**:
- Leaderboard rankings
- Top performers
- Overall statistics

---

## ✅ **Your Current Status**

**You ARE being tested** (250 requests proves this), but:
- You may not be in round 60 specifically
- Results may not be processed yet
- You may appear in other rounds/pages

---

## 🚀 **Next Steps**

1. **Check Agents Page**: https://infinitewebarena.autoppia.com/subnet36/agents
   - Look for UID 160
   - See overall performance

2. **Check Overview Page**: https://infinitewebarena.autoppia.com/subnet36/overview
   - See if you're on the leaderboard
   - Check overall rankings

3. **Test on Playground**: https://infinitewebarena.autoppia.com
   - Verify your miner works
   - Get immediate feedback

4. **Wait for Next Round**:
   - Validators will test you in future rounds
   - Results will appear once you participate

---

## 📝 **Summary**

**You're not on round 60 because**:
- You may not have been selected for that specific round
- Results may not be processed yet
- You may appear in other rounds/pages

**But you ARE**:
- ✅ Registered (UID 160)
- ✅ Being tested (250 requests)
- ✅ Active and responding

**Check other pages on the IWA platform - you may already be there!**

