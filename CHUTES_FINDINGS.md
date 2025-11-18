# 🔍 Chutes API Deep Search Findings

## 🎯 **Critical Discovery**

### **Test Results**:
```
Status: 429
Retry-After: Not provided ❌
X-RateLimit-Limit: Not provided ❌
X-RateLimit-Remaining: Not provided ❌
X-RateLimit-Reset: Not provided ❌
Response: <html><title>429 Too Many Requests</title><hr><center>nginx</center>
```

### **Key Finding**:
- **Chutes API does NOT provide rate limit headers** (Retry-After, X-RateLimit-*)
- **Rate limiting is at nginx level** (infrastructure, not application)
- **No way to know when limit resets** from API response
- **Must rely on time-based backoff** (wait and retry)

---

## 📊 **What Official Docs Say**

### **From Chutes Documentation**:
1. **Rate Limiting Exists**: Confirmed per-minute and per-hour limits separate from daily quota
2. **No Specific Numbers**: Docs don't specify exact limits for paid plans
3. **Best Practices**: Recommend exponential backoff and checking Retry-After header
4. **Problem**: Chutes doesn't actually provide Retry-After header! ❌

### **Standard Practice** (What We Expected):
- APIs usually provide `Retry-After` header
- APIs usually provide `X-RateLimit-*` headers
- These help clients know when to retry

### **Chutes Reality** (What We Found):
- ❌ No `Retry-After` header
- ❌ No `X-RateLimit-*` headers
- ✅ Rate limiting happens at nginx level
- ✅ Must use time-based backoff

---

## 🐛 **Root Cause**

### **Why It's Not Working**:

1. **Rate Limited at Infrastructure Level**:
   - nginx is blocking requests before they reach Chutes API
   - No application-level rate limit info available
   - Must wait for nginx rate limit window to reset

2. **No Rate Limit Information**:
   - Can't tell when limit resets
   - Can't tell how many requests remaining
   - Must guess based on time

3. **Per-Minute Limits** (Likely):
   - During testing, we made many requests quickly
   - Hit per-minute limit (likely 10-20 req/min)
   - Rate limit window hasn't reset yet

---

## ✅ **What We've Fixed**

### **1. Added Retry-After Support** ✅
- Checks for `Retry-After` header (even though Chutes doesn't provide it)
- Falls back to exponential backoff if no header
- Ready for when Chutes adds header support

### **2. Added Rate Limit Header Tracking** ✅
- Tracks `X-RateLimit-*` headers (even though Chutes doesn't provide them)
- Logs rate limit info for debugging
- Ready for when Chutes adds header support

### **3. Improved Exponential Backoff** ✅
- Reduced wait times for paid plans (30s instead of 60s)
- Reduced max backoff (2min instead of 5min)
- Auto-resets after 2 minutes

### **4. Better Reset Logic** ✅
- Auto-resets error counter after 2 minutes
- Prevents stuck rate limit state
- Faster recovery

---

## 🎯 **What You Need to Do**

### **1. Check Chutes Dashboard** (CRITICAL) 🔴
- Log into your Chutes account
- Check current usage and limits
- See if there are per-minute restrictions
- Verify API key status
- **This is the ONLY way to know actual limits!**

### **2. Wait for Rate Limit Reset** (NECESSARY) ⏳
- Per-minute limits typically reset every 60 seconds
- Wait **5-10 minutes** for rate limit to fully reset
- nginx rate limit windows are usually 60 seconds

### **3. Contact Chutes Support** (RECOMMENDED) 📧
- Ask about per-minute rate limits for your plan
- Ask why rate limit headers aren't provided
- Request that they add `Retry-After` header support
- Verify your API key status

---

## 📋 **Action Plan**

### **Immediate**:
1. ✅ Added Retry-After header support (ready for future)
2. ✅ Added rate limit header tracking (ready for future)
3. ✅ Improved exponential backoff
4. ⏳ **Wait 5-10 minutes** for rate limit to reset
5. ⏳ **Check Chutes dashboard** for actual limits

### **Short-Term**:
1. Contact Chutes support about rate limits
2. Monitor for successful LLM calls after reset
3. Adjust rate limiting based on dashboard info
4. Optimize request patterns

### **Long-Term**:
1. Implement dynamic rate limiting based on actual limits
2. Track rate limit usage over time
3. Optimize request patterns
4. Consider using paid models if free models have stricter limits

---

## 🔧 **Current Configuration**

- **Request Interval**: 1s between requests (60 req/min max)
- **429 Wait Time**: 30 seconds (reduced from 60s)
- **Max Backoff**: 120 seconds (2 minutes, reduced from 5)
- **Reset Window**: 120 seconds (auto-reset after 2 min)
- **Retry-After Support**: ✅ Ready (but Chutes doesn't provide it)

---

## 💡 **Recommendations**

### **1. Wait Longer**:
- Wait **10-15 minutes** (not just 5-10)
- nginx rate limits might have longer windows
- Better safe than sorry

### **2. Check Dashboard**:
- **This is critical** - only way to know actual limits
- See if you're hitting per-minute limits
- Verify API key is active

### **3. Contact Support**:
- Ask about rate limits
- Request header support
- Get clarification on limits

### **4. Consider Alternatives**:
- Use paid models (might have higher limits)
- Reduce request frequency
- Implement better caching

---

**Status**: 🔍 **Found Root Cause - No Rate Limit Headers from Chutes**

**Action**: Check Chutes dashboard and wait 10-15 minutes! 📊⏳

