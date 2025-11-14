# 🔍 How to Check if Validators Are Testing Your Miner

## Quick Check Commands

Run these on your DigitalOcean droplet:

```bash
# 1. Check miner service status
systemctl status autoppia-miner

# 2. Check recent miner logs for validator activity
journalctl -u autoppia-miner -n 100 --no-pager | grep -E "forward|synapse|process_task|validator" -i

# 3. Check API logs for solve_task calls (from validators)
journalctl -u autoppia-api -n 100 --no-pager | grep "solve_task"

# 4. Check if miner is listening on axon port
ss -tlnp | grep 8091

# 5. Check miner registration
cd /opt/autoppia-miner
python3 -m bittensor wallet overview --netuid 36 --wallet.name default --wallet.hotkey default
```

## Signs of Validator Activity

### ✅ Active Validator Testing:
- **Miner logs show**: `forward` calls, `synapse` processing, `process_task` executions
- **API logs show**: `POST /solve_task` requests with task data
- **Network activity**: Connections on port 8091 (axon port)
- **UID visible**: Miner shows up in metagraph with valid UID

### ❌ No Validator Activity:
- **Miner logs show**: Only startup messages, no forward calls
- **API logs show**: No solve_task requests (or only health checks)
- **Network**: Port 8091 listening but no connections
- **UID**: Miner registered but not being queried

## Using the Check Script

```bash
cd /opt/autoppia-miner
git pull origin main
bash CHECK_VALIDATOR_ACTIVITY.sh
```

This script will:
1. Check miner service status
2. Look for validator activity in logs
3. Check API activity
4. Verify registration
5. Check axon port status

## Understanding Validator Testing

### How Validators Test Miners:
1. **Validators query miners** via Bittensor network
2. **Miner receives synapse** with task (prompt, URL)
3. **Miner processes task** via `process_task()` function
4. **Miner calls API** (`/solve_task`) to generate actions
5. **Miner returns actions** to validator
6. **Validator evaluates** performance and scores miner

### What You'll See in Logs:

**Miner Logs** (`journalctl -u autoppia-miner -f`):
```
✅ Miner started on port 8091
[INFO] Forward call received
[INFO] Processing synapse: task_id=...
[INFO] API response: 200 OK
```

**API Logs** (`journalctl -u autoppia-api -f`):
```
INFO: POST /solve_task
INFO: Task ID: abc-123-def
INFO: Prompt: "Switch to month view"
INFO: URL: http://...
```

## Factors Affecting Validator Testing

### Why Validators Might NOT Be Testing:

1. **New Miner**: Takes time to be discovered
2. **Low Stake**: Validators prioritize high-stake miners
3. **Network Issues**: Miner not properly connected
4. **Performance Issues**: Previous failures reduce queries
5. **Subnet Activity**: Low validator activity overall

### How to Increase Testing:

1. **Ensure miner is running**: `systemctl status autoppia-miner`
2. **Check registration**: Verify UID is valid
3. **Monitor performance**: Improve success rate
4. **Check network**: Ensure axon port is accessible
5. **Wait for discovery**: New miners take time

## Real-Time Monitoring

### Watch Miner Logs Live:
```bash
journalctl -u autoppia-miner -f
```

### Watch API Logs Live:
```bash
journalctl -u autoppia-api -f
```

### Monitor Both:
```bash
# Terminal 1: Miner logs
journalctl -u autoppia-miner -f

# Terminal 2: API logs  
journalctl -u autoppia-api -f
```

## Expected Activity Levels

### Normal Activity:
- **New miners**: 0-5 requests/hour initially
- **Established miners**: 10-50+ requests/hour
- **Peak times**: More activity during active rounds

### Low Activity Indicators:
- Less than 1 request/hour = Low activity
- No requests for hours = Not being tested
- Check miner status and registration

## Troubleshooting

### If No Validator Activity:

1. **Check miner is running**:
   ```bash
   systemctl status autoppia-miner
   ```

2. **Check registration**:
   ```bash
   python3 -m bittensor wallet overview --netuid 36 --wallet.name default --wallet.hotkey default
   ```

3. **Check axon port**:
   ```bash
   ss -tlnp | grep 8091
   ```

4. **Check firewall**:
   ```bash
   ufw status | grep 8091
   ```

5. **Restart miner**:
   ```bash
   systemctl restart autoppia-miner
   ```

## Your Current Status

Based on previous setup:
- ✅ Miner registered (UID: 160)
- ✅ Miner service running
- ✅ Axon port: 8091
- ✅ API accessible
- ⏳ Waiting for validator queries

**Next Steps**: Monitor logs to see when validators start testing!

