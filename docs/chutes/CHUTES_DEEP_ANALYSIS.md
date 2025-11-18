# 🔍 Deep Analysis: Chutes API Rate Limiting Issue

## 📊 **Findings from Official Documentation**

Based on official Chutes documentation and web search:

### **Key Insights**:

1. **Separate Rate Limits**:
   - ✅ **Daily quota**: 5000 requests/day (confirmed)
   - ⚠️ **Per-minute limits**: Separate from daily quota (UNKNOWN exact number)
   - ⚠️ **Per-hour limits**: May also exist (UNKNOWN)
   - ⚠️ **Burst limits**: Concurrent request limits may apply

2. **Rate Limit Headers** (Standard Practice):
   - `Retry-After`: Tells you how long to wait
   - `X-RateLimit-Limit`: Maximum requests allowed
   - `X-RateLimit-Remaining`: Requests remaining in window
   - `X-RateLimit-Reset`: When the limit resets

3. **Best Practices** (From Official Docs):
   - Check `Retry-After` header when getting 429
   - Implement exponential backoff
   - Monitor rate limit headers
   - Handle 429 errors gracefully

---

## 🐛 **Current Problem**

### **Symptoms**:
- ✅ API key is valid
- ✅ Endpoint is correct (`/v1/chat/completions`)
- ✅ Headers are correct (`X-API-Key`)
- ❌ **Getting 429 immediately** on every request
- ❌ **No successful LLM calls** since deployment

### **Timeline**:
- **6:03-6:13 AM**: Multiple 429 errors with exponential backoff
- **Since then**: No LLM calls attempted (likely due to rate limit state)

---

## 🔍 **Root Cause Analysis**

### **Possible Causes**:

1. **Per-Minute Limit Exceeded** (Most Likely)
   - During testing, we made many requests quickly
   - Hit per-minute limit (likely 10-20 req/min)
   - Rate limit window hasn't reset yet

2. **Burst Limit** (Possible)
   - Multiple concurrent requests
   - Chutes may limit concurrent connections
   - Need to ensure sequential requests

3. **Account-Level Rate Limit** (Possible)
   - API key might be shared/used elsewhere
   - Account-level limits might be stricter
   - Need to check Chutes dashboard

4. **Model-Specific Limits** (Possible)
   - Free models (Qwen) might have stricter limits
   - Paid models might have higher limits
   - Need to verify model-specific limits

---

## ✅ **What We've Fixed**

### **1. Added Retry-After Header Support** ✅
- Now checks `Retry-After` header from Chutes API
- Uses header value if provided (official recommendation)
- Falls back to exponential backoff if no header

### **2. Added Rate Limit Header Tracking** ✅
- Tracks `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- Logs rate limit info for debugging
- Can adjust behavior based on headers

### **3. Reduced Initial Rate Limiting** ✅
- Changed from 2s to 1s between requests (60 req/min)
- Will adjust based on actual rate limit headers
- More aggressive for paid plans

### **4. Better Reset Logic** ✅
- Auto-resets error counter after 2 minutes
- Prevents stuck rate limit state
- Faster recovery

---

## 🎯 **What to Check**

### **1. Chutes Dashboard** (CRITICAL)
- Log into your Chutes account
- Check current usage and limits
- See if there are per-minute restrictions
- Verify API key status

### **2. Rate Limit Headers** (IMPORTANT)
- Run `test_chutes_headers.py` to see headers
- Check `Retry-After` value
- Check `X-RateLimit-*` headers
- Use these to adjust rate limiting

### **3. Wait for Reset** (NECESSARY)
- Per-minute limits typically reset every 60 seconds
- Wait 5-10 minutes for rate limit to fully reset
- Test again after waiting

---

## 📋 **Action Plan**

### **Immediate**:
1. ✅ Added Retry-After header support
2. ✅ Added rate limit header tracking
3. ⏳ **Wait 5-10 minutes** for rate limit to reset
4. ⏳ **Test with headers script** to see actual limits

### **Short-Term**:
1. Check Chutes dashboard for actual limits
2. Adjust rate limiting based on headers
3. Monitor for successful LLM calls
4. Optimize based on actual limits

### **Long-Term**:
1. Implement dynamic rate limiting based on headers
2. Track rate limit usage over time
3. Optimize request patterns
4. Consider using paid models if free models have stricter limits

---

## 🔧 **Next Steps**

1. **Run Header Test**:
   ```bash
   cd /opt/autoppia-miner
   python3 test_chutes_headers.py
   ```
   This will show us the actual rate limit headers.

2. **Wait for Reset**:
   - Wait 5-10 minutes
   - Rate limit windows typically reset every 60 seconds

3. **Check Dashboard**:
   - Log into Chutes account
   - Check usage and limits
   - Verify API key status

4. **Monitor Logs**:
   - Watch for successful LLM calls
   - Check rate limit header values
   - Adjust based on actual limits

---

**Status**: 🔍 **Investigating - Need to Check Headers and Dashboard**

**Action**: Run header test and check Chutes dashboard! 📊

