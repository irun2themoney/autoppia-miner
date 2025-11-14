# 📊 Log Interpretation Guide

## What to Look For in Miner Logs

### ✅ Signs of Validator Activity:

**When a validator tests your miner, you'll see:**

```
[INFO] Forward call received
[INFO] Processing synapse: task_id=abc-123-def
[INFO] API response: 200 OK
[INFO] Returning actions to validator
```

**Or in Bittensor format:**
```
Forward call: synapse=<Synapse object>
Processing task: prompt="Switch to month view", url="http://..."
API call successful: 200
```

### ❌ No Validator Activity:

**If you only see:**
```
✅ Miner started on port 8091
🔧 Initializing Autoppia Miner
✅ Miner registered! UID: 160
🌐 Axon started on 134.199.203.133:8091
```

**And nothing else** = No validators are testing yet.

## What to Look For in API Logs

### ✅ Validator Requests:

**When validators test, you'll see:**
```
INFO: POST /solve_task
INFO: Task ID: abc-123-def-456
INFO: Prompt: "Switch to month view in the calendar"
INFO: URL: http://84.247.180.192:8010/?seed=146
INFO: Generated 12 actions
```

**Request format:**
```json
{
  "id": "task-id-from-validator",
  "prompt": "task description",
  "url": "target URL"
}
```

### ❌ No Validator Activity:

**If you only see:**
```
INFO: Started server process
INFO: Application startup complete
INFO: Uvicorn running on http://0.0.0.0:8080
```

**And no POST /solve_task requests** = No validators testing.

## Common Log Patterns

### Pattern 1: Successful Validator Test
```
[Miner] Forward call received
[Miner] Processing synapse: task_id=xyz
[API] POST /solve_task - Task ID: xyz
[API] Prompt: "Click button"
[API] Generated 7 actions
[Miner] API response: 200 OK
[Miner] Returning actions to validator
```

### Pattern 2: API Error During Test
```
[Miner] Forward call received
[Miner] Processing synapse: task_id=xyz
[API] POST /solve_task - Task ID: xyz
[API] ERROR: Exception occurred
[Miner] API response: 500
[Miner] Returning empty actions
```

### Pattern 3: Timeout
```
[Miner] Forward call received
[Miner] Processing synapse: task_id=xyz
[Miner] API timeout after 30s
[Miner] Returning empty actions
```

## Monitoring Tips

### 1. Watch Both Logs Simultaneously

**Terminal 1 (Miner):**
```bash
journalctl -u autoppia-miner -f
```

**Terminal 2 (API):**
```bash
journalctl -u autoppia-api -f
```

### 2. Filter for Important Events

**Miner logs - only validator activity:**
```bash
journalctl -u autoppia-miner -f | grep -E "forward|synapse|process_task|validator" -i
```

**API logs - only solve_task requests:**
```bash
journalctl -u autoppia-api -f | grep "solve_task"
```

### 3. Count Requests

**Count validator requests in last hour:**
```bash
journalctl -u autoppia-api --since "1 hour ago" | grep -c "solve_task"
```

**Count successful responses:**
```bash
journalctl -u autoppia-miner --since "1 hour ago" | grep -c "200 OK"
```

## Expected Activity Levels

### New Miner (First 24 hours):
- **0-5 requests/hour** = Normal
- **No requests** = Still being discovered

### Established Miner:
- **10-50+ requests/hour** = Good activity
- **100+ requests/hour** = High activity

### Low Activity:
- **< 1 request/hour** = Low activity
- **No requests for hours** = Check miner status

## Troubleshooting Based on Logs

### Problem: No Forward Calls in Miner Logs

**Possible causes:**
1. Miner not registered properly
2. Axon not started
3. Network/firewall blocking port 8091
4. Validators not querying yet

**Check:**
```bash
systemctl status autoppia-miner
ss -tlnp | grep 8091
python3 -m bittensor wallet overview --netuid 36 --wallet.name default --wallet.hotkey default
```

### Problem: Forward Calls But API Errors

**Possible causes:**
1. API not running
2. API timeout
3. API returning errors

**Check:**
```bash
systemctl status autoppia-api
journalctl -u autoppia-api -n 50 | grep ERROR
curl http://localhost:8080/health
```

### Problem: API Requests But No Miner Activity

**Possible causes:**
1. Requests from playground/testing (not validators)
2. Miner not forwarding properly

**Check:**
- Are requests coming from external IPs? (validators)
- Or localhost? (testing)

## Key Metrics to Track

### 1. Request Rate
- How many requests per hour?
- Is it increasing or decreasing?

### 2. Success Rate
- How many return `success: True`?
- How many return `success: False`?

### 3. Response Time
- How long does each request take?
- Are there timeouts?

### 4. Error Rate
- How many errors occur?
- What types of errors?

## Sample Monitoring Script

```bash
#!/bin/bash
# Monitor validator activity

echo "📊 Validator Activity Monitor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Count requests in last hour
REQUESTS=$(journalctl -u autoppia-api --since "1 hour ago" | grep -c "solve_task")
echo "Requests (last hour): $REQUESTS"

# Count forward calls
FORWARDS=$(journalctl -u autoppia-miner --since "1 hour ago" | grep -c "forward\|Forward" -i)
echo "Forward calls (last hour): $FORWARDS"

# Check if miner is running
if systemctl is-active --quiet autoppia-miner; then
    echo "Miner status: ✅ Running"
else
    echo "Miner status: ❌ Not running"
fi

# Check if API is running
if systemctl is-active --quiet autoppia-api; then
    echo "API status: ✅ Running"
else
    echo "API status: ❌ Not running"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

## Next Steps

1. **Start monitoring**: Run the log commands
2. **Watch for patterns**: Look for forward calls and solve_task requests
3. **Track metrics**: Count requests and success rates
4. **Optimize**: Improve based on what you see

