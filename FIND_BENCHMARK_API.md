# Finding the Benchmark API

## Understanding the Benchmark System

### There is NO separate "Benchmark API"

The "benchmark API" **IS your miner's API endpoint** (`/solve_task`). Here's how it works:

## How Validators Test Your Miner

### Flow Diagram

```
Validator
   ↓
Discovers your miner via Bittensor metagraph
   ↓
Gets your API URL from miner metadata (axon endpoint)
   ↓
Calls: POST http://your-api-url/solve_task
   ↓
Your API responds with actions
   ↓
Validator executes actions and scores results
```

### Your API Endpoint IS the Benchmark API

**Endpoint**: `POST /solve_task`

**Your URLs**:
- Local: `http://localhost:8080/solve_task`
- Public: `http://134.199.203.133:8080/solve_task`
- HTTPS: `https://your-tunnel-url.trycloudflare.com/solve_task`

## Where to Find Information

### 1. Autoppia Documentation
- **URL**: https://luxit.gitbook.io/autoppia-docs
- **What to look for**: 
  - "ApifiedWebAgent" pattern
  - Validator testing process
  - Benchmark scoring

### 2. GitHub Repositories

#### Autoppia Web Agents Subnet
- **URL**: https://github.com/autoppia/autoppia_web_agents_subnet
- **What to look for**:
  - Validator code
  - How validators discover miner APIs
  - Benchmark scoring logic

#### IWA Module
- **URL**: https://github.com/autoppia/autoppia_iwa
- **What to look for**:
  - `ApifiedWebAgent` implementation
  - Task execution
  - Action format

### 3. IWA Playground (Testing Tool)

**URL**: https://infinitewebarena.autoppia.com/playground

**How to inspect**:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Enter your API endpoint
4. Click "Run Benchmark"
5. Watch the network requests - you'll see it calling your `/solve_task` endpoint

### 4. Your Miner's Axon Metadata

Validators discover your API URL through your miner's axon metadata:

```python
# In miner/miner.py
self.axon = bt.axon(
    wallet=self.wallet,
    port=self.config.axon.port,  # 8091
)
```

The axon exposes metadata that validators read to find your API endpoint.

## How to Verify Your API is Being Called

### Monitor API Logs

```bash
# On your droplet
journalctl -u autoppia-api -f | grep solve_task
```

You should see:
- POST requests to `/solve_task`
- Request data (id, prompt, url)
- Response times

### Monitor Miner Logs

```bash
# On your droplet
journalctl -u autoppia-miner -f
```

You should see:
- Synapse processing
- Forward calls to API
- Validator connections

### Check Validator Activity

```bash
# On your droplet
bash CHECK_VALIDATOR_ACTIVITY.sh
```

## Testing Your Benchmark API

### 1. Local Test

```bash
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-123",
    "prompt": "Click the submit button",
    "url": "https://example.com"
  }'
```

### 2. Public Test

```bash
curl -X POST http://134.199.203.133:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-123",
    "prompt": "Click the submit button",
    "url": "https://example.com"
  }'
```

### 3. Playground Test

1. Go to: https://infinitewebarena.autoppia.com/playground
2. Enter: `134.199.203.133:8080`
3. Click "Run Benchmark"
4. Watch your API logs to see requests

## Key Points

✅ **Your API endpoint IS the benchmark API**
- Validators call your `/solve_task` endpoint
- No separate benchmark API exists
- The IWA Playground is just a testing tool

✅ **Validators discover your API via**:
- Bittensor metagraph
- Miner axon metadata
- Your miner's registered endpoint

✅ **To find more details**:
- Check Autoppia GitHub repos
- Read Autoppia documentation
- Inspect IWA Playground network requests
- Monitor your API logs

## Next Steps

1. **Verify your API is accessible**:
   ```bash
   curl http://134.199.203.133:8080/health
   ```

2. **Test your endpoint**:
   ```bash
   curl -X POST http://134.199.203.133:8080/solve_task \
     -H "Content-Type: application/json" \
     -d '{"id":"test","prompt":"test","url":"https://example.com"}'
   ```

3. **Monitor for validator calls**:
   ```bash
   journalctl -u autoppia-api -f
   ```

4. **Check GitHub repos** for validator implementation details

## Summary

**The benchmark API = Your `/solve_task` endpoint**

Validators call YOUR API directly. There's no separate benchmark API - your miner's API IS the benchmark API that validators use to test your miner.

