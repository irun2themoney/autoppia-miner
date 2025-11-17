# Quick Deploy & Verify Guide

## Deploy to DigitalOcean Droplet

### Option 1: Automated Script (Recommended)

```bash
# On your droplet
cd /opt/autoppia-miner
bash DEPLOY_AND_VERIFY.sh
```

This script will:
- ✅ Pull latest code
- ✅ Install dependencies
- ✅ Update systemd services (if needed)
- ✅ Restart services
- ✅ Verify everything is working
- ✅ Test API endpoints

### Option 2: Manual Steps

```bash
# 1. SSH into droplet
ssh root@134.199.203.133

# 2. Navigate to project
cd /opt/autoppia-miner

# 3. Pull latest code
git pull origin main

# 4. Install dependencies
source venv/bin/activate
pip install -r requirements.txt

# 5. Restart services
systemctl restart autoppia-api
systemctl restart autoppia-miner

# 6. Check status
systemctl status autoppia-api
systemctl status autoppia-miner
```

## Verify Deployment

### 1. Check Services Are Running

```bash
# Check API
systemctl is-active autoppia-api && echo "✅ API running" || echo "❌ API not running"

# Check Miner
systemctl is-active autoppia-miner && echo "✅ Miner running" || echo "❌ Miner not running"
```

### 2. Test API Endpoints

```bash
# Health check
curl http://localhost:8080/health

# Should return: {"status":"healthy","version":"1.0.0"}

# Test solve_task
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id":"test","prompt":"Switch to month view","url":"https://example.com"}'

# Should return JSON with "actions" array
```

### 3. Check Logs

```bash
# API logs (last 20 lines)
journalctl -u autoppia-api -n 20 --no-pager

# Miner logs (last 20 lines)
journalctl -u autoppia-miner -n 20 --no-pager

# Watch logs in real-time
journalctl -u autoppia-api -f
journalctl -u autoppia-miner -f
```

### 4. Verify Ports

```bash
# Check API port
ss -tlnp | grep 8080
# OR
netstat -tlnp | grep 8080

# Check miner port
ss -tlnp | grep 8091
# OR
netstat -tlnp | grep 8091
```

### 5. Test from Outside

```bash
# From your local machine
curl http://134.199.203.133:8080/health

# Should return: {"status":"healthy","version":"1.0.0"}
```

## Troubleshooting

### API Not Starting

```bash
# Check logs
journalctl -u autoppia-api -n 50 --no-pager

# Common issues:
# - Import errors → Check Python path
# - Port already in use → Check what's using port 8080
# - Missing dependencies → Run: pip install -r requirements.txt
```

### Miner Not Starting

```bash
# Check logs
journalctl -u autoppia-miner -n 50 --no-pager

# Common issues:
# - Wallet not found → Check wallet path
# - Not registered → Register on subnet 36
# - API connection failed → Check API is running
```

### Services Using Old Commands

If services are still using `api.py` or `miner.py` directly:

```bash
# Update API service
sed -i 's|ExecStart=.*api.py|ExecStart=/opt/autoppia-miner/venv/bin/python3 -m api.server|' /etc/systemd/system/autoppia-api.service

# Update miner service
sed -i 's|ExecStart=.*miner.py|ExecStart=/opt/autoppia-miner/venv/bin/python3 -m miner.miner|' /etc/systemd/system/autoppia-miner.service

# Reload and restart
systemctl daemon-reload
systemctl restart autoppia-api
systemctl restart autoppia-miner
```

## Success Indicators

✅ **API Service:**
- Status: `active (running)`
- Health endpoint returns `{"status":"healthy"}`
- Port 8080 is listening
- No errors in logs

✅ **Miner Service:**
- Status: `active (running)`
- Port 8091 is listening
- Connected to API
- No errors in logs

✅ **Endpoints:**
- `/health` returns healthy status
- `/solve_task` returns actions array
- CORS headers present

## Next Steps

After successful deployment:

1. **Monitor for validator activity:**
   ```bash
   bash MONITOR_VALIDATORS.sh
   ```

2. **Set up HTTPS tunnel (for playground):**
   ```bash
   cloudflared tunnel --url http://localhost:8080
   ```

3. **Check overnight activity:**
   ```bash
   bash CHECK_OVERNIGHT_ACTIVITY.sh
   ```

