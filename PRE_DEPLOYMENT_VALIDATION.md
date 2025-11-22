# ✅ Pre-Deployment Validation Guide

## 🎯 **Purpose**

Ensure your miner is correctly configured and ready for validators **BEFORE** deployment. This prevents issues and saves time.

---

## 🚀 **Quick Start**

### **1. Run Full Validation**
```bash
python3 scripts/validate_before_deployment.py
```

This checks:
- ✅ Environment & configuration
- ✅ Wallet setup
- ✅ Network registration
- ✅ API endpoint accessibility
- ✅ Port availability
- ✅ Miner code validation
- ✅ IP detection
- ✅ Validator request simulation

### **2. Run Local Miner Test**
```bash
python3 scripts/test_miner_locally.py
```

This tests:
- ✅ Miner can start and register
- ✅ API endpoint works correctly

---

## 📋 **What Gets Checked**

### **1. Environment & Configuration** ✅
- Subnet UID: Must be 36
- Network: Must be "finney"
- API Port: Must be 8080
- Axon Port: Must be 8091
- API URL: Should match deployment server

### **2. Wallet Configuration** ✅
- Wallet can be loaded
- Wallet has balance (for registration)
- Wallet is accessible

### **3. Network Registration** ✅
- Miner is registered on the network
- UID is found in metagraph
- Axon port matches configuration
- Axon IP is set correctly

### **4. API Endpoint** ✅
- Health endpoint responds
- solve_task endpoint is accessible
- CORS headers are correct

### **5. Port Availability** ✅
- API port (8080) is available
- Axon port (8091) is available

### **6. Miner Code Validation** ✅
- `bt.axon()` is called correctly
- `serve_axon()` is called
- Axon port is configured
- External IP is set
- **NO `external_port` parameter** (critical!)

### **7. IP Detection** ✅
- IP detection methods work
- Can detect public IP

### **8. Validator Request Simulation** ✅
- API can process a test request
- Response format is correct
- Actions are generated

---

## ✅ **Expected Output**

### **All Checks Pass:**
```
✅ All critical checks passed!
ℹ️  Your miner is ready for deployment
ℹ️  Validators should be able to connect once deployed
```

### **Issues Found:**
```
❌ Found 2 issue(s) that need attention:
  1. Axon port is 8080, should be 8091
  2. Miner not registered - run registration first

⚠️  Please fix these issues before deployment
```

---

## 🔧 **Common Issues & Fixes**

### **Issue: Miner Not Registered**
**Fix:**
```bash
btcli subnet register --netuid 36 --wallet.name default --wallet.hotkey default
```

### **Issue: Axon Port Mismatch**
**Fix:** Check `config/settings.py` - `axon_port` should be 8091

### **Issue: external_port Parameter Found**
**Fix:** Remove `external_port=settings.api_port` from `bt.axon()` call in `miner/miner.py`

### **Issue: API Not Accessible**
**Fix:** 
- Ensure API service is running
- Check firewall rules
- Verify API URL in settings

---

## 🎯 **Before Deployment Checklist**

Run validation and ensure:
- [ ] All validation checks pass
- [ ] Miner is registered (UID found)
- [ ] Axon port is 8091 (not 8080)
- [ ] API port is 8080
- [ ] No `external_port` in `bt.axon()`
- [ ] Wallet has balance
- [ ] API endpoint is accessible
- [ ] IP detection works

---

## 🚀 **Deployment Workflow**

1. **Run Validation:**
   ```bash
   python3 scripts/validate_before_deployment.py
   ```

2. **Fix Any Issues:**
   - Address all errors and warnings
   - Re-run validation until all pass

3. **Deploy:**
   - Deploy code to server
   - Start services
   - Verify services are running

4. **Post-Deployment Check:**
   - Check dashboard: `http://YOUR_IP:8080/api/dashboard`
   - Verify miner is registered on metagraph
   - Monitor for validator connections

---

## 💡 **Pro Tips**

1. **Run validation before every deployment** - catches issues early
2. **Fix all errors** - warnings can be ignored if you understand them
3. **Test locally first** - use `test_miner_locally.py` if possible
4. **Check metagraph** - verify your miner appears correctly
5. **Monitor logs** - watch for errors after deployment

---

## 📊 **Validation Script Output**

The script provides:
- ✅ **Green checkmarks**: Everything is correct
- ⚠️ **Yellow warnings**: May need attention
- ❌ **Red errors**: Must be fixed before deployment
- ℹ️ **Blue info**: Informational messages

---

**Status: ✅ VALIDATION TOOLS READY**

Run `python3 scripts/validate_before_deployment.py` before every deployment to ensure validators can connect!

