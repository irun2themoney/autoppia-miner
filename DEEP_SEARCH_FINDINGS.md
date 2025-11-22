# 🔍 Deep Search Findings - Critical Discovery

## 🎯 **Key Finding: Missing Axon Metadata**

### **The Problem**

Your documentation repeatedly states:
- "Validators read axon metadata (your API URL, IP, port)"
- "Gets your API URL from miner metadata (axon endpoint)"
- "The axon exposes metadata that validators read to find your API endpoint"

**BUT** your current code does NOT set any metadata:

```python
# Current code (miner/miner.py line 243-247)
self.axon = bt.axon(
    wallet=self.wallet,
    port=self.config.axon.port,  # 8091
    ip=external_ip,  # 134.199.203.133
)
# ❌ NO METADATA SET!
```

---

## 🔍 **What Validators Need**

Based on the ApifiedWebAgent pattern:
1. Validators discover your miner via metagraph ✅ (working)
2. Validators need to know your **API endpoint URL** ❓ (missing!)
3. Validators call `POST http://134.199.203.133:8080/solve_task` (can't if they don't know the URL)

**The Issue**: Validators see your axon at `134.199.203.133:8091`, but they need to know your API is at `http://134.199.203.133:8080`.

---

## 💡 **Possible Solutions**

### **Solution 1: Add Axon Metadata** (Most Likely Fix)

Bittensor axons may support metadata that validators can read. We need to check if we can add:

```python
self.axon = bt.axon(
    wallet=self.wallet,
    port=self.config.axon.port,
    ip=external_ip,
    # TODO: Add metadata if supported
    # metadata={
    #     "api_url": f"http://{external_ip}:{settings.api_port}",
    #     "api_endpoint": "/solve_task",
    #     "api_version": "1.0.0"
    # }
)
```

### **Solution 2: Use Convention** (If metadata not supported)

Validators might assume:
- API is on port 8080 (standard)
- They infer: `http://{axon_ip}:8080/solve_task`

This should work IF validators use this convention.

### **Solution 3: Synapse Method** (Fallback)

Validators send synapse to axon (port 8091), miner forwards to API internally. This should work but we're not seeing synapses.

---

## 📊 **What We Need to Verify**

1. **Does Bittensor axon support metadata?**
   - Check Bittensor documentation
   - Check official Autoppia miner examples
   - Check if `bt.axon()` accepts metadata parameter

2. **How do validators actually discover API URLs?**
   - Check Autoppia validator code
   - Check official miner examples
   - Check if they use convention or metadata

3. **Are validators trying to connect?**
   - Check for connection attempts to port 8091 (synapses)
   - Check for connection attempts to port 8080 (API calls)
   - Monitor network activity

---

## 🚀 **Recommended Action**

1. **Check Bittensor axon API** for metadata support
2. **Check official Autoppia miner examples** to see how they set metadata
3. **If metadata is supported, add it** to expose API URL
4. **If not supported, verify convention** (port 8080 assumption)

---

## 📝 **Next Steps**

1. Review Bittensor axon documentation
2. Check Autoppia GitHub repos for miner examples
3. Add metadata if supported
4. Test and verify validators can discover API URL

---

**Status**: ⚠️ **Potential missing configuration - axon metadata not set**

**Impact**: Validators may not be able to discover your API endpoint URL

**Priority**: HIGH - This could be preventing validator connections

