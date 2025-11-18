# ⏱️ Validator Discovery Timing After Redeployment

**Last Updated**: November 18, 2025

## 🎯 Quick Answer

**After redeployment, validators typically start communicating within:**
- **5-15 minutes**: Initial discovery (metagraph sync)
- **15-30 minutes**: First test requests
- **30-60 minutes**: Regular task flow begins

**However**, this depends on when validators are actively running rounds.

---

## 📊 Discovery Timeline Breakdown

### **Immediate (0-5 minutes)**
✅ **Miner appears in metagraph**
- Your miner registers immediately when it starts
- UID is assigned and visible on the network
- Axon is served to subtensor network

### **5-15 minutes: Validator Discovery**
✅ **Validators discover your miner**
- Validators sync metagraph every **1-5 minutes**
- During their next sync, they see your miner (UID 160)
- They read your axon metadata (IP, port, API URL)

### **15-30 minutes: Initial Testing**
✅ **Validators verify and test**
- Validators call your `/health` endpoint
- They verify your API is accessible
- They send initial test tasks to `/solve_task`

### **30-60 minutes: Regular Flow**
✅ **Regular task flow begins**
- Validators include you in their regular testing cycles
- Tasks start flowing consistently
- Your scores begin accumulating

---

## 🔄 Round-Based Discovery

### **Current Round Status**
Based on IWA Platform data:
- **Round 36** is currently running (59% complete, 444 blocks remaining)
- **Round duration**: Typically 1-2 hours per round
- **Validators test during active rounds**

### **When Validators Query**
Validators query miners:
1. **At round start**: Validators discover new miners
2. **During rounds**: Validators test miners with tasks
3. **Between rounds**: Validators may do health checks

### **After Redeployment**
If you redeploy **during an active round**:
- ✅ Validators may discover you **immediately** (if they sync metagraph)
- ⏱️ Or they may wait until **next round starts**
- 📊 Most activity happens **during active rounds**

---

## ⚡ Factors Affecting Discovery Speed

### **1. Metagraph Sync Frequency**
- **Validators sync**: Every 1-5 minutes
- **Your miner re-serves axon**: Every 3 minutes
- **Result**: Discovery within 5-15 minutes typically

### **2. Validator Activity**
- **Active validators**: Discover faster (they sync more frequently)
- **Inactive validators**: May take longer
- **Current**: 2-4 validators active per round

### **3. Round Timing**
- **During active round**: Faster discovery (validators actively querying)
- **Between rounds**: Slower (validators may be idle)
- **Round start**: Best time for discovery

### **4. Network Conditions**
- **Low latency**: Faster discovery
- **High latency**: Slower discovery
- **Firewall/ports**: Must be accessible

---

## 📈 What to Expect After Redeployment

### **Scenario 1: Redeploy During Active Round** ⚡ FASTEST
- **0-5 min**: Miner appears in metagraph
- **5-15 min**: Validators discover during metagraph sync
- **15-30 min**: First test requests arrive
- **30-60 min**: Regular task flow

### **Scenario 2: Redeploy Between Rounds** ⏱️ MODERATE
- **0-5 min**: Miner appears in metagraph
- **5-15 min**: Validators discover during metagraph sync
- **Wait for next round**: Validators may wait until round starts
- **Round start**: Validators begin testing
- **Total**: 15-60 minutes (depending on round timing)

### **Scenario 3: Redeploy During Low Activity** 🐌 SLOWEST
- **0-5 min**: Miner appears in metagraph
- **5-15 min**: Validators discover
- **Wait for validator activity**: May take longer if validators are idle
- **Total**: 30-120 minutes

---

## ✅ How to Verify Discovery

### **1. Check Miner Status**
```bash
ssh root@134.199.203.133 "journalctl -u autoppia-miner -n 50 | grep -i 'uid\|serving\|axon'"
```

**Look for**:
- ✅ `UID: 160` (or your UID)
- ✅ `Serving axon on port 8091`
- ✅ `Axon served to subtensor network`

### **2. Check for Validator Requests**
```bash
ssh root@134.199.203.133 "journalctl -u autoppia-api --since '10 minutes ago' | grep -i 'POST.*solve_task' | tail -20"
```

**Look for**:
- ✅ Requests from external IPs (not 127.0.0.1)
- ✅ Status code 200 (successful)
- ✅ Validator IPs (e.g., 45.22.240.79, 84.247.180.192)

### **3. Monitor Dashboard**
- **Dashboard**: `http://134.199.203.133:8080/api/dashboard`
- **Watch for**: Total requests increasing
- **Check**: Recent activity showing validator IPs

### **4. Check IWA Platform**
- **URL**: `https://infinitewebarena.autoppia.com/subnet36/overview`
- **Look for**: Your UID (160) appearing in rounds
- **Check**: If you're receiving tasks in current round

---

## 🎯 Best Practices

### **1. Redeploy During Active Rounds**
- **Best time**: When rounds are actively running
- **Why**: Validators are actively querying miners
- **Result**: Faster discovery

### **2. Monitor After Redeployment**
- **First 15 minutes**: Check miner logs for axon serving
- **15-30 minutes**: Watch for validator requests
- **30-60 minutes**: Verify regular task flow

### **3. Verify Services**
- ✅ **Miner service**: `systemctl status autoppia-miner`
- ✅ **API service**: `systemctl status autoppia-api`
- ✅ **Ports**: 8080 and 8091 listening
- ✅ **Health**: `/health` endpoint responding

---

## 📊 Real-World Example

### **Your Current Status**
- **Deployed**: Latest enhancements (job patterns, etc.)
- **Miner**: Running and serving axon
- **API**: Accessible on port 8080
- **Current Round**: 36 (59% complete)

### **Expected Timeline**
1. **0-5 min**: ✅ Already visible in metagraph (UID 160)
2. **5-15 min**: Validators discover during next metagraph sync
3. **15-30 min**: First test requests (especially job tasks!)
4. **30-60 min**: Regular flow with new job pattern handling

### **What's Different Now**
With the new job pattern enhancements:
- ✅ Validators testing **APPLY_FOR_JOB** will get proper responses
- ✅ Validators testing **VIEW_JOB** will get proper responses
- ✅ Validators testing **SEARCH_JOBS** will get proper responses
- 🎯 **3 out of 4 validators** are testing job tasks - you're now ready!

---

## 🚀 Bottom Line

### **Typical Timeline**
- **5-15 minutes**: Validators discover you
- **15-30 minutes**: First test requests
- **30-60 minutes**: Regular task flow

### **Factors**
- ✅ **Metagraph sync**: Every 1-5 minutes (fast)
- ✅ **Round timing**: During active rounds (faster)
- ✅ **Validator activity**: Active validators (faster)

### **Your Situation**
- ✅ **Miner deployed**: Latest enhancements live
- ✅ **Round active**: Round 36 running (59% complete)
- ✅ **Validators active**: 2-4 validators testing
- 🎯 **Expected**: First requests within **15-30 minutes**

---

## 📝 Monitoring Commands

```bash
# Watch for validator requests in real-time
ssh root@134.199.203.133 "journalctl -u autoppia-api -f | grep 'POST.*solve_task'"

# Check recent validator activity
ssh root@134.199.203.133 "journalctl -u autoppia-api --since '30 minutes ago' | grep -E 'POST.*solve_task|INFO.*:\d+:\d+' | tail -30"

# Monitor dashboard metrics
curl -s http://134.199.203.133:8080/api/dashboard/metrics | python3 -m json.tool | grep -A 10 overview
```

---

**Status**: ✅ **Your miner is ready and discoverable!**

**Expected**: First validator requests within **15-30 minutes** of deployment.

