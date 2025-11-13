# 🎮 Operations Manual - Quick Reference

**For complete guides, see [SETUP_AND_MINING_GUIDE.md](./SETUP_AND_MINING_GUIDE.md)**

---

## ⚡ Essential Commands

### Check Status (Do This First!)
```bash
# Quick status check
pm2 status autoppia_miner

# See what's happening
pm2 logs autoppia_miner --lines 10 --nostream

# Or live stream
pm2 logs autoppia_miner
```

### Start/Stop/Restart
```bash
# Start miner (from ~/autoppia_web_agents_subnet)
cd ~/autoppia_web_agents_subnet && pm2 start ecosystem.config.js

# Stop
pm2 stop autoppia_miner

# Restart
pm2 restart autoppia_miner

# Kill all
pm2 kill
```

### Verify Everything Works
```bash
# Worker health
curl https://autoppia-miner.onrender.com/health

# Wallet balance
btcli wallet balance --wallet.name default

# Check registration
btcli subnet list --wallet.name default | grep 36
```

---

## 🛠️ Common Issues & Fixes

| Problem | Command to Fix |
|---------|----------------|
| Miner crashed | `pm2 restart autoppia_miner` |
| Out of memory | `pm2 kill && pm2 start ecosystem.config.js` |
| Worker not responding | `curl https://autoppia-miner.onrender.com/health` |
| Want to see real activity | `pm2 logs autoppia_miner` |
| Not earning tasks? | Check hotkey registration |

---

## 📊 Real-time Monitoring

### Option A: Simple
```bash
pm2 monit autoppia_miner
```

### Option B: Live Logs
```bash
pm2 logs autoppia_miner
```

### Option C: Detailed Refresh (Every 60s)
```bash
./monitor_miner.sh
```

### Option D: Quick Check
```bash
./check_miner.sh
```

---

## 🔧 System Information

**System Location**: `/Users/illfaded2022/Desktop/WORKSPACE/autoppia-miner`

**Miner Location**: `~/autoppia_web_agents_subnet`

**Worker**: https://autoppia-miner.onrender.com (Render - deployed)

**Miner Process**: `autoppia_miner` (PM2 - running on Mac)

**Network**: Bittensor Subnet 36 (Autoppia Web Agents)

**Status**: ✅ RUNNING

---

## 🚀 If Starting Everything from Scratch

```bash
# 1. Go to miner directory
cd ~/autoppia_web_agents_subnet
source miner_env/bin/activate

# 2. Start it
pm2 start ecosystem.config.js

# 3. Verify
pm2 status

# 4. Watch it work
pm2 logs autoppia_miner
```

---

## 💾 Important Files

- **Miner Config**: `~/autoppia_web_agents_subnet/.env`
- **PM2 Config**: `~/autoppia_web_agents_subnet/ecosystem.config.js`
- **Worker Config**: `/Users/illfaded2022/Desktop/WORKSPACE/autoppia-miner/.env`
- **Worker Code**: `/Users/illfaded2022/Desktop/WORKSPACE/autoppia-miner/worker.py`
- **Logs**: Check via `pm2 logs autoppia_miner`

---

## 🎯 What Should I See?

### In PM2 Logs
```
Receiving tasks from validators on subnet 36
Processing task X with prompt: "..."
Sending to worker: https://autoppia-miner.onrender.com/solve_task
Got response: 3 actions generated
Submitting result back to validator
```

### Success Indicators
- ✅ PM2 shows `online` status
- ✅ CPU < 10% (at rest)
- ✅ Memory < 100MB
- ✅ Worker health returns `healthy`
- ✅ Logs show task activity
- ✅ Balance doesn't decrease (only increases when earning!)

---

## 🚨 Emergency Procedures

### If Everything Is Broken
```bash
# Nuclear option
pm2 kill

# Restart miner
cd ~/autoppia_web_agents_subnet
pm2 start ecosystem.config.js

# Check if worker is still running
curl https://autoppia-miner.onrender.com/health
```

### If Worker Crashes (Render)
- Go to https://dashboard.render.com
- Click the service
- Click "Redeploy"
- Wait 2-3 minutes

### If Hotkey Lost Funds
```bash
btcli wallet balance --wallet.name default
btcli wallet show --wallet.name default
```

---

## 📈 Performance Tips

1. **For Best Performance**: Let it run continuously
2. **Monitor Growth**: Watch `pm2 status` - memory should stay stable
3. **Restart Weekly**: Keeps things fresh
   ```bash
   pm2 restart autoppia_miner
   ```
4. **Check Logs Daily**: Look for errors or warnings
   ```bash
   pm2 logs autoppia_miner --lines 50 --nostream | grep -i error
   ```

---

## 🎓 Learning Resources

- [Full Setup Guide](./SETUP_AND_MINING_GUIDE.md) - Read this for details
- [Project Status](./PROJECT_STATUS.md) - Current metrics
- [Monitoring Guide](./MONITORING_GUIDE.md) - Advanced monitoring
- [API Keys Explained](./API_KEYS_EXPLAINED.md) - API key reference

---

## ✅ Daily Checklist

- [ ] Check miner is running: `pm2 status`
- [ ] Check worker is responding: `curl https://autoppia-miner.onrender.com/health`
- [ ] Check recent logs: `pm2 logs autoppia_miner --lines 5`
- [ ] Monitor once: `pm2 monit` (Ctrl+C to exit)

---

**Questions?** See [SETUP_AND_MINING_GUIDE.md](./SETUP_AND_MINING_GUIDE.md)

**Emergency?** Run this: `pm2 restart autoppia_miner && curl https://autoppia-miner.onrender.com/health`

✨ **Happy Mining!** ✨

