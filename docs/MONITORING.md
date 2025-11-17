# Monitoring Guide

Complete guide for monitoring your Autoppia miner.

## Quick Monitoring

### Real-time Monitoring

```bash
# Monitor both miner and API logs
bash MONITOR_VALIDATORS.sh

# Monitor miner only
bash MONITOR_SIMPLE.sh

# Monitor API only
bash MONITOR_API.sh
```

### Check Validator Activity

```bash
# Check for validator requests
bash CHECK_VALIDATOR_ACTIVITY.sh

# Quick overnight check
bash QUICK_OVERNIGHT_CHECK.sh

# Detailed overnight analysis
bash CHECK_OVERNIGHT_ACTIVITY.sh
```

## What to Look For

### Validator Activity Patterns

**Successful Requests:**
- `INFO` logs showing task processing
- `POST /solve_task` in API logs
- Actions being generated and returned

**Error Patterns:**
- `ERROR` or `WARNING` in logs
- Failed API calls
- Timeout errors
- Connection refused errors

### Log Interpretation

**Miner Logs** (`journalctl -u autoppia-miner -f`):
- Look for synapse processing
- Check for registration status
- Monitor connection to API

**API Logs** (`journalctl -u autoppia-api -f`):
- Request/response patterns
- Action generation success
- Error responses

## Expected Behavior

### Normal Operation
- Periodic validator requests (varies by network activity)
- Successful action generation
- API responding with 200 status codes
- No frequent errors

### Troubleshooting

**No Validator Activity:**
1. Check miner registration: `python3 -m bittensor wallet overview --netuid 36`
2. Verify API is accessible: `curl http://localhost:8080/health`
3. Check firewall: `ufw status`
4. Review logs for errors

**API Errors:**
1. Check API service: `systemctl status autoppia-api`
2. Verify port is open: `ss -tlnp | grep 8080`
3. Check API logs: `journalctl -u autoppia-api -n 50`

**Connection Issues:**
1. Verify API_URL in .env matches actual API location
2. Check network connectivity
3. Verify miner can reach API endpoint

## Monitoring Scripts

All monitoring scripts are in the root directory:

- `MONITOR_VALIDATORS.sh` - Combined real-time monitoring
- `MONITOR_SIMPLE.sh` - Miner-only monitoring
- `MONITOR_API.sh` - API-only monitoring
- `CHECK_VALIDATOR_ACTIVITY.sh` - Check for validator requests
- `QUICK_OVERNIGHT_CHECK.sh` - Quick activity summary
- `CHECK_OVERNIGHT_ACTIVITY.sh` - Detailed activity analysis

## Interpreting Results

### Activity Metrics

**Total Requests:** Number of validator requests received
**Success Rate:** Percentage of successful responses
**Error Types:** Categories of errors encountered
**Sample Tasks:** Examples of tasks processed

### What Good Metrics Look Like

- ✅ Consistent validator requests
- ✅ High success rate (>90%)
- ✅ Low error rate
- ✅ Diverse task types

### Red Flags

- ❌ No validator activity for extended periods
- ❌ High error rate (>10%)
- ❌ Repeated timeout errors
- ❌ Connection refused errors

## Next Steps

If you see issues:
1. Review detailed logs
2. Check service status
3. Verify configuration
4. Test API endpoints manually
5. Check network connectivity

