# 🚀 Enhanced Monitoring Guide (Based on Grok's Analysis)

## ✅ Current Status Confirmed

**Grok's Assessment**: You're primed and ready!
- ✅ Axon visible + API responding
- ✅ UID 160 in metagraph (no registration ghosts)
- ✅ Solid uptime (past flaky startup phase)
- ✅ Endpoint public-ready

## 📊 Discovery Timeline (Grok's Analysis)

- **Best Case**: 5-15 minutes (if validator hot-looping SN36)
- **Typical**: 15-30 minutes (as validators cycle through UIDs)
- **Worst Case**: 1-2 hours (network lag or high load)

**Your Status**: No red flags - you're in the "soon" category! 🎯

## 🔍 Enhanced Monitoring Commands

### **1. Live Log Tails (Bread & Butter)**

#### API Side (Watch for Validator Requests):
```bash
journalctl -u autoppia-api -f | grep -E "(solve_task|POST /solve_task|validator|health)"
```

**What to Spot**:
- Incoming POSTs from validator IPs (18.x.x.x AWS ranges common)
- First request might be `/health` probe
- Tasks follow after health check

#### Miner Side (Watch for Task Processing):
```bash
journalctl -u autoppia-miner -f | grep -E "(process_task|Dynamic 3|extraction|form_fill|success|error)"
```

**Pro Tip**: "Processing task: ID xyz" means you're in! Log the task type for optimization.

#### Watch Both at Once:
```bash
# Using tmux (if installed)
tmux new-session -d -s miner-watch
tmux split-window -h
tmux send-keys -t 0 "journalctl -u autoppia-api -f" Enter
tmux send-keys -t 1 "journalctl -u autoppia-miner -f" Enter
tmux attach -t miner-watch
```

### **2. Dashboard Deep Dive (Crystal Ball)**

**Access**: `http://134.199.203.133:8080/api/dashboard`

**Key Metrics to Refresh Every 2 Mins**:
- **Total Requests**: 
  - Static at 0? → Waiting
  - Jumps to 1-5? → Probes incoming
  - 10+? → Task flood - emissions inbound! 🎉

- **Validator IPs**: 
  - Empty → pre-discovery
  - Populates with unique IPs → scored

- **Success Rates**: 
  - Starts at N/A
  - 0% on first fails (normal - tune retries)
  - Climbs to 70%+ as agent adapts

- **Uptime/Errors**: 
  - Green across board? → You're golden

**Quick JSON Check**:
```bash
curl -s http://localhost:8080/api/dashboard/metrics | python3 -m json.tool
```

### **3. Network Snoops (Paranoia Mode)**

#### Axon Health Check:
```bash
btcli axon ping --netuid 36 --wallet.name your_wallet --wallet.hotkey your_hotkey
```
Confirms validators can see you.

#### Traffic Watch:
```bash
tcpdump -i any port 8091 or port 8080 -n
# Look for SYN from external IPs
# Ctrl+C after 5 mins
```

#### Metagraph Check:
```bash
btcli metagraph --netuid 36 | grep "160"
```
Your UID should show with axon details.

### **4. Off-Server Backup Monitoring**

#### IWAP Leaderboard:
- Visit: `https://infinitewebarena.autoppia.com` > Agents tab
- Search: UID 160
- Updates: ~every 10 mins post-first task

#### Taostats:
- Visit: `https://taostats.io/subnets/netuid=36/miners`
- Watch: Your UID's incentive weight tick up from 0

## 🎯 Post-Discovery Game Plan

### **First Tasks (What to Expect)**
- 5-20 Dynamic 3 evals
- Synthetic e-com nav or form chaos
- Success on 60%+ gets baseline emissions
- ~0.1-0.3 TAO initial drip
- Scaling with ranks

### **Quick Optimizations (If Needed)**

#### If Errors Spike on Mutations:
```yaml
# Add to config
retry_policy:
  backoff: 2.0
  max: 5
```

#### If Low Speed:
- Cap screenshots to every 3 actions
- Chain Chutes LLM (cuts latency 20-30%)

### **Emission Watch**
After 1-2 hours of tasks:
```bash
btcli wallet overview --netuid 36
```
Top newbies hit **0.5+ TAO/day** by EOD if uptime holds!

## 🛠️ Quick Status Scripts

### **Enhanced Monitor**:
```bash
./scripts/monitor_validator_discovery.sh
```
Comprehensive status check with all metrics.

### **Live Activity Watcher**:
```bash
./scripts/watch_validator_activity.sh
```
Real-time validator activity monitoring.

### **Quick Status Check**:
```bash
./scripts/check_discovery_status.sh
```
Fast discovery status (run every few minutes).

## ⚠️ Risk Check (If No Activity After 1 Hour)

1. **Check Firewall**:
   ```bash
   ufw allow 8091/tcp
   ufw allow 8080/tcp
   ufw status
   ```

2. **Check Axon Logs**:
   ```bash
   journalctl -u autoppia-miner | grep -E "bind|error|axon"
   ```

3. **Verify Ports**:
   ```bash
   ss -tlnp | grep -E "8091|8080"
   ```

## 📈 Success Indicators

### **You're Discovered When**:
- ✅ `POST /solve_task` appears in API logs
- ✅ Validator IPs show up (not 127.0.0.1)
- ✅ Dashboard shows `total_requests > 0`
- ✅ Miner logs show "Processing task"
- ✅ IWAP leaderboard shows your UID

### **You're Scoring When**:
- ✅ Success rate > 50%
- ✅ Multiple validator IPs
- ✅ Consistent task flow
- ✅ TAO balance increasing

## 🎉 Bottom Line

**Grok's Verdict**: "This screams 'soon.'"

Your miner is:
- ✅ Fully operational
- ✅ Properly configured
- ✅ Visible to validators
- ✅ Ready for discovery

**Just wait - validators will find you!** 🚀

---

**Status**: ✅ **PRIMED AND READY - DISCOVERY IMMINENT!**

