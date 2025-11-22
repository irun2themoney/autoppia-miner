# 🔍 DigitalOcean Server Diagnosis

**Server IP**: `134.199.203.133`  
**Date**: $(date)

---

## ✅ What's Working

1. **Server is Reachable**: ✅ Ping successful
2. **API Health**: ✅ Responding correctly
   - Status: `healthy`
   - Version: `1.0.0`
   - Agent Type: `hybrid`

---

## 🔍 What We Need to Check on the Server

Since this is a **DigitalOcean server**, we need to SSH in to check:

### 1. Check Miner Status
```bash
ssh root@134.199.203.133
systemctl status autoppia-miner
```

### 2. Check Miner Logs
```bash
journalctl -u autoppia-miner -n 100 | grep -i "uid\|registered\|served\|axon"
```

### 3. Check Wallet Configuration
```bash
# On server, check .env
cat /opt/autoppia-miner/.env | grep WALLET
```

### 4. Check Registration
```bash
# On server
btcli subnet show --netuid 36 --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY
```

### 5. Check if Axon is Served
```bash
# On server
journalctl -u autoppia-miner | grep -i "served to.*network\|serve_axon"
```

### 6. Check Recent Validator Activity
```bash
# On server
journalctl -u autoppia-miner --since "1 hour ago" | grep -i "processing task\|validator\|synapse"
```

---

## 🎯 Most Likely Issues

Based on the documentation, your server was working before. The most likely issues are:

1. **Miner Service Stopped** - May have crashed or been stopped
2. **Wallet Configuration Missing** - `.env` on server may not have wallet credentials
3. **Registration Issue** - Miner may not be registered or lost registration
4. **IP Detection Issue** - Miner may be using wrong IP (0.0.0.0)

---

## 🔧 Quick Fixes

### Fix 1: Restart Services
```bash
ssh root@134.199.203.133
systemctl restart autoppia-api
systemctl restart autoppia-miner
journalctl -u autoppia-miner -f  # Watch for errors
```

### Fix 2: Check Wallet Config
```bash
ssh root@134.199.203.133
cd /opt/autoppia-miner
cat .env | grep WALLET
# If missing, add:
# WALLET_NAME=your_wallet
# WALLET_HOTKEY=your_hotkey
```

### Fix 3: Verify Registration
```bash
ssh root@134.199.203.133
btcli subnet show --netuid 36 --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY
```

### Fix 4: Check IP Detection
```bash
ssh root@134.199.203.133
journalctl -u autoppia-miner | grep "Final external IP"
# Should show: 134.199.203.133 (not 0.0.0.0)
```

---

## 📋 Action Plan

1. **SSH into server**:
   ```bash
   ssh root@134.199.203.133
   ```

2. **Check miner status**:
   ```bash
   systemctl status autoppia-miner
   ```

3. **Check logs for errors**:
   ```bash
   journalctl -u autoppia-miner -n 100
   ```

4. **Check if miner is registered**:
   ```bash
   journalctl -u autoppia-miner | grep -i "uid\|registered"
   ```

5. **Check if axon is served**:
   ```bash
   journalctl -u autoppia-miner | grep -i "served to.*network"
   ```

---

## 🎯 Why Validators Aren't Connecting

**Most likely reasons**:

1. **Miner service not running** - Check with `systemctl status autoppia-miner`
2. **Miner not registered** - Check UID in logs
3. **Axon not served** - Check for "served to network" message
4. **Wrong IP** - Check if IP is 0.0.0.0 instead of 134.199.203.133
5. **Wallet config missing** - Check `.env` on server

---

## ✅ Next Steps

1. **SSH into server and run diagnostics**:
   ```bash
   ssh root@134.199.203.133
   cd /opt/autoppia-miner
   ./scripts/diagnose_validator_connection.sh
   ```

2. **Or check manually**:
   ```bash
   ssh root@134.199.203.133
   systemctl status autoppia-miner
   journalctl -u autoppia-miner -n 50
   ```

3. **Fix any issues found** and restart services

---

**Status**: ⚠️ **Need to check server directly** - API is working, but miner status unknown

