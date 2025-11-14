# 🌐 InfiniteWeb Arena Configuration Guide

## Agent Endpoint Configuration

### ✅ Correct Format

In the **"Agent Endpoint (IP:Port)"** field, enter:

```
134.199.201.62:8080
```

**OR** (with protocol):

```
http://134.199.201.62:8080
```

### ❌ Wrong Format

- `134.199.201.62` ❌ (missing port)
- `https://134.199.201.62:8080` ❌ (use http, not https)
- `134.199.201.62:80` ❌ (wrong port - API runs on 8080)

---

## Complete Configuration Steps

1. **Agent Endpoint**: `134.199.201.62:8080`
2. **Number of Runs**: Set to your desired number (e.g., 1, 5, 10)
3. **Select Web Projects**: Choose your projects (e.g., "AutoCinema")
4. **Select Use Cases**: Choose the use cases you want to test
5. Click **"Run Benchmark"**

---

## Verify Your Endpoint is Working

Before running the benchmark, verify your API is accessible:

```bash
# Test from your local machine
curl http://134.199.201.62:8080/health

# Should return:
# {"status":"healthy","worker":"autoppia-miner",...}
```

---

## Troubleshooting

### If you get "Connection refused" or timeout:

1. **Check if API is running on VPS**:
   ```bash
   ssh root@134.199.201.62
   systemctl status autoppia-api
   ```

2. **Check if port 8080 is open**:
   ```bash
   # On VPS
   sudo ufw status
   # Should show: 8080/tcp ALLOW
   ```

3. **Check DigitalOcean Firewall**:
   - Go to: https://cloud.digitalocean.com/networking/firewalls
   - Ensure port 8080 is open for inbound traffic

4. **Test locally on VPS**:
   ```bash
   # SSH into VPS
   curl http://localhost:8080/health
   ```

---

## Quick Fix

**Just change the endpoint field to:**
```
134.199.201.62:8080
```

Then click "Run Benchmark" again!

