# Validator Discovery Timeline

## ✅ Current Status

### **Deployment Verified**
- ✅ Latest code deployed
- ✅ API service running
- ✅ Miner service running
- ✅ Miner registered: UID 160
- ✅ Axon served to network

## 🔍 How Validators Discover Your Miner

### **Discovery Process**

1. **Metagraph Sync**
   - Validators sync the metagraph every **1-5 minutes**
   - Your miner (UID 160) appears in the metagraph
   - Validators see your axon endpoint: `134.199.203.133:8091`

2. **Axon Metadata**
   - Validators read your axon metadata
   - They discover your API endpoint: `http://134.199.203.133:8080`
   - They verify your miner is active and responding

3. **Health Check**
   - Validators call your `/health` endpoint
   - They verify your API is accessible
   - They check your miner is ready for tasks

4. **Task Assignment**
   - Once verified, validators start sending tasks
   - Tasks come to `/solve_task` endpoint
   - Your miner processes and returns actions

## ⏱️ Discovery Timeline

### **Typical Timeline**

- **Immediate (0-5 minutes)**: Your miner appears in metagraph
- **5-15 minutes**: Validators discover your miner during metagraph sync
- **15-30 minutes**: Validators verify your API and start testing
- **30-60 minutes**: Regular task flow begins

### **Factors Affecting Discovery**

1. **Metagraph Sync Frequency**
   - Validators sync every 1-5 minutes
   - Your miner appears immediately after registration

2. **Validator Activity**
   - Active validators discover faster
   - Some validators may be offline or inactive

3. **Network Conditions**
   - Network latency affects discovery
   - Firewall/port accessibility matters

4. **Subnet Activity**
   - More active subnet = faster discovery
   - Subnet 36 is active, so discovery should be quick

## 📊 What to Expect

### **First Hour**
- ✅ Miner visible in metagraph
- ✅ Validators discover your miner
- ✅ Initial health checks
- ✅ First test tasks arrive

### **First 24 Hours**
- ✅ Regular task flow
- ✅ Performance metrics populate
- ✅ Dashboard shows activity
- ✅ Leaderboard ranking appears

### **Ongoing**
- ✅ Continuous task processing
- ✅ Performance optimization
- ✅ Earnings accumulation

## 🎯 How to Monitor Discovery

### **Check Miner Status**
```bash
# On server
journalctl -u autoppia-miner -f

# Look for:
# - "Axon served to subtensor network!"
# - "Processing task: ..."
# - Validator IP addresses
```

### **Check API Activity**
```bash
# On server
journalctl -u autoppia-api -f

# Look for:
# - POST /solve_task requests
# - Validator IP addresses
# - Task processing
```

### **Check Dashboard**
- Visit: `http://134.199.203.133:8080/api/dashboard`
- Watch for:
  - Total requests increasing
  - Validator activity appearing
  - Success rates updating

## ✅ Your Miner is Ready!

### **Current Status**
- ✅ **Deployed**: Latest code running
- ✅ **Registered**: UID 160 on subnet 36
- ✅ **Serving**: Axon visible to validators
- ✅ **Healthy**: API responding correctly
- ✅ **Ready**: Waiting for validator discovery

### **Expected Discovery**
- **Best Case**: 5-15 minutes
- **Typical**: 15-30 minutes
- **Worst Case**: 1-2 hours

**Your miner is fully operational and will be discovered soon!** 🚀

---

## 🔍 Quick Status Check

Run these commands to verify everything is working:

```bash
# Check services
systemctl status autoppia-api autoppia-miner

# Check recent activity
journalctl -u autoppia-miner --since '10 minutes ago' | grep -E 'serving|task|validator'

# Check API health
curl http://134.199.203.133:8080/health

# Check dashboard
curl http://134.199.203.133:8080/api/dashboard/metrics
```

**Status**: ✅ **READY - Waiting for Validator Discovery**

