# Testing on IWA Playground

Guide for testing your deployed miner on the [IWA Playground](https://infinitewebarena.autoppia.com/playground).

## Prerequisites

✅ **Miner deployed and running** (you've completed this!)
✅ **API accessible** at `http://134.199.203.133:8080`
✅ **HTTPS tunnel** (required for playground)

## Step 1: Set Up HTTPS Tunnel

The playground requires HTTPS. Set up a Cloudflare Tunnel:

### On Your Droplet:

```bash
# Install cloudflared (if not already installed)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Start tunnel (this will give you an HTTPS URL)
cloudflared tunnel --url http://localhost:8080
```

You'll see output like:
```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at:                                         |
|  https://abc123-def456-ghi789.trycloudflare.com                                           |
+--------------------------------------------------------------------------------------------+
```

**Copy that HTTPS URL** - you'll need it for the playground!

### Keep Tunnel Running

To keep the tunnel running in the background:

```bash
# Run in screen/tmux or as systemd service
screen -S tunnel
cloudflared tunnel --url http://localhost:8080
# Press Ctrl+A then D to detach

# Or use the provided script
bash START_TUNNEL.sh
```

## Step 2: Test on Playground

1. **Go to**: https://infinitewebarena.autoppia.com/playground

2. **Configure Benchmark**:
   - **Select Web Projects**: Choose one or more projects to test
   - **Select Use Cases**: Choose specific use cases
   - **Number of Runs**: Start with 1-3 runs for testing
   - **Agent Endpoint**: Enter your endpoint in one of these formats:
     - Domain only: `abc123-def456-ghi789.trycloudflare.com` (no https://)
     - Or IP:port: `134.199.203.133:8080` (if using direct HTTP)
     - Note: Try domain first, if that doesn't work, use IP:port format

3. **Click "Run Benchmark"**

4. **Monitor Results**:
   - Watch for task execution
   - Check success rates
   - Review action generation

## Step 3: Verify Results

### What to Look For

✅ **Success Indicators**:
- Tasks completing successfully
- Actions being generated
- No "Failed to fetch" errors
- Success rate > 0%

❌ **Common Issues**:
- "Failed to call benchmark API: Failed to fetch" → HTTPS tunnel not working
- Empty actions → Check API logs
- Timeout errors → Check API response time

### Check Logs

While testing, monitor your API logs:

```bash
# On your droplet
journalctl -u autoppia-api -f
```

You should see:
- POST requests to `/solve_task`
- Action generation
- Response times

## Troubleshooting

### "Failed to fetch" Error

**Cause**: HTTPS tunnel not accessible or CORS issues

**Fix**:
1. Verify tunnel is running: `ps aux | grep cloudflared`
2. Test tunnel URL: `curl https://your-tunnel-url.trycloudflare.com/health`
3. Check CORS headers in API response

### Empty Actions

**Cause**: API not generating actions correctly

**Fix**:
1. Check API logs: `journalctl -u autoppia-api -n 50`
2. Test API directly: `curl -X POST http://localhost:8080/solve_task ...`
3. Verify action generation is working

### Timeout Errors

**Cause**: API taking too long to respond

**Fix**:
1. Check API response time
2. Optimize action generation
3. Reduce number of actions if needed

## Expected Behavior

### Successful Test

- ✅ Playground connects to your API
- ✅ Tasks are sent to your API
- ✅ Actions are generated and returned
- ✅ Tasks complete (even if not 100% success)
- ✅ No errors in playground console

### Sample Test Configuration

For initial testing:
- **Projects**: Select 1-2 simple projects
- **Use Cases**: Choose basic use cases (click, navigate)
- **Runs**: 1-3 runs
- **Endpoint**: Your HTTPS tunnel URL

## Next Steps

After successful playground testing:

1. **Monitor Validator Activity**:
   ```bash
   bash MONITOR_VALIDATORS.sh
   ```

2. **Check Overnight Activity**:
   ```bash
   bash CHECK_OVERNIGHT_ACTIVITY.sh
   ```

3. **Optimize Based on Results**:
   - Improve selector strategies
   - Adjust wait times
   - Enhance action generation

## Quick Reference

**Playground URL**: https://infinitewebarena.autoppia.com/playground

**Your API**: `http://134.199.203.133:8080` (HTTP)
**HTTPS Tunnel**: `https://your-tunnel-url.trycloudflare.com` (use this in playground)

**Monitor**: `journalctl -u autoppia-api -f`

