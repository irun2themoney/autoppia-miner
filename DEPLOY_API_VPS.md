# 🚀 Deploy HTTP API to VPS (For InfiniteWeb Arena Testing)

## Why Deploy API to VPS?

- ✅ **Direct IP access** - No Cloudflare blocking (works with `ip:port` format)
- ✅ **24/7 operation** - Always available for testing
- ✅ **Platform compatible** - Works with InfiniteWeb Arena's endpoint format
- ✅ **Full control** - No hosting restrictions

## Quick Setup Guide

### 1. Choose a VPS Provider

**Recommended (Cheapest):**
- **Hetzner**: €4-8/month (best value, EU-based)
- **DigitalOcean**: $6-12/month (US-based)
- **Linode**: $5-10/month
- **Vultr**: $6-12/month
- **AWS EC2**: Pay as you go (free tier available)

### 2. Set Up VPS

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install python3 python3-pip git curl ufw -y

# Clone your repository
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner

# Install Python dependencies
pip3 install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment file
cp env.example .env

# Edit .env with your settings
nano .env
```

Set these values:
```ini
# Required
CHUTES_API_KEY=your_chutes_api_key_here

# Optional (defaults shown)
CHUTES_API_URL=https://api.chutes.ai
WORKER_NAME=autoppia-miner
LOG_LEVEL=INFO

# For VPS deployment, set API_URL to your VPS IP
# We'll get the IP in the next step
```

### 4. Get Your VPS Public IP

```bash
# Get your public IP address
curl -4 ifconfig.me
# Or
curl ifconfig.me
# Or
hostname -I | awk '{print $1}'
```

**Save this IP!** You'll need it for:
- Setting `API_URL` in `.env` (if running miner on VPS)
- Testing the endpoint
- Configuring in InfiniteWeb Arena platform

### 5. Configure Firewall

```bash
# Allow SSH (important - don't lock yourself out!)
ufw allow 22/tcp

# Allow HTTP API port (default 8080)
ufw allow 8080/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

### 6. Test API Locally First

```bash
# Start API server manually
python3 api.py

# In another terminal, test it
curl http://localhost:8080/health

# Test solve_task endpoint
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id": "test", "prompt": "Click button", "url": "https://example.com"}'
```

If it works, press `Ctrl+C` to stop and continue to next step.

### 7. Set Up Systemd Service (Auto-Start)

```bash
# Create service file
nano /etc/systemd/system/autoppia-api.service
```

Add this content (adjust paths as needed):
```ini
[Unit]
Description=Autoppia HTTP API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/autoppia-miner
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="PORT=8080"
ExecStart=/usr/bin/python3 /root/autoppia-miner/api.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
# Reload systemd
systemctl daemon-reload

# Enable service (starts on boot)
systemctl enable autoppia-api

# Start service
systemctl start autoppia-api

# Check status
systemctl status autoppia-api

# View logs
journalctl -u autoppia-api -f
```

### 8. Test External Access

From your local machine (not VPS):

```bash
# Replace YOUR_VPS_IP with your actual VPS IP
YOUR_VPS_IP="your-vps-ip-here"

# Test health endpoint
curl http://$YOUR_VPS_IP:8080/health

# Test solve_task endpoint
curl -X POST http://$YOUR_VPS_IP:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test",
    "prompt": "Register with username testuser",
    "url": "https://example.com"
  }'
```

### 9. Configure in InfiniteWeb Arena

1. Go to [InfiniteWeb Arena](https://infinitewebarena.autoppia.com/)
2. Navigate to "Benchmark Your Agent"
3. Enter your endpoint as: `YOUR_VPS_IP:8080`
   - Example: `123.45.67.89:8080`
4. Run your benchmark!

## Alternative: Run on Different Port

If you want to use port 80 (standard HTTP):

```bash
# Edit service file
nano /etc/systemd/system/autoppia-api.service
```

Change the port:
```ini
Environment="PORT=80"
```

Update firewall:
```bash
ufw allow 80/tcp
```

Restart service:
```bash
systemctl restart autoppia-api
```

Then use: `YOUR_VPS_IP:80` in the platform.

## Monitoring

### View Logs
```bash
# Follow logs in real-time
journalctl -u autoppia-api -f

# View last 100 lines
journalctl -u autoppia-api -n 100

# View logs since today
journalctl -u autoppia-api --since today
```

### Check Status
```bash
# Service status
systemctl status autoppia-api

# Check if port is listening
netstat -tlnp | grep 8080
# Or
ss -tlnp | grep 8080
```

### Test Endpoint
```bash
# Health check
curl http://localhost:8080/health

# Metrics
curl http://localhost:8080/metrics

# Test task solving
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id": "test", "prompt": "test", "url": "https://example.com"}'
```

## Troubleshooting

### Service won't start
```bash
# Check logs for errors
journalctl -u autoppia-api -n 50

# Check if port is already in use
netstat -tlnp | grep 8080

# Test manually
cd /root/autoppia-miner
python3 api.py
```

### Can't access from outside
```bash
# Check firewall
ufw status

# Check if service is listening on 0.0.0.0
netstat -tlnp | grep 8080
# Should show: 0.0.0.0:8080 (not 127.0.0.1:8080)

# Check VPS provider firewall
# (DigitalOcean, Hetzner, etc. have their own firewalls)
```

### API returns errors
```bash
# Check environment variables
cat .env

# Check if CHUTES_API_KEY is set
grep CHUTES_API_KEY .env

# View detailed logs
journalctl -u autoppia-api -f
```

## Security Best Practices

1. **Use SSH keys** (not passwords)
   ```bash
   # On local machine
   ssh-copy-id root@your-vps-ip
   ```

2. **Keep system updated**
   ```bash
   apt update && apt upgrade -y
   ```

3. **Configure firewall properly**
   ```bash
   # Only allow necessary ports
   ufw allow 22/tcp   # SSH
   ufw allow 8080/tcp # API
   ufw enable
   ```

4. **Use non-root user** (optional, advanced)
   ```bash
   # Create user
   adduser autoppia
   # Configure service to run as this user
   ```

5. **Monitor logs regularly**
   ```bash
   # Set up log rotation
   # Check for suspicious activity
   ```

## Cost Estimate

- **VPS**: $5-12/month
- **Bandwidth**: Usually included
- **Total**: ~$5-12/month for 24/7 API availability

## Next Steps

1. ✅ Deploy API to VPS
2. ✅ Test endpoint works
3. ✅ Configure in InfiniteWeb Arena
4. ✅ Run benchmarks
5. ✅ Monitor performance

## Support

If you encounter issues:
1. Check logs: `journalctl -u autoppia-api -f`
2. Test locally first: `python3 api.py`
3. Verify firewall: `ufw status`
4. Check VPS provider's firewall settings

