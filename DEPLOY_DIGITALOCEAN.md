# 🚀 Deploy to DigitalOcean VPS

## Quick Setup Guide for DigitalOcean

### 1. Create a Droplet

1. **Log into DigitalOcean**: https://cloud.digitalocean.com
2. **Click "Create" → "Droplets"**
3. **Choose configuration**:
   - **Image**: Ubuntu 22.04 LTS (recommended)
   - **Plan**: Basic - Regular Intel with SSD
   - **CPU**: 1 vCPU, 1GB RAM ($6/month) - **Minimum recommended**
   - **Datacenter**: Choose closest to you
   - **Authentication**: SSH keys (recommended) or root password
4. **Click "Create Droplet"**

### 2. Get Your Droplet IP

After creation, you'll see your droplet's IP address. **Save this IP!**

Example: `157.230.123.45`

### 3. SSH into Your Droplet

```bash
# If using SSH key (recommended)
ssh root@YOUR_DROPLET_IP

# If using password
ssh root@YOUR_DROPLET_IP
# Enter password when prompted
```

### 4. Deploy the API

#### Option A: Automated (Recommended)

```bash
# Clone repository
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner

# Make script executable
chmod +x deploy_api_vps.sh

# Run deployment script
sudo ./deploy_api_vps.sh
```

The script will:
- ✅ Install all dependencies
- ✅ Configure firewall
- ✅ Set up systemd service
- ✅ Start the API server
- ✅ Show your public IP

#### Option B: Manual Setup

Follow the detailed guide in [DEPLOY_API_VPS.md](./DEPLOY_API_VPS.md)

### 5. Configure Environment Variables

```bash
# Edit environment file
nano .env
```

Set your Chutes API key:
```ini
CHUTES_API_KEY=your_chutes_api_key_here
CHUTES_API_URL=https://api.chutes.ai
WORKER_NAME=autoppia-miner
LOG_LEVEL=INFO
```

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

### 6. Restart Service (if needed)

```bash
# Restart to load new environment variables
systemctl restart autoppia-api

# Check status
systemctl status autoppia-api
```

### 7. Configure DigitalOcean Firewall (Important!)

DigitalOcean has a cloud firewall that might block your port:

1. **Go to**: DigitalOcean Dashboard → Networking → Firewalls
2. **Create Firewall** (or edit existing):
   - **Inbound Rules**:
     - SSH (22) - Allow
     - Custom TCP (8080) - Allow - Source: All IPv4, All IPv6
   - **Outbound Rules**: Allow all
3. **Apply to your droplet**

**OR** use UFW (already configured by script):
```bash
# Check UFW status
ufw status

# Should show:
# 22/tcp    ALLOW
# 8080/tcp  ALLOW
```

### 8. Test Your Endpoint

From your local machine:

```bash
# Replace with your droplet IP
DROPLET_IP="your-droplet-ip-here"

# Test health endpoint
curl http://$DROPLET_IP:8080/health

# Test solve_task endpoint
curl -X POST http://$DROPLET_IP:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test",
    "prompt": "Click button",
    "url": "https://example.com"
  }'
```

### 9. Use in InfiniteWeb Arena

1. Go to: https://infinitewebarena.autoppia.com/
2. Navigate to "Benchmark Your Agent"
3. Enter endpoint: `YOUR_DROPLET_IP:8080`
   - Example: `157.230.123.45:8080`
4. Run your benchmark!

## Monitoring

### View Logs
```bash
# Real-time logs
journalctl -u autoppia-api -f

# Last 100 lines
journalctl -u autoppia-api -n 100
```

### Check Status
```bash
# Service status
systemctl status autoppia-api

# Check if port is listening
netstat -tlnp | grep 8080
```

### Restart Service
```bash
systemctl restart autoppia-api
```

## Troubleshooting

### Can't SSH into droplet
- Check DigitalOcean dashboard for droplet status
- Verify SSH key is added to your account
- Try: `ssh -v root@YOUR_IP` for verbose output

### API not accessible from outside
1. **Check UFW firewall**:
   ```bash
   ufw status
   # Should show 8080/tcp ALLOW
   ```

2. **Check DigitalOcean Cloud Firewall**:
   - Dashboard → Networking → Firewalls
   - Ensure port 8080 is open

3. **Check if service is running**:
   ```bash
   systemctl status autoppia-api
   ```

4. **Check if port is listening**:
   ```bash
   netstat -tlnp | grep 8080
   # Should show: 0.0.0.0:8080
   ```

### Service won't start
```bash
# Check logs
journalctl -u autoppia-api -n 50

# Check if .env file exists
ls -la .env

# Test manually
cd /root/autoppia-miner
python3 api.py
```

### API returns errors
```bash
# Check environment variables
cat .env

# Verify CHUTES_API_KEY is set
grep CHUTES_API_KEY .env

# View detailed logs
journalctl -u autoppia-api -f
```

## Cost Estimate

- **Droplet**: $6/month (1 vCPU, 1GB RAM)
- **Bandwidth**: 1TB included (more than enough)
- **Total**: ~$6/month for 24/7 API availability

## Security Best Practices

1. **Use SSH keys** (not passwords)
   - Add your SSH key in DigitalOcean dashboard
   - Or: `ssh-copy-id root@YOUR_IP` from local machine

2. **Keep system updated**
   ```bash
   apt update && apt upgrade -y
   ```

3. **Configure firewall properly**
   - UFW is already configured by script
   - DigitalOcean cloud firewall adds extra layer

4. **Monitor logs regularly**
   ```bash
   journalctl -u autoppia-api -f
   ```

## Next Steps

1. ✅ Create droplet
2. ✅ Deploy API
3. ✅ Test endpoint
4. ✅ Configure in InfiniteWeb Arena
5. ✅ Run benchmarks
6. ✅ Monitor performance

## Support

If you encounter issues:
1. Check logs: `journalctl -u autoppia-api -f`
2. Verify firewall: `ufw status`
3. Test locally: `curl http://localhost:8080/health`
4. Check DigitalOcean cloud firewall settings

