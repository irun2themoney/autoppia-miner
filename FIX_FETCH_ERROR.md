# Fix "Failed to call benchmark API: Failed to fetch" Error

## Quick Diagnosis

This error means the IWA Playground cannot reach your API endpoint. Let's fix it step by step.

## Step 1: Verify API is Running

### On Your Droplet:

```bash
# Check API service status
systemctl status autoppia-api

# Check if API is listening
ss -tlnp | grep 8080
# OR
netstat -tlnp | grep 8080

# Test API locally
curl http://localhost:8080/health
```

**Expected**: Should return `{"status":"healthy",...}`

## Step 2: Verify API is Publicly Accessible

### From Your Local Machine:

```bash
# Test public access
curl http://134.199.203.133:8080/health

# Test solve_task endpoint
curl -X POST http://134.199.203.133:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id":"test","prompt":"test","url":"https://example.com"}'
```

**If this fails**: API is not publicly accessible (firewall issue)

## Step 3: Check Firewall

### On Your Droplet:

```bash
# Check firewall status
ufw status

# If port 8080 is not open, open it:
ufw allow 8080/tcp
ufw reload

# Verify it's open
ufw status | grep 8080
```

## Step 4: Check CORS Configuration

The API must have CORS enabled for the playground to work.

### Verify CORS in `api/server.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Must allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Step 5: HTTPS vs HTTP Issue

The IWA Playground runs on HTTPS, so it may block HTTP API calls (mixed content).

### Solution 1: Use HTTPS Tunnel (Recommended)

```bash
# On your droplet, install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Start tunnel
cloudflared tunnel --url http://localhost:8080
```

This will give you an HTTPS URL like:
```
https://abc123-def456-ghi789.trycloudflare.com
```

**Use this HTTPS URL in the playground** (without `https://` prefix):
```
abc123-def456-ghi789.trycloudflare.com
```

### Solution 2: Use IP:Port Format

If the playground accepts HTTP, try:
```
134.199.203.133:8080
```

## Step 6: Verify Endpoint Format

The playground expects one of these formats:

1. **Domain only** (no protocol):
   ```
   abc123-def456-ghi789.trycloudflare.com
   ```

2. **IP:Port**:
   ```
   134.199.203.133:8080
   ```

3. **HTTP URL** (if accepted):
   ```
   http://134.199.203.133:8080
   ```

**Do NOT use**:
- `https://134.199.203.133:8080` (unless you have SSL certificate)
- `http://134.199.203.133:8080/solve_task` (playground adds `/solve_task`)

## Step 7: Test Endpoint Directly

### Test from Browser:

1. Open browser DevTools (F12)
2. Go to Console tab
3. Run:
   ```javascript
   fetch('http://134.199.203.133:8080/health')
     .then(r => r.json())
     .then(console.log)
     .catch(console.error)
   ```

If this fails, you'll see the exact error.

## Step 8: Check API Logs

### On Your Droplet:

```bash
# Watch API logs in real-time
journalctl -u autoppia-api -f

# Check recent errors
journalctl -u autoppia-api -n 50 --no-pager | grep -i error
```

Look for:
- Connection errors
- CORS errors
- Request failures

## Common Solutions

### Solution A: API Not Running

```bash
# Start API service
systemctl start autoppia-api
systemctl enable autoppia-api

# Check status
systemctl status autoppia-api
```

### Solution B: Firewall Blocking

```bash
# Open port 8080
ufw allow 8080/tcp
ufw reload

# Verify
ufw status | grep 8080
```

### Solution C: CORS Not Configured

Check `api/server.py` has CORS middleware configured (see Step 4).

### Solution D: HTTPS Required

Use Cloudflare Tunnel to get HTTPS URL (see Step 5).

### Solution E: Wrong Endpoint Format

Use IP:port format: `134.199.203.133:8080` (no http://)

## Quick Fix Checklist

- [ ] API service is running: `systemctl status autoppia-api`
- [ ] Port 8080 is open: `ufw status | grep 8080`
- [ ] API is accessible: `curl http://134.199.203.133:8080/health`
- [ ] CORS is configured in `api/server.py`
- [ ] Using correct endpoint format in playground
- [ ] HTTPS tunnel running (if needed): `ps aux | grep cloudflared`

## Still Not Working?

1. **Check API logs** for specific errors
2. **Test from browser console** to see exact error
3. **Try HTTPS tunnel** if using HTTP
4. **Verify endpoint format** matches playground requirements
5. **Check network connectivity** from playground location

## Expected Behavior

Once fixed, you should see:
- ✅ Playground connects to your API
- ✅ Tasks are sent to `/solve_task`
- ✅ Actions are returned
- ✅ No "Failed to fetch" errors

