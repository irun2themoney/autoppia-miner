# 🔍 Chutes API Diagnosis - 429 Rate Limit Issues

## 🐛 **Current Problem**

### **Symptoms**:
- ✅ ChutesAgent is properly configured
- ✅ API key is set correctly
- ✅ API endpoint is correct
- ❌ **Getting 429 (Rate Limited) errors immediately**
- ❌ LLM calls not working despite 5000 requests/day plan

### **Test Results**:
```
Status: 429
Response: <html><head><title>429 Too Many Requests</title></head>...
```

Even after waiting 60+ seconds, still getting 429 errors.

---

## 🤔 **Possible Causes**

### **1. Per-Minute Rate Limits (Most Likely)**
- **Issue**: Chutes API has **separate per-minute limits** from daily limits
- **Example**: 5000/day but only 10-20 requests/minute
- **Impact**: Even with 5000/day, you can't make requests too quickly
- **Solution**: Need to know actual per-minute limit

### **2. API Key Already Rate Limited**
- **Issue**: API key might be rate limited from previous testing
- **Impact**: Rate limit window hasn't reset yet
- **Solution**: Wait longer (5-10 minutes) or check Chutes dashboard

### **3. Account-Level Rate Limits**
- **Issue**: Rate limits might be at account level, not just API key
- **Impact**: Multiple API keys or previous usage affecting limits
- **Solution**: Check Chutes dashboard for account usage

### **4. Different Rate Limits for Different Models**
- **Issue**: Free models (Qwen) might have stricter limits than paid models
- **Impact**: Using Qwen/Qwen2.5-7B-Instruct might have lower limits
- **Solution**: Try a different model or check model-specific limits

---

## 🔧 **What We've Fixed**

### **1. Reduced Rate Limiting** ✅
- Changed from 3s to 2s between requests
- Reduced backoff times (30s instead of 60s)
- Reduced max backoff (2min instead of 5min)

### **2. Added Reset Logic** ✅
- Auto-resets error counter after 2 minutes
- Prevents stuck rate limit state

### **3. Better Error Handling** ✅
- Faster recovery from rate limits
- Less aggressive backoff for paid plans

---

## 🎯 **What to Check**

### **1. Chutes Dashboard**
- Check your actual usage: https://chutes.ai/dashboard (or similar)
- See if you're hitting per-minute limits
- Check if there are any account-level restrictions

### **2. API Key Status**
- Verify API key is active
- Check if key has been rate limited
- See if there are any key-specific limits

### **3. Per-Minute Limits**
- Daily limit: 5000 requests/day ✅
- Per-minute limit: **UNKNOWN** ❓
- Need to find actual per-minute limit

---

## 💡 **Recommendations**

### **Immediate Actions**:

1. **Check Chutes Dashboard**:
   - Log into your Chutes account
   - Check current usage and limits
   - See if there are per-minute restrictions

2. **Wait Longer**:
   - Rate limit windows typically reset after 1-5 minutes
   - Wait 5-10 minutes and test again
   - Per-minute limits usually reset every 60 seconds

3. **Try Different Model**:
   - Current: `Qwen/Qwen2.5-7B-Instruct` (free model)
   - Try: `gpt-4o-mini` or `gpt-3.5-turbo` (paid models might have different limits)

4. **Contact Chutes Support**:
   - Ask about per-minute rate limits for your plan
   - Verify API key status
   - Check if there are any account restrictions

---

## 🔄 **Next Steps**

1. **Wait 5-10 minutes** for rate limit to reset
2. **Check Chutes dashboard** for actual limits
3. **Test again** with updated rate limiting
4. **Monitor logs** for successful LLM calls
5. **Adjust rate limiting** based on actual limits

---

## 📊 **Current Configuration**

- **Request Interval**: 2 seconds (30 req/min max)
- **429 Wait Time**: 30 seconds
- **Max Backoff**: 120 seconds (2 minutes)
- **Reset Window**: 120 seconds (auto-reset)

---

**Status**: ⚠️ **Rate Limited - Need to Verify Actual Limits**

**Action**: Check Chutes dashboard and wait for rate limit to reset! 🔍

