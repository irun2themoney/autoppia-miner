# 📊 Miner Activity Report

**Date**: November 22, 2025  
**UID**: 160

---

## ✅ Service Status

### **Miner Service**
- **Status**: ✅ **Running**
- **Started**: 09:25:07 UTC (today)
- **PID**: 308845
- **Memory**: 139.8M
- **Registration**: ✅ **Registered** (UID: 160)
- **Axon**: ✅ **Served** (134.199.203.133:8091)

### **API Service**
- **Status**: ✅ **Running**
- **Port**: 8080
- **Endpoint**: `/solve_task` available

---

## 🔍 Activity Analysis

### **Today's Activity**

**Validator Requests**:
- API `solve_task` calls: Check logs
- Task processing: Check logs

**Miner Activity**:
- Forward calls: Check logs
- Synapse processing: Check logs

---

## 📋 How to Check Activity

### **Real-Time Monitoring**:
```bash
# Watch miner logs
journalctl -u autoppia-miner -f

# Watch API logs
journalctl -u autoppia-api -f

# Check for validator requests
journalctl -u autoppia-api --since '1 hour ago' | grep solve_task
```

### **Activity Counts**:
```bash
# Count API requests today
journalctl -u autoppia-api --since today | grep -c solve_task

# Count miner tasks today
journalctl -u autoppia-miner --since today | grep -cE 'forward|process_task'
```

---

## 🎯 What to Look For

### **Signs of Activity**:
- ✅ `solve_task` calls in API logs
- ✅ `forward` or `process_task` in miner logs
- ✅ Validator IPs in API logs
- ✅ Task IDs in logs

### **No Activity Means**:
- ⏳ Validators haven't selected your miner yet
- ⏳ Waiting for next evaluation round
- ⏳ Normal if just started

---

## 📚 References

- [IWA Platform](https://infinitewebarena.autoppia.com/subnet36/agents) - Check agent activity
- [Taostats](https://taostats.io/subnets/36/chart) - Subnet 36 stats

