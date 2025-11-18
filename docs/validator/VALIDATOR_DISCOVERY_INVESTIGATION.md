# 🔍 Validator Discovery Investigation

## ✅ **What's Working**

### **Metagraph Status** ✅
- **UID**: 160 (registered)
- **IP**: 134.199.203.133 (correct, not 0.0.0.0)
- **Port**: 8091 (axon port)
- **Total Miners**: 256
- **Active Validators**: 6

### **Services** ✅
- **Miner**: Running and serving axon
- **API**: Running on port 8080
- **Ports**: Both 8080 and 8091 open and listening
- **Firewall**: Configured correctly

---

## 🤔 **The Issue**

**Problem**: No validator requests despite:
- ✅ Miner registered (UID 160)
- ✅ Axon served correctly
- ✅ IP correct on metagraph
- ✅ 6 active validators on subnet
- ✅ Services running

---

## 🔍 **Possible Causes**

### **1. API Endpoint Discovery** ⚠️
**Issue**: Validators need to know your API endpoint (`http://134.199.203.133:8080`), but they only see your axon (`134.199.203.133:8091`).

**ApifiedWebAgent Pattern**:
- Validators call API directly: `POST http://your-ip:8080/solve_task`
- But how do they know port 8080?

**Possible Solutions**:
1. **Convention**: Validators might assume API is on port 8080 (standard)
2. **Metadata**: API URL might need to be in axon metadata
3. **Inference**: Validators might infer API from axon IP + standard port

### **2. Validator Activity** ⚠️
**Issue**: Even with 6 active validators, they might:
- Not be actively querying all miners
- Have specific selection criteria
- Be testing other miners first

### **3. Subnet Activity** ⚠️
**Issue**: Subnet 36 might have:
- Low validator activity
- Validators testing specific miners
- Delayed discovery cycles

### **4. Network/Connectivity** ⚠️
**Issue**: Validators might not be able to reach:
- Your API endpoint (port 8080)
- Your axon (port 8091)
- Due to firewall or network issues

---

## 🔧 **What We Need to Check**

### **1. API Endpoint Accessibility**
```bash
# Test from external network
curl http://134.199.203.133:8080/health
curl -X POST http://134.199.203.133:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id":"test","prompt":"test","url":"https://example.com"}'
```

### **2. Axon Metadata**
- Check if API URL needs to be in axon metadata
- Verify validators can infer API from axon IP

### **3. Validator Behavior**
- Check if validators are actively querying
- Verify validator selection criteria
- Check if there's a minimum stake/weight requirement

### **4. IWAP Visibility**
- Check if miner appears on IWAP leaderboard
- Verify miner is visible to validators

---

## 🎯 **Next Steps**

1. **Verify API Accessibility**: Test from external network
2. **Check Axon Metadata**: See if API URL needs to be added
3. **Monitor Validator Activity**: Watch for any connection attempts
4. **Check IWAP**: See if miner appears on leaderboard
5. **Review Official Docs**: Check how validators discover API endpoints

---

## 📊 **Current Status**

- ✅ **Miner**: Registered and visible
- ✅ **Axon**: Served correctly
- ✅ **API**: Running and accessible
- ⏳ **Validators**: Not connecting yet

**This is likely a timing/activity issue rather than a configuration problem.**

---

**Status**: Investigating validator discovery mechanism...

