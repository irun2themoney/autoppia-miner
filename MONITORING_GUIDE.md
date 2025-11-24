# 📊 Monitoring Guide - Performance Enhancements

## Quick Status Check

```bash
# Check service status
ssh root@134.199.203.133 "systemctl status autoppia-api autoppia-miner --no-pager"

# Check API health
curl http://134.199.203.133:8080/health
```

## Monitor Performance Enhancements

### 1. Quality Scores
Watch for quality scores in logs (indicates optimizations are working):
```bash
ssh root@134.199.203.133 "journalctl -u autoppia-api -f | grep 'Quality score'"
```

Expected output:
```
✅ Quality score: 0.92 for 8 actions
```

### 2. Response Times
Monitor browser automation performance:
```bash
ssh root@134.199.203.133 "journalctl -u autoppia-api -f | grep 'Browser Automation found'"
```

Expected output:
```
✅ Browser Automation found 5 candidates in 2.3s
```

### 3. Action Optimization
Check for optimization logs:
```bash
ssh root@134.199.203.133 "journalctl -u autoppia-api -f | grep 'Optimized action sequence'"
```

### 4. Fast Mode Status
Verify fast mode is enabled:
```bash
ssh root@134.199.203.133 "journalctl -u autoppia-api --since '5 minutes ago' | grep -i 'fast_mode\|timeout' | head -5"
```

## Monitor Validator Activity

### Check for Validator Requests
```bash
ssh root@134.199.203.133 "journalctl -u autoppia-miner -f | grep -iE 'synapse|task|validator|round'"
```

### Count Requests (Last 24h)
```bash
ssh root@134.199.203.133 "journalctl -u autoppia-api --since '24 hours ago' | grep 'solve_task' | wc -l"
```

### Monitor API Requests
```bash
ssh root@134.199.203.133 "journalctl -u autoppia-api -f | grep 'solve_task'"
```

## Performance Metrics

### Expected Improvements
- **Response time**: 40% faster (4-6s vs 7-10s)
- **Action accuracy**: 85-95%
- **Success rate**: Improved

### Track Metrics
```bash
# Response time distribution
ssh root@134.199.203.133 "journalctl -u autoppia-api --since '1 hour ago' | grep 'Browser Automation found' | grep -oE '[0-9]+\.[0-9]+s' | sort -n"

# Quality score distribution
ssh root@134.199.203.133 "journalctl -u autoppia-api --since '1 hour ago' | grep 'Quality score' | grep -oE '[0-9]\.[0-9]+' | sort -n"
```

## Troubleshooting

### If Quality Scores Not Appearing
- Check if actions are being generated
- Verify ResponseQualityEnhancer is imported
- Check logs for errors

### If Response Times Still Slow
- Verify fast_mode is enabled
- Check browser automation timeouts
- Review DOM analysis logs

### If Services Not Running
```bash
# Restart services
ssh root@134.199.203.133 "systemctl restart autoppia-api autoppia-miner"

# Check logs for errors
ssh root@134.199.203.133 "journalctl -u autoppia-api --since '5 minutes ago' --no-pager | tail -20"
```

## Key Indicators

### ✅ Good Signs
- Quality scores > 0.85
- Response times < 5s for simple tasks
- No errors in logs
- Services running continuously

### ⚠️ Warning Signs
- Quality scores < 0.70
- Response times > 10s consistently
- Frequent timeouts
- Service restarts

## Daily Monitoring Checklist

1. ✅ Check service status
2. ✅ Review quality scores
3. ✅ Monitor response times
4. ✅ Check validator requests
5. ✅ Review error logs
6. ✅ Verify fast mode enabled

## Automated Monitoring Script

Create a monitoring script:
```bash
#!/bin/bash
# monitor_performance.sh

echo "=== Performance Monitoring ==="
echo ""

# Service status
echo "Services:"
ssh root@134.199.203.133 "systemctl is-active autoppia-api autoppia-miner"

# Recent quality scores
echo ""
echo "Recent Quality Scores:"
ssh root@134.199.203.133 "journalctl -u autoppia-api --since '1 hour ago' | grep 'Quality score' | tail -5"

# Response times
echo ""
echo "Recent Response Times:"
ssh root@134.199.203.133 "journalctl -u autoppia-api --since '1 hour ago' | grep 'Browser Automation found' | tail -5"

# Validator requests
echo ""
echo "Validator Requests (last 24h):"
ssh root@134.199.203.133 "journalctl -u autoppia-api --since '24 hours ago' | grep 'solve_task' | wc -l"
```

Save as `scripts/monitor_performance.sh` and run:
```bash
chmod +x scripts/monitor_performance.sh
./scripts/monitor_performance.sh
```

