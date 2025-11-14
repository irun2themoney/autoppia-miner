# 🚀 Autoppia Miner - Complete Deployment Guide

**Status:** ✅ Production Ready  
**Last Updated:** November 14, 2025  
**Tests:** 52/52 passing ✅

---

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [DigitalOcean VPS Setup](#digitalocean-setup)
3. [Manual Installation](#manual-installation)
4. [Configuration](#configuration)
5. [Verification & Monitoring](#verification)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Option 1: Automated DigitalOcean Deployment (Recommended)

```bash
# SSH into your DigitalOcean droplet
ssh root@YOUR_DROPLET_IP

# Clone and deploy (choose deployment mode)
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner

# Deploy API only
./deploy_to_do.sh API_ONLY

# OR deploy Miner only
./deploy_to_do.sh MINER_ONLY YOUR_WALLET YOUR_HOTKEY

# OR deploy both
./deploy_to_do.sh BOTH YOUR_WALLET YOUR_HOTKEY
```

### Option 2: Local Testing

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env

# Configure
nano .env  # Add your CHUTES_API_KEY

# Run API
python3 api.py

# In another terminal, run Miner
python3 miner.py --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY
```

---

## DigitalOcean Setup

### Step 1: Create a DigitalOcean Droplet

```bash
# Recommended specs:
# - OS: Ubuntu 22.04 (LTS)
# - Size: $4/month (Basic) minimum
# - Region: Choose closest to you
# - Memory: 512MB minimum, 1GB recommended
```

### Step 2: Initial Server Setup

```bash
# SSH into droplet
ssh root@YOUR_DROPLET_IP

# Update system
apt-get update
apt-get upgrade -y

# Install basic tools
apt-get install -y curl wget git build-essential python3-dev python3-pip
```

### Step 3: Automated Deployment

```bash
# Clone repository
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner

# Make script executable
chmod +x deploy_to_do.sh

# Run deployment
./deploy_to_do.sh BOTH default default

# OR with custom wallet
./deploy_to_do.sh BOTH my_wallet_name my_hotkey_name
```

### Step 4: Configure Environment

```bash
# Edit configuration
sudo nano /opt/autoppia-miner/.env

# Add your values:
CHUTES_API_KEY=your_api_key_here
API_URL=http://YOUR_DROPLET_IP:8000
WORKER_NAME=autoppia-miner
LOG_LEVEL=INFO
```

### Step 5: Start Services

```bash
# Start API server
sudo systemctl start autoppia-api

# Start Miner (requires Bittensor wallet)
sudo systemctl start autoppia-miner

# Enable auto-start on boot
sudo systemctl enable autoppia-api autoppia-miner
```

---

## Manual Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure

```bash
# Copy example configuration
cp env.example .env

# Edit with your settings
nano .env  # or use your preferred editor
```

### Step 5: Run Components

**Option A: API Server Only**

```bash
python3 api.py
# Server runs on http://localhost:8000
```

**Option B: Bittensor Miner**

```bash
# First, register on subnet 36 (requires TAO tokens)
btcli subnet register --netuid 36 --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY

# Then run miner
python3 miner.py --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY
```

**Option C: Both (Recommended for Production)**

```bash
# Terminal 1: Start API server
python3 api.py

# Terminal 2: Start Miner
python3 miner.py --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY
```

---

## Configuration

### Essential Environment Variables

```bash
# .env file configuration

# AI Provider (Chutes API)
CHUTES_API_KEY=your_chutes_api_key_here
CHUTES_API_URL=https://api.chutes.ai

# Worker Configuration
WORKER_NAME=autoppia-miner
WORKER_VERSION=0.1.0
WORKER_DESCRIPTION=Autoppia AI Worker

# Miner Configuration
API_URL=https://your-api-url.com  # Used by miner.py to connect to API
PORT=8000  # API server port

# Logging
LOG_LEVEL=INFO  # or DEBUG for verbose logging
```

### Bittensor Miner Setup

```bash
# Register wallet (one-time, requires TAO)
btcli wallet create --name my_wallet
btcli wallet register --netuid 36 --wallet.name my_wallet

# View miner status
btcli wallet overview --netuid 36 --wallet.name my_wallet

# View subnet stats
btcli subnet stats --netuid 36
```

---

## Verification & Monitoring

### Check API Health

```bash
# Health check
curl http://localhost:8000/health

# Get metadata
curl http://localhost:8000/metadata

# Get metrics
curl http://localhost:8000/metrics
```

### Expected API Response

```json
{
  "status": "healthy",
  "worker": "autoppia-miner",
  "version": "0.1.0",
  "timestamp": "2025-11-14T12:34:56Z",
  "chutes_api_configured": true,
  "cache": {
    "size": 5,
    "max_size": 100,
    "ttl_seconds": 3600
  },
  "requests": {
    "total": 1234,
    "success": 1200,
    "errors": 34,
    "success_rate_percent": "97.2%"
  }
}
```

### Monitor Systemd Services

```bash
# Check service status
sudo systemctl status autoppia-api
sudo systemctl status autoppia-miner

# View live logs
sudo journalctl -u autoppia-api -f
sudo journalctl -u autoppia-miner -f

# View past logs
sudo journalctl -u autoppia-api -n 100  # Last 100 lines
sudo journalctl -u autoppia-api --since "2 hours ago"
```

### Test Miner

```bash
# Check if miner is registered
btcli wallet overview --netuid 36

# View miner UID and performance
btcli subnet metagraph --netuid 36

# Check miner logs
journalctl -u autoppia-miner -f
```

### Example Monitoring Commands

```bash
# Monitor API response time
while true; do
    time curl -s http://localhost:8000/health > /dev/null
    sleep 5
done

# Monitor miner status
watch -n 10 "btcli wallet overview --netuid 36 | grep -E 'UID|Stake|Emission'"

# Check system resources
watch -n 5 "free -h && ps aux | grep autoppia"
```

---

## Troubleshooting

### API Server Won't Start

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Check logs for errors
journalctl -u autoppia-api -n 50

# Try running with debug output
python3 api.py 2>&1 | head -50

# Check .env file permissions
ls -la .env
```

### Worker Initialization Failed

```bash
# Ensure logs directory exists
mkdir -p logs

# Check directory permissions
ls -la logs/

# Ensure .env exists
ls -la .env

# Verify CHUTES_API_KEY is set
grep CHUTES_API_KEY .env
```

### Miner Not Registering

```bash
# Check wallet exists
btcli wallet list

# Check hotkey
btcli wallet overview

# Ensure you have TAO tokens
btcli wallet balance

# Register manually
btcli subnet register --netuid 36 --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY

# Check registration
btcli wallet overview --netuid 36
```

### Timeout Issues

```bash
# Increase timeout in api.py
# Or check Chutes API connectivity
curl -v https://api.chutes.ai/health

# Check network connectivity
ping 8.8.8.8
dig google.com
```

### High Memory Usage

```bash
# Check process memory
ps aux | grep python3

# Limit cache size in api.py (line 273)
# cache = RequestCache(max_size=50)  # Reduce from 100

# Restart service
sudo systemctl restart autoppia-api
```

### Miner Disconnects

```bash
# Check logs for network errors
journalctl -u autoppia-miner -f

# Verify Bittensor network connectivity
python3 -c "import bittensor as bt; print(bt.subtensor(network='finney').get_block())"

# Restart miner
sudo systemctl restart autoppia-miner
```

---

## Performance Optimization

### Enable Caching

Caching is enabled by default. Verify it's working:

```bash
# Check cache metrics
curl http://localhost:8000/metrics | jq '.cache'

# Should show increasing size as tasks are cached
```

### Monitor Response Times

```bash
# Check API response times in metrics
curl http://localhost:8000/metrics | jq '.requests'

# Goal: <300ms average, <1s maximum
```

### Resource Usage

```bash
# Monitor in real-time
top

# Or use htop for better interface
htop

# Expected usage:
# - Memory: 50-100MB (API), 100-200MB (Miner)
# - CPU: <10% (idle), 20-50% (during tasks)
```

---

## Maintenance

### Regular Updates

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Restart services
sudo systemctl restart autoppia-api autoppia-miner
```

### Log Rotation

```bash
# Configure logrotate for large logs
sudo nano /etc/logrotate.d/autoppia

# Add:
/opt/autoppia-miner/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 $USER $USER
}

# Apply rotation
sudo logrotate -f /etc/logrotate.d/autoppia
```

### Backup Configuration

```bash
# Backup .env file (IMPORTANT!)
cp /opt/autoppia-miner/.env /opt/autoppia-miner/.env.backup

# Backup all config
tar czf autoppia-backup-$(date +%Y%m%d).tar.gz /opt/autoppia-miner/
```

---

## Security Hardening

### 1. Firewall Configuration

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8000/tcp  # API
sudo ufw allow 8091/tcp  # Miner axon
sudo ufw enable
```

### 2. Protect .env File

```bash
# Restrict .env permissions
chmod 600 /opt/autoppia-miner/.env

# Verify
ls -la /opt/autoppia-miner/.env
# Should show: -rw------- 
```

### 3. Use API Keys

```bash
# Never commit .env to git
echo ".env" >> .gitignore

# Store API keys securely
# Use environment variables instead of files when possible
```

### 4. Monitor Access Logs

```bash
# Check API access patterns
tail -f /var/log/syslog | grep autoppia

# Detect unusual activity
journalctl -u autoppia-api | grep "503\|ERROR"
```

---

## Deployment Checklist

Before deploying to production:

- [ ] All tests passing (52/52)
- [ ] .env file configured with real API keys
- [ ] Bittensor wallet registered on subnet 36
- [ ] Firewall rules configured
- [ ] Systemd services enabled for auto-start
- [ ] Monitoring/logging configured
- [ ] Backups created
- [ ] Documentation updated
- [ ] Error handling tested
- [ ] Performance validated

---

## Support & Resources

- **GitHub:** https://github.com/irun2themoney/autoppia-miner
- **Docs:** https://luxit.gitbook.io/autoppia-docs
- **Bittensor:** https://docs.bittensor.com
- **Subnet 36:** https://taostats.io/subnets/36/
- **Leaderboard:** https://infinitewebarena.autoppia.com/

---

## Quick Commands Reference

```bash
# Deploy
./deploy_to_do.sh BOTH wallet_name hotkey_name

# Start/Stop services
sudo systemctl start|stop|restart autoppia-api autoppia-miner

# View logs
sudo journalctl -u autoppia-api -f
sudo journalctl -u autoppia-miner -f

# Check status
sudo systemctl status autoppia-api autoppia-miner

# Health check
curl http://localhost:8000/health

# Metrics
curl http://localhost:8000/metrics

# Update
git pull origin main && pip install -r requirements.txt

# Backup
tar czf backup-$(date +%Y%m%d).tar.gz /opt/autoppia-miner/
```

---

**🎉 Happy mining! For support, check the GitHub issues or community channels.**

