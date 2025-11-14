# 📊 What to Expect When Monitoring

## Running the Monitor

```bash
cd /opt/autoppia-miner
git pull origin main
bash MONITOR_VALIDATORS.sh
```

## Expected Output

### If Validators ARE Testing:

```
🔍 Real-Time Validator Activity Monitor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Watching for validator activity...
Press Ctrl+C to stop

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Miner] 14:23:45 Forward call received
[Miner] 14:23:45 Processing synapse: task_id=abc-123-def-456
[API] 14:23:45 POST /solve_task
[API] 14:23:45 Task ID: abc-123-def-456
[API] 14:23:45 Prompt: "Switch to month view in the calendar"
[API] 14:23:45 URL: http://84.247.180.192:8010/?seed=146
[Miner] 14:23:46 API response: 200 OK
[Miner] 14:23:46 Returning actions to validator
[API] 14:23:46 Generated 12 actions
```

### If Validators are NOT Testing:

```
🔍 Real-Time Validator Activity Monitor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Watching for validator activity...
Press Ctrl+C to stop

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

(No output - just waiting)
```

**If you see no output for 5-10 minutes**, validators are likely not testing yet.

## Troubleshooting

### Problem: Script doesn't exist

**Error:**
```
bash: MONITOR_VALIDATORS.sh: No such file or directory
```

**Solution:**
```bash
git pull origin main
ls -la MONITOR_*.sh
```

### Problem: Permission denied

**Error:**
```
bash: ./MONITOR_VALIDATORS.sh: Permission denied
```

**Solution:**
```bash
chmod +x MONITOR_VALIDATORS.sh
bash MONITOR_VALIDATORS.sh
```

### Problem: No output at all

**Possible causes:**
1. Services not running
2. No validator activity
3. Logs not being generated

**Check:**
```bash
# Check services
systemctl status autoppia-miner autoppia-api

# Check if logs exist
journalctl -u autoppia-miner -n 10
journalctl -u autoppia-api -n 10
```

## Alternative: Manual Monitoring

If the script doesn't work, use manual commands:

**Terminal 1:**
```bash
journalctl -u autoppia-miner -f | grep -E "forward|synapse|process_task" -i
```

**Terminal 2:**
```bash
journalctl -u autoppia-api -f | grep "solve_task"
```

## Understanding the Output

### Miner Logs (Blue):
- **"Forward call received"** = Validator is testing
- **"Processing synapse"** = Handling validator request
- **"API response: 200 OK"** = Successfully processed
- **"Returning actions"** = Sending response to validator

### API Logs (Green):
- **"POST /solve_task"** = Received request
- **"Task ID: ..."** = Unique task identifier
- **"Prompt: ..."** = What the validator wants done
- **"URL: ..."** = Target website
- **"Generated X actions"** = Actions created

## Activity Patterns

### Normal Activity:
- Requests come in bursts
- 1-5 requests per minute during active periods
- Gaps of 5-30 minutes between bursts

### High Activity:
- Continuous requests
- 10+ requests per minute
- Very short gaps (< 1 minute)

### Low/No Activity:
- No requests for hours
- Only startup messages
- This is normal for new miners

## Next Steps

1. **Run the monitor** and watch for 10-15 minutes
2. **If you see activity**: Great! Validators are testing
3. **If no activity**: 
   - Check miner is running: `systemctl status autoppia-miner`
   - Check registration: `python3 -m bittensor wallet overview --netuid 36 --wallet.name default --wallet.hotkey default`
   - Wait longer - new miners take time to be discovered

## Quick Status Check

While monitoring, you can check status in another terminal:

```bash
# Check services
systemctl status autoppia-miner autoppia-api --no-pager | grep Active

# Count recent requests
journalctl -u autoppia-api --since "1 hour ago" | grep -c solve_task

# Check miner registration
python3 -m bittensor wallet overview --netuid 36 --wallet.name default --wallet.hotkey default
```

