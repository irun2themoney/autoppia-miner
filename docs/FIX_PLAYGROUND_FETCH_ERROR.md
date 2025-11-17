# Fix "Failed to call benchmark API: Failed to fetch" Error

## Quick Fix Steps

### Step 1: Verify HTTPS Tunnel is Running

```bash
ssh root@134.199.203.133 'ps aux | grep cloudflared | grep -v grep'
```

If not running, start it:
```bash
ssh root@134.199.203.133 'screen -dmS tunnel bash -c "cloudflared tunnel --url http://localhost:8080 2>&1 | tee /tmp/cloudflared.log"'
```

### Step 2: Get Current Tunnel URL

```bash
ssh root@134.199.203.133 'grep -oP "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cloudflared.log | tail -1'
```

Or check the screen session:
```bash
ssh root@134.199.203.133 'screen -r tunnel'
```

### Step 3: Test Tunnel URL

```bash
# Test health endpoint
curl https://YOUR-TUNNEL-URL.trycloudflare.com/health

# Test CORS
curl -X OPTIONS https://YOUR-TUNNEL-URL.trycloudflare.com/solve_task \
  -H "Origin: https://infinitewebarena.autoppia.com" \
  -H "Access-Control-Request-Method: POST" -I
```

### Step 4: Use Correct Endpoint Format in Playground

**Option 1: HTTPS Tunnel (Recommended)**
- Enter: `YOUR-TUNNEL-URL.trycloudflare.com` (without `https://`)
- Example: `got-pen-mass-subdivision.trycloudflare.com`

**Option 2: Direct IP (May not work due to mixed content)**
- Enter: `134.199.203.133:8080`
- Note: Playground runs on HTTPS, so HTTP endpoints may be blocked

### Step 5: Verify API is Accessible

Test from your browser console (on the playground page):
```javascript
fetch('https://YOUR-TUNNEL-URL.trycloudflare.com/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

## Common Issues

### Issue 1: Tunnel URL Changed
**Solution**: Get the latest tunnel URL and update in playground

### Issue 2: Mixed Content (HTTP from HTTPS page)
**Solution**: Use HTTPS tunnel URL, not direct IP

### Issue 3: CORS Not Working
**Solution**: Verify CORS headers are present:
```bash
curl -X OPTIONS https://YOUR-TUNNEL-URL.trycloudflare.com/solve_task \
  -H "Origin: https://infinitewebarena.autoppia.com" \
  -H "Access-Control-Request-Method: POST" -I
```

Should return:
```
access-control-allow-origin: *
access-control-allow-methods: GET, POST, OPTIONS
```

### Issue 4: Firewall Blocking
**Solution**: Check firewall on server:
```bash
ssh root@134.199.203.133 'ufw status'
```

If port 8080 is blocked, open it:
```bash
ssh root@134.199.203.133 'ufw allow 8080/tcp && ufw reload'
```

## Quick Test Script

```bash
#!/bin/bash
TUNNEL_URL=$(ssh root@134.199.203.133 'grep -oP "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cloudflared.log | tail -1')
echo "Tunnel URL: $TUNNEL_URL"
echo ""
echo "Testing health endpoint..."
curl -s "$TUNNEL_URL/health" | python3 -m json.tool
echo ""
echo "Testing CORS..."
curl -s -X OPTIONS "$TUNNEL_URL/solve_task" \
  -H "Origin: https://infinitewebarena.autoppia.com" \
  -H "Access-Control-Request-Method: POST" -I | grep -i "access-control"
```

## Still Not Working?

1. **Check browser console** for detailed error messages
2. **Test tunnel URL directly** in browser
3. **Verify API is running**: `ssh root@134.199.203.133 'systemctl status autoppia-api'`
4. **Check API logs**: `ssh root@134.199.203.133 'journalctl -u autoppia-api -n 50'`

