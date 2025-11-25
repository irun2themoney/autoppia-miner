# 📊 Monitoring Plan - Post Critical Fix Deployment

## ✅ What We've Accomplished

**Critical Fix**: Protocol naming conventions (camelCase compliance)  
**Status**: ✅ Implemented and tested  
**Impact**: Validator's Pydantic model should now accept responses

---

## 🎯 Expected Timeline

### Immediate (After Deployment)
- ✅ Response times: < 3.0s (ideally < 1.5s)
- ✅ IWA Validation: ✅ VALID for all TaskSynapses
- ✅ Protocol compliance: All actions use camelCase

### 30-90 Minutes After Deployment (1-2 Tempo Periods)
- 🎯 **First Confirmation**: Incentive > 0.000000τ
- **Meaning**: Validator successfully parsed, executed, and scored actions as non-zero
- **Action**: Monitor on-chain status every 15-30 minutes

### 1-2 Hours After Incentive Updates
- 🎯 **Final Confirmation**: Active Status = 1
- **Meaning**: UID is no longer eligible for pruning
- **Action**: Continue monitoring for stability

---

## 📊 Monitoring Checklist

### 1. Log Monitoring (Immediate)

**Check Response Times**:
```bash
journalctl -u autoppia-miner -f | grep -E 'TASK_RESPONSE|Time:'
```

**Expected**:
```
📤 TASK_RESPONSE: {validator_ip} - Completed TaskSynapse | Success: True | Actions: 5 | Time: 0.96s | IWA: ✅ VALID
```

**Warning Signs**:
```
⚠️ SLOW_RESPONSE: Task took 4.5s (validators may timeout)
```

### 2. IWA Validation (Immediate)

**Check Validation Status**:
```bash
journalctl -u autoppia-miner -f | grep -E 'IWA_VALIDATION|IWA:'
```

**Expected**:
```
✅ IWA Validation Passed: 5 actions valid
📤 TASK_RESPONSE: ... | IWA: ✅ VALID
```

**Warning Signs**:
```
❌ IWA_VALIDATION_FAILED: Invalid action format detected
```

### 3. On-Chain Status (Every 15-30 Minutes)

**Check Incentive**:
```bash
python3 scripts/check_onchain_status.py
```

**Expected**:
```
--- CRITICAL METRICS ---
Active Status: 0 (will update after incentive)
Incentive: 0.000123τ ✅ (non-zero!)
Emissions: 0.000045τ ✅ (non-zero!)
```

**Success Indicator**:
```
🎯 INCENTIVE DETECTED! Active status update is imminent.
```

### 4. Active Status (1-2 Hours After Incentive)

**Check Active Status**:
```bash
python3 scripts/check_onchain_status.py
```

**Expected**:
```
--- CRITICAL METRICS ---
Active Status: 1 ✅ (ACTIVE!)
Incentive: 0.000456τ ✅
Emissions: 0.000123τ ✅
```

---

## ⚠️ Troubleshooting: If Incentive Still Zero After 2 Hours

If after 2 tempo cycles (≈2 hours) incentive remains 0.000000τ, the issue is likely:

### 1. Execution Failure
**Symptom**: Actions are syntactically correct but fail when executed  
**Check**: Review validator logs (if available) or test actions manually  
**Action**: Improve selector accuracy, add more fallback strategies

### 2. Validator Timeout
**Symptom**: Response times > 3-4 seconds  
**Check**: Monitor response time logs  
**Action**: Further optimize browser automation, reduce DOM analysis time

### 3. Minimal Score
**Symptom**: Valid actions but too simple/repetitive  
**Check**: Review action sequences (are they just ScreenshotActions?)  
**Action**: Improve action generation quality, reduce fallback usage

---

## 🎯 Success Indicators

### ✅ Protocol Compliance (Achieved)
- ✅ camelCase naming conventions
- ✅ Valid IWA format
- ✅ Proper field names (timeSeconds, caseSensitive, webAgentId, taskType)

### ✅ Performance (Achieved)
- ✅ Browser caching (saves 2-4s per request)
- ✅ Response times < 1.5s (average 0.9s)
- ✅ Fast page loading (domcontentloaded)

### 🔄 Monitoring (In Progress)
- 🔄 Validator acceptance (incentive > 0)
- 🔄 Active Status update (Active = 1)
- 🔄 Emissions increase

---

## 📝 Monitoring Commands

### Quick Status Check:
```bash
python3 scripts/check_onchain_status.py
```

### Monitor Logs:
```bash
journalctl -u autoppia-miner -f | grep -E 'TASK_RESPONSE|IWA_VALIDATION|INCENTIVE|ON-CHAIN STATUS'
```

### Check Recent Activity:
```bash
journalctl -u autoppia-miner --since '10 minutes ago' | grep -E 'TASK_RESPONSE|IWA'
```

---

## 🎉 What Success Looks Like

**Logs**:
```
📤 TASK_RESPONSE: 192.168.1.1 - Completed TaskSynapse | Success: True | Actions: 5 | Time: 0.96s | IWA: ✅ VALID
--- ON-CHAIN STATUS --- | Active: 0 | Last Update: 4959923 | Incentive: 0.000123τ | Emissions: 0.000045τ
🎯 INCENTIVE DETECTED! Active status update is imminent.
```

**On-Chain**:
```
--- CRITICAL METRICS ---
Active Status: 1 ✅
Incentive: 0.000456τ ✅
Emissions: 0.000123τ ✅
```

---

## 💡 Next Steps

1. ✅ **Deploy Fixed Code** - Deploy camelCase fixes to production
2. 🔄 **Monitor Logs** - Watch for IWA: ✅ VALID and response times
3. 🔄 **Check On-Chain** - Monitor incentive every 15-30 minutes
4. ⏰ **Wait 1-2 Hours** - Allow time for validator evaluation
5. 🎯 **Verify Active Status** - Confirm Active Status = 1

---

**Status**: ✅ Critical fixes complete, monitoring phase  
**Timeline**: 30-90 min for incentive, 1-2 hours for Active Status  
**Goal**: See incentive > 0, then Active Status = 1

