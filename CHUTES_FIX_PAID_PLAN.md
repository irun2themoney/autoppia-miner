# 🔧 Chutes API Fix for Paid Plan (5000 requests/day)

## 🐛 **Problem Identified**

### **Issue**:
- Chutes API returning **429 (Rate Limited)** errors
- Rate limiting was too aggressive for paid plan
- Consecutive 429 errors causing long backoff periods
- LLM calls not working despite having 5000 requests/day quota

### **Root Cause**:
1. **Too conservative rate limiting**: 3s between requests (20 req/min)
2. **Long backoff periods**: 60s+ waits after 429 errors
3. **No reset logic**: Rate limit state persisted even after window passed
4. **Exponential backoff too aggressive**: Up to 5 minutes wait

---

## ✅ **Fixes Applied**

### **1. Reduced Rate Limiting Interval**
- **Before**: 3 seconds between requests (20 req/min max)
- **After**: 2 seconds between requests (30 req/min max)
- **Reason**: Paid plans can handle higher per-minute rates

### **2. Reduced Backoff Wait Times**
- **Before**: 60s wait after 429 error
- **After**: 30s wait after 429 error
- **Reason**: Paid plans have higher limits, less need for long waits

### **3. Reduced Exponential Backoff**
- **Before**: 60s, 120s, 240s, 300s (max 5 minutes)
- **After**: 15s, 30s, 60s, 120s (max 2 minutes)
- **Reason**: Faster recovery for paid plans

### **4. Added Rate Limit Reset Logic**
- **New**: If 2+ minutes since last 429, reset error counter
- **Reason**: Rate limit windows typically reset after 1-2 minutes
- **Benefit**: Prevents stuck rate limit state

### **5. Less Aggressive Interval Increase**
- **Before**: Increased to 5s after successful retry
- **After**: Only increases by 0.5s, capped at 3s
- **Reason**: Paid plans can handle more requests

---

## 📊 **Expected Behavior**

### **With 5000 Requests/Day Plan**:
- **Per-minute limit**: Likely 20-30 requests/minute
- **Daily limit**: 5000 requests (about 3.5 req/min average)
- **Rate limiting**: 2s between requests (30 req/min max)
- **Backoff**: 30s after 429, then 15s, 30s, 60s, 120s max

### **When Rate Limited**:
1. Wait 30s (reduced from 60s)
2. Retry request
3. If still rate limited, wait 15s, 30s, 60s, 120s (reduced from 60s, 120s, 240s, 300s)
4. After 2 minutes, reset error counter (new)

---

## 🧪 **Testing**

### **To Verify It's Working**:

1. **Check Logs**:
   ```bash
   journalctl -u autoppia-api -f | grep -E "Chutes|LLM|429"
   ```

2. **Monitor Success**:
   - Watch for successful LLM calls
   - Check for reduced 429 errors
   - Verify faster recovery from rate limits

3. **Test Directly**:
   ```bash
   cd /opt/autoppia-miner
   python3 test_chutes_direct.py
   ```

---

## 🎯 **Next Steps**

1. **Wait for Rate Limit Reset**:
   - If currently rate limited, wait 1-2 minutes
   - Rate limit windows typically reset after 60-120 seconds

2. **Monitor Performance**:
   - Watch dashboard for LLM usage
   - Check logs for successful API calls
   - Track success rate improvement

3. **If Still Rate Limited**:
   - Check Chutes dashboard for actual usage
   - Verify API key is correct
   - Contact Chutes support if needed

---

## 📝 **Configuration Summary**

| Setting | Before | After | Reason |
|---------|--------|-------|--------|
| Request Interval | 3s | 2s | Paid plan can handle more |
| 429 Wait Time | 60s | 30s | Faster recovery |
| Max Backoff | 300s (5min) | 120s (2min) | Less aggressive |
| Reset Window | Never | 120s | Auto-recover from stuck state |
| Interval Increase | +2s (to 5s) | +0.5s (max 3s) | Less conservative |

---

**Status**: ✅ **Rate Limiting Optimized for Paid Plan**

**Action**: Wait 1-2 minutes for rate limit to reset, then test again! 🚀

