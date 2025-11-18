# ✅ Correct Playground Endpoint Format

## 🎯 Use This Format

The IWA Playground requires **`ip:port`** format (no `http://` or `https://`).

### ✅ Correct Endpoint:
```
134.199.203.133:8080
```

### ❌ Wrong Formats:
- `https://got-pen-mass-subdivision.trycloudflare.com` (tunnel URL not accepted)
- `http://134.199.203.133:8080` (don't include http://)
- `134.199.203.133` (missing port)

## 📝 How to Use in Playground

1. Go to: https://infinitewebarena.autoppia.com/playground

2. In the "Agent Endpoint" field, enter:
   ```
   134.199.203.133:8080
   ```

3. Click "Run Benchmark"

## ✅ Verification

- ✅ API is accessible at `http://134.199.203.133:8080`
- ✅ CORS headers are configured correctly
- ✅ Endpoint format matches playground requirements

## 🔍 If You Get "Failed to fetch"

If the playground still can't connect (due to HTTPS blocking HTTP), you have two options:

### Option 1: Use HTTPS Tunnel (Alternative)
Some playgrounds accept HTTPS tunnel URLs. If yours does, try:
```
got-pen-mass-subdivision.trycloudflare.com
```
(Without `https://`)

### Option 2: Check Firewall
Make sure port 8080 is open:
```bash
ssh root@134.199.203.133 'ufw status | grep 8080'
```

If not open:
```bash
ssh root@134.199.203.133 'ufw allow 8080/tcp && ufw reload'
```

## 🎯 Summary

**Use this exact format in the playground:**
```
134.199.203.133:8080
```

That's it! No `http://`, no `https://`, just `ip:port`.

