# 🔒 Service Reliability & Connection Stability

## ✅ **Current Configuration**

### **Auto-Restart Settings:**
- **Restart Policy**: `always` - Services restart automatically if they crash
- **Restart Delay**: `10 seconds` - Waits 10 seconds before restarting
- **Start Limit**: 5 restarts per 5 minutes (prevents restart loops)
- **Enabled on Boot**: Services start automatically when server reboots

### **Service Dependencies:**
- **Miner depends on API**: Miner waits for API to start first
- **Network dependency**: Services wait for network to be online

---

## 🛡️ **Reliability Features Added**

### **1. Enhanced Service Configuration** ✅
- **KillMode=mixed**: Graceful shutdown with fallback
- **TimeoutStopSec=30**: 30 seconds for graceful shutdown
- **StartLimitInterval=300**: Rate limiting (5 restarts per 5 minutes)
- **StartLimitBurst=5**: Maximum restart attempts

### **2. Health Check Timer** ✅
- **Frequency**: Every 5 minutes
- **Checks**: Both API and miner services
- **Action**: Auto-restarts if services are down
- **Logging**: All checks logged to `/var/log/autoppia-health-check.log`

### **3. Keep-Alive Settings** ✅
- **API**: `--timeout-keep-alive 75` - Keeps connections alive
- **Prevents**: Connection timeouts and disconnections

---

## 📊 **Monitoring & Verification**

### **Check Service Status:**
```bash
systemctl status autoppia-miner
systemctl status autoppia-api
```

### **Check Auto-Restart Configuration:**
```bash
systemctl show autoppia-miner --property=Restart,RestartSec
systemctl show autoppia-api --property=Restart,RestartSec
```

### **Check Health Check Timer:**
```bash
systemctl status autoppia-health-check.timer
systemctl list-timers | grep autoppia
```

### **View Health Check Logs:**
```bash
tail -f /var/log/autoppia-health-check.log
```

---

## 🔄 **What Happens If Services Crash**

### **Automatic Recovery:**
1. **Service crashes** → Systemd detects failure
2. **Wait 10 seconds** → RestartSec delay
3. **Auto-restart** → Service starts again
4. **Health check** → Timer verifies every 5 minutes
5. **If still down** → Health check script restarts it

### **Rate Limiting:**
- **Max 5 restarts** in 5 minutes
- **Prevents restart loops** if there's a persistent issue
- **Logs warnings** if limit is reached

---

## 🚀 **Boot Behavior**

### **On Server Reboot:**
1. **Network comes online**
2. **API service starts** (enabled on boot)
3. **Miner service starts** (after API, enabled on boot)
4. **Health check timer starts** (enabled on boot)
5. **All services running** within ~30 seconds

---

## 📈 **Connection Stability**

### **Prevents Disconnections:**
- ✅ **Auto-restart on crash**
- ✅ **Health check monitoring**
- ✅ **Keep-alive connections**
- ✅ **Graceful shutdown handling**
- ✅ **Network dependency management**

### **Maintains Uptime:**
- ✅ **Services restart automatically**
- ✅ **Start on server boot**
- ✅ **Monitor and recover from failures**
- ✅ **Rate limiting prevents loops**

---

## 🎯 **Current Status**

### **Services:**
- ✅ **Miner**: Active, auto-restart enabled
- ✅ **API**: Active, auto-restart enabled
- ✅ **Health Check**: Timer active, runs every 5 minutes

### **Reliability:**
- ✅ **Auto-restart**: Configured
- ✅ **Boot on start**: Enabled
- ✅ **Health monitoring**: Active
- ✅ **Connection stability**: Optimized

---

## 💡 **Best Practices**

1. **Monitor Logs Regularly:**
   ```bash
   journalctl -u autoppia-miner -f
   journalctl -u autoppia-api -f
   ```

2. **Check Health Check Logs:**
   ```bash
   tail -f /var/log/autoppia-health-check.log
   ```

3. **Verify Services After Updates:**
   ```bash
   systemctl status autoppia-miner autoppia-api
   ```

4. **Monitor Dashboard:**
   - Check uptime regularly
   - Watch for connection issues
   - Monitor validator activity

---

**Status: ✅ SERVICES CONFIGURED FOR MAXIMUM RELIABILITY**

Your miner will stay connected and automatically recover from any issues!

