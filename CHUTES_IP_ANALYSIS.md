# 🔍 Chutes API - IP-Based Rate Limiting Analysis

## 🎯 **Critical Finding**

**The API key works for "ridges" but NOT for our miner** - Even from local machine!

### **Test Results**:
- ✅ **Ridges**: Works perfectly
- ❌ **Our Miner (Server IP)**: 429 Rate Limited
- ❌ **Our Miner (Local IP)**: 429 Rate Limited

---

## 💡 **What This Means**

### **Most Likely Cause: IP-Based Rate Limiting** 🌐

If the key works for ridges but not for us (even from different IPs):
1. **Ridges IP**: Not rate limited ✅
2. **Our IPs** (server + local): Rate limited ❌
3. **Solution**: Need to use the same IP as ridges OR wait for rate limit to reset

### **Alternative Causes**:

1. **Timing Issue**:
   - Ridges used the API before rate limit window
   - We're hitting it during the rate limit window
   - **Solution**: Wait for rate limit window to reset

2. **Combined Usage**:
   - Ridges + Our Miner = Too many requests
   - Combined usage exceeds limits
   - **Solution**: Coordinate usage or use separate keys

3. **Request Format**:
   - Ridges might use different format
   - Our format might trigger rate limiting
   - **Solution**: Compare exact request format

---

## 🔍 **What to Check**

### **1. Test from Ridges IP** 🌐
- If ridges is on a different server/IP, test from there
- See if it works from ridges IP
- If yes → IP-based rate limiting confirmed

### **2. Check Timing** ⏰
- When did ridges last use the API?
- Is there a rate limit window?
- Wait and test again

### **3. Compare Request Format** 📋
- How does ridges call the API?
- Compare headers, payload, endpoint
- See if there are differences

### **4. Check Combined Usage** 📊
- Are ridges and our miner using the API simultaneously?
- Combined usage might exceed limits
- Check Chutes dashboard for total usage

---

## 🧪 **Quick Test**

### **Test from Ridges Context**:
If ridges is on a different server/IP:
```bash
# SSH into ridges server
ssh user@ridges-server

# Test from there
python3 test_chutes_simple.py
```

If it works from ridges IP but not ours → **IP-based rate limiting**

---

## 💡 **Most Likely Solution**

### **Option 1: Use Ridges IP** 🌐
- Deploy miner on same server/IP as ridges
- Or route requests through ridges IP

### **Option 2: Wait for Rate Limit Reset** ⏰
- Rate limit windows typically reset after 1 hour
- Wait and test again

### **Option 3: Contact Chutes Support** 📧
- Request IP whitelisting for our server IP
- Or ask about rate limit reset

### **Option 4: Use Separate API Key** 🔑
- Create new API key for our miner
- Keep ridges on its own key

---

## 📋 **Next Steps**

1. **Test from Ridges IP** - See if it works
2. **Check Timing** - When did ridges last use it?
3. **Wait 1 Hour** - Test again after rate limit window
4. **Contact Chutes** - Request IP whitelisting

---

**Status**: 🔍 **IP-Based Rate Limiting (Most Likely)**

**Action**: Test from ridges IP or wait for rate limit reset! 🌐⏰

