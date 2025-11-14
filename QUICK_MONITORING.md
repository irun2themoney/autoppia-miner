# 🚀 Quick Monitoring Guide

## Simple Commands

### Option 1: Monitor Miner (Validator Activity)
```bash
journalctl -u autoppia-miner -f | grep -E "forward|synapse|process_task" -i
```

### Option 2: Monitor API (solve_task Requests)
```bash
journalctl -u autoppia-api -f | grep "solve_task"
```

### Option 3: Monitor Both (Use Scripts)
```bash
# Terminal 1: Miner logs
bash MONITOR_SIMPLE.sh

# Terminal 2: API logs
bash MONITOR_API.sh
```

## Using the Monitoring Scripts

### Combined Monitor (Both Services)
```bash
cd /opt/autoppia-miner
git pull origin main
bash MONITOR_VALIDATORS.sh
```

This shows:
- **Blue [Miner]**: Validator forward calls, synapse processing
- **Green [API]**: solve_task requests, task details

### Separate Monitors

**Terminal 1 - Miner:**
```bash
bash MONITOR_SIMPLE.sh
```

**Terminal 2 - API:**
```bash
bash MONITOR_API.sh
```

## What You'll See

### When Validators Test:

**Miner Log:**
```
[Miner] 14:23:45 Forward call received
[Miner] 14:23:45 Processing synapse: task_id=abc-123
[Miner] 14:23:46 API response: 200 OK
```

**API Log:**
```
[API] 14:23:45 POST /solve_task
[API] 14:23:45 Task ID: abc-123
[API] 14:23:45 Prompt: "Switch to month view"
[API] 14:23:46 Generated 12 actions
```

### No Activity:

**Miner Log:**
```
(empty or only startup messages)
```

**API Log:**
```
(empty or only startup messages)
```

## Advanced Filtering

### Show Only Errors:
```bash
journalctl -u autoppia-miner -f | grep -E "ERROR|error|Exception|exception" -i
journalctl -u autoppia-api -f | grep -E "ERROR|error|Exception|exception" -i
```

### Show Task Details:
```bash
journalctl -u autoppia-api -f | grep -E "Task ID|Prompt|URL" -i
```

### Count Requests:
```bash
# Count in last hour
journalctl -u autoppia-api --since "1 hour ago" | grep -c "solve_task"
```

## Tips

1. **Use separate terminals** for miner and API logs
2. **Watch for patterns** - requests usually come in bursts
3. **Check timestamps** - activity varies throughout the day
4. **Monitor errors** - fix issues quickly to improve score

## Quick Status Check

```bash
# Check if services are running
systemctl status autoppia-miner autoppia-api --no-pager | grep Active

# Count recent requests
echo "Requests (last hour): $(journalctl -u autoppia-api --since '1 hour ago' | grep -c solve_task)"
```

