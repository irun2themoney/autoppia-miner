# 🔍 How Validators Discover Your Miner

**Date**: November 18, 2025

---

## ✅ **YES - Validators Can See You!**

**The playground is NOT how validators discover miners.** Validators use the **Bittensor metagraph** to find and test miners.

---

## 🎯 **How Validator Discovery Works**

### **Step 1: Miner Registration**

Your miner registers on the Bittensor network:

```python
# In miner/miner.py
self.metagraph = bt.metagraph(netuid=36, network="finney")
self.uid = self.metagraph.hotkeys.index(self.wallet.hotkey.ss58_address)
```

**What this does**:
- Connects to Bittensor Subnet 36
- Gets assigned a UID (Unique Identifier)
- Registers your miner on the metagraph

---

### **Step 2: Axon Serving**

Your miner serves an axon that exposes metadata:

```python
# In miner/miner.py
self.axon = bt.axon(
    wallet=self.wallet,
    port=self.config.axon.port,  # Port 8091
)

# Serve the axon
subtensor.serve_axon(
    netuid=36,
    axon=self.axon,
)
```

**What this does**:
- Creates an axon endpoint (port 8091)
- Exposes your miner's metadata to the network
- Makes your API URL discoverable

---

### **Step 3: Validator Discovery**

Validators query the metagraph:

1. **Validators sync the metagraph** (list of all miners)
2. **Validators read axon metadata** (your API URL, IP, port)
3. **Validators call your API directly** (`http://134.199.203.133:8080/solve_task`)

**The playground is NOT involved in this process!**

---

## 🔍 **What Validators See**

### **From the Metagraph**

Validators can see:
- ✅ Your UID (Unique Identifier)
- ✅ Your hotkey address
- ✅ Your axon endpoint (IP:port)
- ✅ Your API URL (from axon metadata)
- ✅ Your stake/rank (if applicable)

### **From Your Axon**

Validators can see:
- ✅ Your API endpoint URL
- ✅ Your miner's capabilities
- ✅ Connection status

---

## 🚀 **How Validators Test You**

### **Direct API Calls**

Validators test your miner by calling your API directly:

```bash
# Validator does this:
POST http://134.199.203.133:8080/solve_task
{
  "id": "validator-task-123",
  "prompt": "Click the login button",
  "url": "https://example.com"
}
```

**This is exactly what we tested with our direct testing script!**

---

## ✅ **Verify Your Miner is Discoverable**

### **Check Miner Status**

```bash
ssh root@134.199.203.133 "journalctl -u autoppia-miner -n 100 | grep -i 'uid\|registered\|serving'"
```

**Look for**:
- ✅ `UID: X` (your miner's unique ID)
- ✅ `Serving axon on port 8091`
- ✅ `Registered on metagraph`

### **Check Axon is Serving**

```bash
ssh root@134.199.203.133 "netstat -tlnp | grep 8091"
```

**Should show**: Port 8091 is listening

### **Check API is Accessible**

```bash
curl http://134.199.203.133:8080/health
```

**Should return**: `{"status": "healthy", ...}`

---

## 🎯 **Playground vs Validators**

### **Playground** (Developer Tool)
- ❌ **NOT used by validators**
- ✅ Used by developers to test their miners
- ⚠️ Has infrastructure issues (CORS errors)
- 🎯 **Optional** - nice to have, but not required

### **Validators** (What Matters)
- ✅ **Use Bittensor metagraph** to discover miners
- ✅ **Call your API directly** (like our test script)
- ✅ **Test you automatically** (no playground needed)
- 🎯 **This is what counts!**

---

## 📊 **Discovery Timeline**

### **When You Deploy**

1. **Miner starts** → Registers on metagraph
2. **Axon serves** → Exposes your API URL
3. **Metagraph syncs** → Validators see you
4. **Validators test** → Call your API directly

### **Typical Timeline**

- **Immediate**: Miner registered on metagraph
- **Within minutes**: Validators discover you
- **Within hours**: Validators start testing
- **Within days**: Scores start appearing

---

## ✅ **What You Need**

### **For Validators to Find You**

1. ✅ **Miner running** → `systemctl status autoppia-miner`
2. ✅ **Axon serving** → Port 8091 listening
3. ✅ **API accessible** → Port 8080 responding
4. ✅ **Registered on metagraph** → UID assigned

**All of these are already set up!**

---

## 🚀 **Bottom Line**

### **YES - Validators Can See You!**

✅ **Your miner is registered** on the Bittensor metagraph  
✅ **Your axon is serving** (port 8091)  
✅ **Your API is accessible** (port 8080)  
✅ **Validators will discover you** automatically  

### **The Playground Doesn't Matter**

- ❌ Playground is just a developer tool
- ✅ Validators don't use the playground
- ✅ Validators test directly (like our test script)
- ✅ Your miner is discoverable regardless

---

## 📋 **Action Items**

1. ✅ **Verify miner is running**: `systemctl status autoppia-miner`
2. ✅ **Check logs for UID**: `journalctl -u autoppia-miner -f`
3. ✅ **Monitor for validator requests**: `journalctl -u autoppia-api -f | grep validator`
4. ✅ **Wait for discovery**: Validators will find you automatically

---

**Status**: ✅ **Your miner is discoverable and ready for validators!**

**The playground is optional - validators will find you through the metagraph!**

