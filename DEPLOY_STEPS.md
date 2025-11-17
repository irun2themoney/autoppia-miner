# Step-by-Step Deployment Commands

Copy and paste these commands one at a time on your server.

## Step 1: SSH into your server
```bash
ssh root@YOUR_SERVER_IP
# Replace YOUR_SERVER_IP with your actual server IP
```

## Step 2: Navigate to the miner directory
```bash
cd /opt/autoppia-miner
```

## Step 3: Pull the latest code with the fix
```bash
git pull origin main
```

## Step 4: Verify the fix is in the code
```bash
grep -n "serve_axon" miner/miner.py
```
You should see lines with `serve_axon` - this confirms the fix is present.

## Step 5: Check current miner status
```bash
systemctl status autoppia-miner --no-pager | head -15
```

## Step 6: Restart the miner service
```bash
systemctl restart autoppia-miner
```

## Step 7: Wait a few seconds for it to start
```bash
sleep 5
```

## Step 8: Check if miner started successfully
```bash
systemctl status autoppia-miner --no-pager | head -15
```
Look for "active (running)" in green.

## Step 9: Check the logs for the critical success message
```bash
journalctl -u autoppia-miner -n 30 --no-pager | grep -E "Axon served|Failed to serve|Miner registered|UID:"
```

**What to look for:**
- ✅ **SUCCESS**: "Axon served to subtensor network!" or "✅ Axon served to subtensor network!"
- ✅ **SUCCESS**: "Miner registered! UID: X"
- ❌ **ERROR**: "Failed to serve axon" - if you see this, there's a problem

## Step 10: View full recent logs
```bash
journalctl -u autoppia-miner -n 50 --no-pager
```

## Step 11: Verify port 8091 is listening
```bash
ss -tlnp | grep 8091
```
You should see something like `:8091` in the output.

## Step 12: Verify API is still running
```bash
systemctl status autoppia-api --no-pager | head -10
```

## Step 13: Test API health endpoint
```bash
curl http://localhost:8080/health
```
Should return: `{"status":"healthy","version":"1.0.0","agent_type":"template"}`

## Step 14: Monitor logs in real-time (optional)
```bash
journalctl -u autoppia-miner -f
```
Press `Ctrl+C` to exit when done watching.

---

## Troubleshooting

### If miner fails to start:
```bash
journalctl -u autoppia-miner -n 100 --no-pager
```
Look for error messages.

### If you see "Failed to serve axon":
1. Check firewall:
   ```bash
   ufw status | grep 8091
   ```
   If port 8091 is not open:
   ```bash
   ufw allow 8091/tcp
   ufw reload
   ```

2. Check miner registration:
   ```bash
   python3 -m bittensor wallet overview --netuid 36 --wallet.name default --wallet.hotkey default
   ```

### If miner is not registered:
```bash
btcli wallet register --netuid 36 --wallet.name default --wallet.hotkey default
```

---

## Success Indicators

After deployment, you should see in the logs:
1. ✅ "Miner registered! UID: X"
2. ✅ "Axon started on X.X.X.X:8091"
3. ✅ "Axon served to subtensor network!"
4. ✅ "Miner is running and ready to receive validator requests!"

If you see all of these, the fix is deployed successfully and validators should be able to discover your miner!

