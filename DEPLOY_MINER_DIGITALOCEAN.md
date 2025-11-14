# 🚀 Deploy Bittensor Miner to DigitalOcean

Complete guide for deploying your Autoppia Bittensor miner to DigitalOcean for 24/7 operation.

## Architecture Overview

```
Validator → Bittensor Network → Your Miner (DigitalOcean) → HTTP API (DigitalOcean) → Response
```

**What runs where:**
- ✅ **HTTP API** (`api.py`) → Runs on DigitalOcean VPS (port 8080)
- ✅ **Bittensor Miner** (`miner.py`) → Runs on DigitalOcean VPS (port 8091)

## Prerequisites

1. **DigitalOcean Account**: [Sign up](https://cloud.digitalocean.com)
2. **TAO Tokens**: Required for subnet registration
3. **Bittensor Wallet**: Created and funded
4. **API Endpoint**: Your HTTP API running (Render or VPS)

## Quick Setup (5 Minutes)

### 1. Create a DigitalOcean Droplet

1. **Log into DigitalOcean**: https://cloud.digitalocean.com
2. **Click "Create" → "Droplets"**
3. **Choose configuration**:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic - Regular Intel with SSD
   - **CPU**: 1 vCPU, 1GB RAM ($6/month) - **Minimum recommended**
   - **Datacenter**: Choose closest to you
   - **Authentication**: SSH keys (recommended)
4. **Click "Create Droplet"**
5. **Save your droplet IP address**

### 2. SSH into Your Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

### 3. Run Deployment Script

```bash
# Clone and run deployment
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner
chmod +x deploy_miner_digitalocean.sh

# Run deployment (default wallet/hotkey: default/default)
sudo ./deploy_miner_digitalocean.sh

# OR specify wallet and hotkey
sudo ./deploy_miner_digitalocean.sh my_wallet my_hotkey finney
```

The script will:
- ✅ Install all dependencies
- ✅ Set up the miner as a systemd service
- ✅ Configure firewall
- ✅ Check wallet registration
- ✅ Start the miner automatically

### 4. Configure Environment Variables

During deployment, you'll be prompted to configure `.env`:

```bash
nano .env
```

Set these values:
```ini
CHUTES_API_KEY=your_chutes_api_key_here
CHUTES_API_URL=https://api.chutes.ai
API_URL=https://autoppia-miner.onrender.com
WORKER_NAME=autoppia-miner
LOG_LEVEL=INFO
```

**Important**: `API_URL` should point to your HTTP API (Render or VPS).

### 5. Set Up Wallet

**Option A: Copy wallet from local machine** (Recommended)
```bash
# From your local machine
scp -r ~/.bittensor/wallets/default root@YOUR_DROPLET_IP:~/.bittensor/wallets/
```

**Option B: Create new wallet on VPS**
```bash
# On the VPS
btcli wallet create --name default
```

### 6. Register on Subnet 36

If not already registered:
```bash
btcli subnet register \
  --netuid 36 \
  --wallet.name default \
  --wallet.hotkey default
```

⚠️ **This requires TAO tokens for registration fees.**

### 7. Configure DigitalOcean Firewall

**Critical Step!** Validators need to reach your miner's axon port.

1. **Go to**: DigitalOcean Dashboard → Networking → Firewalls
2. **Create Firewall** (or edit existing):
   - **Inbound Rules**:
     - SSH (22) - Allow
     - Custom TCP (8091) - Allow - Source: All IPv4, All IPv6
   - **Outbound Rules**: Allow all
3. **Apply to your droplet**

**OR** use UFW (already configured by script):
```bash
ufw status
# Should show: 8091/tcp ALLOW
```

### 8. Verify Miner is Running

```bash
# Check service status
systemctl status autoppia-miner

# View logs
journalctl -u autoppia-miner -f

# Check Bittensor registration
btcli wallet overview --netuid 36 --wallet.name default --wallet.hotkey default
```

You should see:
- ✅ Service status: `active (running)`
- ✅ Logs showing: "Miner serving on network!"
- ✅ UID displayed in wallet overview

## Monitoring

### View Real-Time Logs
```bash
journalctl -u autoppia-miner -f
```

### Check Miner Status
```bash
# Service status
systemctl status autoppia-miner

# Bittensor network status
btcli wallet overview --netuid 36

# Check if axon port is listening
netstat -tlnp | grep 8091
```

### Restart Miner
```bash
systemctl restart autoppia-miner
```

## Troubleshooting

### Miner not starting

**Check logs:**
```bash
journalctl -u autoppia-miner -n 50
```

**Common issues:**
1. **Wallet not found**: Copy wallet files or create new wallet
2. **Not registered**: Register on subnet 36 first
3. **API_URL incorrect**: Check `.env` file
4. **Port blocked**: Configure DigitalOcean firewall

### Validators can't reach miner

1. **Check firewall**:
   ```bash
   ufw status
   # Should show 8091/tcp ALLOW
   ```

2. **Check DigitalOcean Cloud Firewall**:
   - Dashboard → Networking → Firewalls
   - Ensure port 8091 is open

3. **Check if port is listening**:
   ```bash
   netstat -tlnp | grep 8091
   # Should show: 0.0.0.0:8091
   ```

4. **Test from outside**:
   ```bash
   # From your local machine
   telnet YOUR_DROPLET_IP 8091
   ```

### Miner not receiving requests

1. **Check registration**:
   ```bash
   btcli wallet overview --netuid 36
   ```

2. **Check metagraph**:
   ```bash
   btcli metagraph --netuid 36
   ```

3. **Verify API is accessible**:
   ```bash
   curl https://autoppia-miner.onrender.com/health
   ```

4. **Check miner logs for errors**:
   ```bash
   journalctl -u autoppia-miner -f
   ```

### Service keeps restarting

**Check logs for errors:**
```bash
journalctl -u autoppia-miner -n 100
```

**Common causes:**
- Missing environment variables
- Wallet not found
- Network connectivity issues
- API endpoint unreachable

## Cost Estimate

- **Droplet**: $6/month (1 vCPU, 1GB RAM)
- **Bandwidth**: 1TB included (more than enough)
- **Total**: ~$6/month for 24/7 miner operation

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
   journalctl -u autoppia-miner -f
   ```

5. **Secure wallet files**
   - Wallet files are in `~/.bittensor/wallets/`
   - Keep backups of your wallet

## Architecture Details

### How It Works

1. **Miner connects** to Bittensor subnet 36
2. **Validators discover** your miner via metagraph
3. **Validators send tasks** to your miner's axon (port 8091)
4. **Miner forwards** tasks to HTTP API (`api.py` on Render)
5. **HTTP API processes** tasks and returns actions
6. **Miner sends** actions back to validators
7. **Validators evaluate** and reward you with TAO

### Ports Used

- **8091**: Axon port (validators connect here)
- **22**: SSH (for management)

### Files Created

- `/etc/systemd/system/autoppia-miner.service`: Systemd service
- `~/.bittensor/wallets/`: Wallet files (if created on VPS)
- `.env`: Environment configuration

## Next Steps

1. ✅ Deploy miner to DigitalOcean
2. ✅ Verify miner is running
3. ✅ Check registration on subnet 36
4. ✅ Monitor logs for validator requests
5. ✅ Track rewards on [taostats.io](https://taostats.io/subnets/36/)

## Support

- **Miner Logs**: `journalctl -u autoppia-miner -f`
- **Bittensor Docs**: https://docs.bittensor.com
- **Subnet 36 Stats**: https://taostats.io/subnets/36/
- **Autoppia Docs**: https://luxit.gitbook.io/autoppia-docs

## Quick Reference

```bash
# Start miner
systemctl start autoppia-miner

# Stop miner
systemctl stop autoppia-miner

# Restart miner
systemctl restart autoppia-miner

# View logs
journalctl -u autoppia-miner -f

# Check status
systemctl status autoppia-miner

# Check registration
btcli wallet overview --netuid 36

# Edit configuration
nano .env
systemctl restart autoppia-miner
```

