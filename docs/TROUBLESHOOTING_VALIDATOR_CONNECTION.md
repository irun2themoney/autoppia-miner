# 🔍 Troubleshooting: Why Validators Aren't Connecting

## Common Issues & Solutions

### Issue 1: IP Address is 0.0.0.0 ❌

**Symptom**: Miner logs show `Final external IP: 0.0.0.0`

**Problem**: Validators cannot connect to `0.0.0.0` - this is not a valid public IP.

**Solution**:
1. Check if you're behind a NAT/firewall
2. Ensure your server has a public IP address
3. Run the diagnostic script: `./scripts/diagnose_validator_connection.sh`
4. The miner now tries multiple methods to get your IP:
   - Metagraph (most reliable)
   - External services (ipify.org, ifconfig.me)
   - System method (fallback)

**Fix**: If IP is still 0.0.0.0, manually set it in `.env`:
```bash
# Get your public IP
curl ifconfig.me

# Add to .env (if needed, though miner should auto-detect)
# The miner will use the metagraph IP if available
```

---

### Issue 2: Axon Not Served to Network ❌

**Symptom**: No "Axon served to subtensor network!" message in logs

**Problem**: Miner is running but not advertising itself to validators.

**Solution**:
1. Check miner logs: `journalctl -u autoppia-miner -n 100`
2. Look for errors during `serve_axon()` call
3. Ensure miner is registered: `btcli subnet show --netuid 36`
4. Restart miner: `sudo systemctl restart autoppia-miner`

**Fix**: The miner should automatically serve the axon. If it fails:
- Check wallet configuration
- Verify registration status
- Check network connectivity to Bittensor network

---

### Issue 3: API Not Publicly Accessible ❌

**Symptom**: API works locally but not from external network

**Problem**: Firewall or network configuration blocking port 8080.

**Solution**:
1. Test from external network:
   ```bash
   curl http://YOUR_IP:8080/health
   ```

2. Check firewall:
   ```bash
   # UFW
   sudo ufw allow 8080/tcp
   sudo ufw allow 8091/tcp
   
   # Firewalld
   sudo firewall-cmd --add-port=8080/tcp --permanent
   sudo firewall-cmd --add-port=8091/tcp --permanent
   sudo firewall-cmd --reload
   ```

3. Check if API is bound to 0.0.0.0 (not just localhost):
   ```bash
   netstat -tuln | grep 8080
   # Should show: 0.0.0.0:8080 (not 127.0.0.1:8080)
   ```

**Fix**: Ensure API is accessible from internet on port 8080.

---

### Issue 4: Validators Don't Know Your API URL ⚠️

**Symptom**: Miner is registered, axon is served, but no requests

**Problem**: Validators need to know your API endpoint URL.

**How Validators Discover API**:
1. **Via Synapse** (Port 8091): Validators send synapse to your axon, miner forwards to API
2. **Direct API Call** (Port 8080): Validators call `http://YOUR_IP:8080/solve_task` directly

**Solution**: 
- The miner handles both methods
- If validators use synapses, they go to port 8091 → miner forwards to API
- If validators call API directly, they need to know port 8080 (convention)

**Fix**: Ensure both ports are open and accessible:
- Port 8091: For Bittensor synapses
- Port 8080: For direct API calls

---

### Issue 5: Miner Not Registered ❌

**Symptom**: No UID assigned, miner logs show "not registered"

**Problem**: Miner is not registered on subnet 36.

**Solution**:
1. Check registration:
   ```bash
   btcli subnet show --netuid 36 --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY
   ```

2. Register if needed:
   ```bash
   btcli subnet register --netuid 36 --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY
   ```

3. Verify in `.env`:
   ```bash
   WALLET_NAME=your_wallet
   WALLET_HOTKEY=your_hotkey
   ```

**Fix**: Register miner on subnet 36 (requires 0.1+ TAO).

---

### Issue 6: Low Validator Activity ⏱️

**Symptom**: Everything is correct but no requests

**Problem**: Validators may not be actively testing all miners.

**Reality Check**:
- Validators test miners in batches
- New miners may have lower priority
- Discovery can take 10-30 minutes
- Some validators may be inactive

**Solution**:
1. Wait 30-60 minutes after deployment
2. Check if other miners are getting requests (subnet activity)
3. Monitor logs: `journalctl -u autoppia-miner -f`
4. Check dashboard: `http://YOUR_IP:8080/api/dashboard`

**Fix**: Be patient - validators will discover you eventually.

---

## Diagnostic Checklist

Run this to check everything:

```bash
./scripts/diagnose_validator_connection.sh
```

**Checklist**:
- [ ] Miner registered on subnet 36 (has UID)
- [ ] API service running (`systemctl status autoppia-api`)
- [ ] Miner service running (`systemctl status autoppia-miner`)
- [ ] Port 8080 listening and accessible from internet
- [ ] Port 8091 listening
- [ ] External IP is correct (not 0.0.0.0)
- [ ] Axon served to network (check logs)
- [ ] No errors in miner logs
- [ ] Firewall allows ports 8080 and 8091

---

## Quick Fixes

### Fix 1: Restart Everything
```bash
sudo systemctl restart autoppia-api
sudo systemctl restart autoppia-miner
journalctl -u autoppia-miner -f  # Watch for errors
```

### Fix 2: Check IP Detection
```bash
# Get your public IP
curl ifconfig.me

# Check what miner detected
journalctl -u autoppia-miner | grep "Final external IP"
```

### Fix 3: Verify Ports
```bash
# Check if ports are listening
netstat -tuln | grep -E "8080|8091"

# Test API from external network
curl http://YOUR_IP:8080/health
```

### Fix 4: Check Registration
```bash
# Verify registration
btcli subnet show --netuid 36 --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY

# Check UID in logs
journalctl -u autoppia-miner | grep "UID:"
```

---

## Expected Timeline

**After Deployment**:
- **0-5 minutes**: Miner appears in metagraph
- **5-15 minutes**: Validators discover your miner
- **15-30 minutes**: First validator requests arrive
- **30-60 minutes**: Regular task flow begins

**If no requests after 1 hour**:
1. Run diagnostic script
2. Check all items in checklist
3. Verify other miners are getting requests
4. Check for errors in logs

---

## Still Not Working?

1. **Check miner logs**:
   ```bash
   journalctl -u autoppia-miner -n 200 | grep -i "error\|failed\|exception"
   ```

2. **Check API logs**:
   ```bash
   journalctl -u autoppia-api -n 200 | grep -i "error\|failed"
   ```

3. **Verify network connectivity**:
   ```bash
   # Test from external network
   curl -v http://YOUR_IP:8080/health
   curl -v http://YOUR_IP:8091
   ```

4. **Check subnet activity**:
   - Are other miners getting requests?
   - How many active validators are there?
   - Is subnet 36 active?

---

## Most Common Issue

**90% of cases**: IP address is `0.0.0.0` or API is not publicly accessible.

**Quick check**:
```bash
# 1. Get your IP
curl ifconfig.me

# 2. Test API from external network
curl http://$(curl -s ifconfig.me):8080/health

# 3. Check miner detected IP
journalctl -u autoppia-miner | grep "Final external IP"
```

If IP is `0.0.0.0` or API is not accessible, that's your problem!

