# IWA Benchmark API Information

## Current Understanding

### Your Miner's API Endpoint

**Endpoint**: `POST /solve_task`

**Location**: 
- Local: `http://localhost:8080/solve_task`
- Public: `http://134.199.203.133:8080/solve_task`
- HTTPS Tunnel: `https://your-tunnel-url.trycloudflare.com/solve_task`

**Request Format**:
```json
{
  "id": "task-id",
  "prompt": "Task description",
  "url": "https://example.com"
}
```

**Response Format**:
```json
{
  "actions": [...],
  "web_agent_id": "task-id",
  "recording": "",
  "id": "task-id",
  "task_id": "task-id"
}
```

## How Validators Test Your Miner

### Method 1: Direct API Call (ApifiedWebAgent Pattern)

Validators call your miner's API endpoint directly:

1. **Validator discovers your miner** via Bittensor metagraph
2. **Validator gets your API URL** from miner metadata (axon endpoint)
3. **Validator calls** `POST http://your-api-url/solve_task`
4. **Your API responds** with actions
5. **Validator executes** actions and scores results

### Method 2: Via Bittensor Synapse

1. **Validator sends synapse** to your miner's axon (port 8091)
2. **Your miner receives** synapse with task data
3. **Miner forwards** to local API (`http://localhost:8080/solve_task`)
4. **API generates** actions
5. **Miner returns** actions in synapse response
6. **Validator scores** the response

## Finding the Official Benchmark API

### IWA Playground
- **URL**: https://infinitewebarena.autoppia.com/playground
- **Purpose**: Test your miner's API endpoint
- **How it works**: You provide your API URL, it calls `/solve_task`

### Autoppia Documentation
- **Docs**: https://luxit.gitbook.io/autoppia-docs
- **IWA Module**: https://github.com/autoppia/autoppia_iwa
- **Subnet Repo**: https://github.com/autoppia/autoppia_web_agents_subnet

### What We Need to Find

1. **Official Benchmark API Endpoint** (if there is one)
2. **How validators discover miner API URLs**
3. **Benchmark scoring mechanism**
4. **Task generation source**

## Next Steps to Find Benchmark API

1. **Check Autoppia Documentation**
   - Review: https://luxit.gitbook.io/autoppia-docs
   - Look for "benchmark API" or "validator testing"

2. **Check GitHub Repositories**
   - https://github.com/autoppia/autoppia_web_agents_subnet
   - https://github.com/autoppia/autoppia_iwa
   - Look for validator code or benchmark API code

3. **Check IWA Playground Source**
   - Inspect network requests in browser dev tools
   - See what API endpoints it calls

4. **Check Miner Logs**
   - Look for validator requests
   - See what endpoints validators are calling
   - Check request patterns

## Current Status

✅ **Your API is set up correctly**:
- Endpoint: `/solve_task` ✅
- Format: IWA BaseAction format ✅
- CORS: Enabled ✅
- Response: Correct structure ✅

❓ **What we need to find**:
- Official benchmark API endpoint (if separate)
- How validators discover your API
- Benchmark scoring details
- Task generation source

## Testing Your API

### Local Test
```bash
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id":"test-123","prompt":"Click button","url":"https://example.com"}'
```

### Playground Test
1. Go to: https://infinitewebarena.autoppia.com/playground
2. Enter your API endpoint: `134.199.203.133:8080`
3. Run benchmark
4. Check results

### Monitor Validator Calls
```bash
# Watch for validator requests
journalctl -u autoppia-api -f | grep solve_task
```

