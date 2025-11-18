# Fix "Failed to fetch" - HTTPS Playground Issue

## 🔍 The Problem

The IWA Playground runs on **HTTPS** (`https://infinitewebarena.autoppia.com`), and browsers block HTTP requests from HTTPS pages due to **mixed content security policies**.

When you use `134.199.203.133:8080` (HTTP), the browser blocks it.

## ✅ The Solution

Use an **HTTPS tunnel** to make your HTTP API accessible via HTTPS.

### Step 1: Get Your HTTPS Tunnel URL

The tunnel is already running. Get the URL:

```bash
ssh root@134.199.203.133 'grep -oP "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cloudflared.log | head -1'
```

Or check the screen session:
```bash
ssh root@134.199.203.133 'screen -r tunnel'
```

### Step 2: Use Tunnel URL in Playground

In the IWA Playground, enter the tunnel URL **without** `https://`:

```
got-pen-mass-subdivision.trycloudflare.com
```

(Replace with your actual tunnel URL)

### Step 3: Verify Tunnel is Working

Test the tunnel URL:
```bash
curl https://YOUR-TUNNEL-URL.trycloudflare.com/health
```

Should return:
```json
{"status":"healthy",...}
```

## 🔧 If Tunnel is Not Running

Start it:
```bash
ssh root@134.199.203.133 << 'EOF'
pkill cloudflared || true
screen -dmS tunnel bash -c 'cloudflared tunnel --url http://localhost:8080 2>&1 | tee /tmp/cloudflared.log'
sleep 5
grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflared.log | head -1
EOF
```

## 📝 Quick Reference

**Problem**: Playground (HTTPS) can't call HTTP API (mixed content)

**Solution**: Use HTTPS tunnel URL

**Format in Playground**: `domain.trycloudflare.com` (no `https://`)

**Example**: `got-pen-mass-subdivision.trycloudflare.com`

## 🎯 Alternative: Direct IP (May Not Work)

Some playgrounds might accept direct IP if they proxy the request. Try:
```
134.199.203.133:8080
```

But if you get "Failed to fetch", you **must** use the HTTPS tunnel.

