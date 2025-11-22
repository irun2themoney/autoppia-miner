# 🔍 Validator Connection Diagnosis Report

**Date**: $(date)
**Location**: Local Development Machine (macOS)

---

## ✅ What's Working

1. **API Server**: ✅ Running on port 8080
   - Process ID: 85839
   - Status: Active and responding
   - Health endpoint: Accessible

2. **Python Environment**: ✅ Configured
   - Python: 3.13.3
   - Bittensor: 9.12.0

3. **Configuration File**: ✅ .env exists

---

## ❌ Critical Issues Found

### Issue 1: Wallet Configuration Missing ⚠️ **CRITICAL**

**Problem**: `WALLET_NAME` and `WALLET_HOTKEY` are not set in `.env`

**Impact**: Miner cannot register on subnet 36 without wallet configuration.

**Fix Required**:
```bash
# Edit .env file and add:
WALLET_NAME=your_wallet_name
WALLET_HOTKEY=your_hotkey_name
```

**To check if you have a wallet**:
```bash
btcli wallet list
```

**To create a wallet** (if needed):
```bash
btcli wallet create --wallet.name your_wallet_name
btcli wallet new_hotkey --wallet.name your_wallet_name --wallet.hotkey your_hotkey_name
```

---

### Issue 2: Miner Not Running ⚠️ **CRITICAL**

**Problem**: Miner process is not running.

**Impact**: Even if wallet is configured, validators cannot connect because miner is not running.

**Fix Required**:
```bash
# Start the miner
python3 -m miner.miner --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY
```

Or if you have systemd services on a server:
```bash
sudo systemctl start autoppia-miner
```

---

### Issue 3: Local Development Environment ⚠️

**Problem**: This appears to be a local development machine, not a production server.

**Impact**: 
- Validators need to connect to a publicly accessible IP
- Local IPs (127.0.0.1, localhost) won't work for validators
- You need a server with a public IP address

**Options**:
1. **Deploy to a server** (DigitalOcean, AWS, etc.) with public IP
2. **Use a tunnel** (ngrok, cloudflare tunnel) for testing
3. **Use the production server** if you have one deployed

---

## 📋 Action Items

### Immediate Actions:

1. **Set Wallet Configuration**:
   ```bash
   # Edit .env
   nano .env
   
   # Add these lines:
   WALLET_NAME=your_actual_wallet_name
   WALLET_HOTKEY=your_actual_hotkey_name
   ```

2. **Verify Wallet Exists**:
   ```bash
   btcli wallet list
   ```

3. **Check Registration** (if wallet is set):
   ```bash
   btcli subnet show --netuid 36 --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY
   ```

4. **Start Miner** (after wallet is configured):
   ```bash
   python3 -m miner.miner --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY
   ```

### For Production Deployment:

1. **Deploy to Server**:
   - Use DigitalOcean, AWS, or similar
   - Ensure public IP address
   - Open ports 8080 and 8091 in firewall

2. **Configure Services**:
   - Set up systemd services (see `scripts/deploy/`)
   - Configure `.env` on server
   - Start both API and miner services

3. **Verify Accessibility**:
   ```bash
   # From external network
   curl http://YOUR_SERVER_IP:8080/health
   ```

---

## 🔍 Current Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| API Server | ✅ Running | Port 8080, localhost only |
| Miner | ❌ Not Running | Needs wallet config first |
| Wallet Config | ❌ Missing | WALLET_NAME and WALLET_HOTKEY not set |
| Registration | ❓ Unknown | Cannot check without wallet |
| Public Access | ❌ No | Local development machine |
| Port 8091 | ❌ Not Listening | Miner not running |

---

## 🎯 Why Validators Aren't Connecting

**Primary Reasons**:

1. **Miner Not Running** - The miner process must be running to receive validator requests
2. **No Wallet Configuration** - Miner cannot register without wallet credentials
3. **Local Environment** - Validators need a publicly accessible IP address
4. **Not Registered** - Cannot verify registration without wallet config

**To Fix**:
1. Set wallet configuration in `.env`
2. Start the miner
3. Deploy to a server with public IP (if this is for production)
4. Verify registration on subnet 36

---

## 📝 Next Steps

1. **If this is for local testing**:
   - Set up wallet configuration
   - Start miner locally
   - Use a tunnel (ngrok/cloudflare) to expose API publicly
   - Test with validators

2. **If this is for production**:
   - Deploy to a server (DigitalOcean, AWS, etc.)
   - Configure wallet on server
   - Set up systemd services
   - Open firewall ports
   - Start services
   - Monitor logs

3. **Check existing deployment**:
   - If you have a production server, check its status
   - Verify services are running
   - Check logs for errors
   - Run diagnostic script on server

---

## 🔧 Quick Commands

```bash
# Check wallet
btcli wallet list

# Check registration (after wallet is set)
btcli subnet show --netuid 36 --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY

# Start API (if not running)
python3 -m api.server

# Start Miner (after wallet config)
python3 -m miner.miner --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY

# Check if ports are listening
lsof -i :8080 -i :8091

# Test API
curl http://localhost:8080/health
```

---

**Status**: ⚠️ **Configuration Required** - Wallet credentials needed before miner can run

