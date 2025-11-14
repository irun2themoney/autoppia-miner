# 🔧 Troubleshooting "Failed to fetch" Error

## Problem
InfiniteWeb Arena shows: **"Failed to call benchmark API: Failed to fetch"**

This means InfiniteWeb Arena cannot reach your API endpoint.

---

## ✅ Quick Fix Steps

### Step 1: Run the Fix Script on Your VPS

**SSH into your droplet:**
```bash
ssh root@134.199.201.62
```

**Run the fix script:**
```bash
cd /opt/autoppia-miner
curl -s https://raw.githubusercontent.com/irun2themoney/autoppia-miner/main/fix_api_accessibility.sh -o fix_api_accessibility.sh
chmod +x fix_api_accessibility.sh
sudo ./fix_api_accessibility.sh
```

**OR manually run these commands:**

```bash
# 1. Check if API is running
systemctl status autoppia-api

# 2. If not running, start it
sudo systemctl start autoppia-api

# 3. Open firewall port 8080
sudo ufw allow 8080/tcp
sudo ufw reload

# 4. Test locally
curl http://localhost:8080/health
```

---

### Step 2: Configure DigitalOcean Firewall (CRITICAL)

**This is the most common cause of "Failed to fetch"!**

1. **Go to DigitalOcean Dashboard:**
   - https://cloud.digitalocean.com/networking/firewalls

2. **Check if a firewall exists for your droplet:**
   - If yes: Edit it
   - If no: Create a new one

3. **Add Inbound Rule:**
   - **Type**: Custom
   - **Protocol**: TCP
   - **Port Range**: 8080
   - **Sources**: All IPv4, All IPv6 (or specific IPs if you prefer)
   - **Description**: "API Access"

4. **Apply to your droplet:**
   - Select your droplet
   - Click "Apply"

5. **Also ensure these ports are open:**
   - **22** (SSH)
   - **8080** (API) ← **This is critical!**
   - **8091** (Miner axon, if running miner)

---

### Step 3: Verify API is Accessible

**From your local machine, test:**
```bash
curl http://134.199.201.62:8080/health
```

**Should return:**
```json
{"status":"healthy","worker":"autoppia-miner",...}
```

**If you get "Connection refused" or timeout:**
- DigitalOcean Firewall is blocking it
- Go back to Step 2

---

### Step 4: Check API Logs

**On your VPS:**
```bash
# View recent logs
journalctl -u autoppia-api -n 50

# Follow logs in real-time
journalctl -u autoppia-api -f
```

**Look for:**
- ✅ "Application startup complete"
- ✅ "Uvicorn running on http://0.0.0.0:8080"
- ❌ Any error messages

---

### Step 5: Verify CORS Configuration

**The API should allow all origins by default, but verify:**

**On your VPS:**
```bash
# Check .env file
cat /opt/autoppia-miner/.env | grep CORS

# If not set, add it:
echo "CORS_ORIGINS=*" >> /opt/autoppia-miner/.env

# Restart API
sudo systemctl restart autoppia-api
```

---

## 🔍 Common Issues & Solutions

### Issue 1: API Service Not Running
**Solution:**
```bash
sudo systemctl start autoppia-api
sudo systemctl enable autoppia-api  # Auto-start on boot
```

### Issue 2: Port 8080 Blocked by UFW
**Solution:**
```bash
sudo ufw allow 8080/tcp
sudo ufw reload
```

### Issue 3: DigitalOcean Firewall Blocking
**Solution:**
- Go to: https://cloud.digitalocean.com/networking/firewalls
- Add inbound rule for port 8080
- Apply to your droplet

### Issue 4: API Binding to Wrong Interface
**Check:**
```bash
# Should show 0.0.0.0:8080 (not 127.0.0.1:8080)
netstat -tuln | grep 8080
```

**If it shows 127.0.0.1:8080, fix api.py:**
- Ensure `uvicorn.run(host="0.0.0.0", port=8080)`

### Issue 5: API Crashed
**Check logs:**
```bash
journalctl -u autoppia-api -n 100
```

**Common causes:**
- Missing CHUTES_API_KEY
- Port already in use
- Python errors

---

## ✅ Verification Checklist

Before trying InfiniteWeb Arena again, verify:

- [ ] API service is running: `systemctl status autoppia-api`
- [ ] Port 8080 is listening: `netstat -tuln | grep 8080`
- [ ] UFW allows port 8080: `ufw status | grep 8080`
- [ ] DigitalOcean Firewall allows port 8080
- [ ] API responds locally: `curl http://localhost:8080/health`
- [ ] API responds externally: `curl http://134.199.201.62:8080/health`
- [ ] CORS is configured: `CORS_ORIGINS=*` in .env

---

## 🚨 Still Not Working?

### Test from Multiple Locations:

```bash
# From your local machine
curl http://134.199.201.62:8080/health

# From a different network (use online tool)
# Go to: https://reqbin.com/curl
# Enter: http://134.199.201.62:8080/health
```

### Check if Droplet is Accessible:

```bash
# Ping test
ping 134.199.201.62

# Port test
nc -zv 134.199.201.62 8080
```

### Contact Support:

If nothing works:
1. Check DigitalOcean status: https://status.digitalocean.com
2. Contact DigitalOcean support
3. Share API logs for debugging

---

## 📋 Quick Reference

**Your Endpoint:**
```
134.199.201.62:8080
```

**Test Command:**
```bash
curl http://134.199.201.62:8080/health
```

**Firewall Settings:**
- UFW: `sudo ufw allow 8080/tcp`
- DigitalOcean: Add inbound rule for TCP 8080

**Service Commands:**
```bash
sudo systemctl status autoppia-api
sudo systemctl restart autoppia-api
sudo systemctl logs -u autoppia-api -f
```

