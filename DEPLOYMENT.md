# Deployment Guide

Complete guide for deploying the Autoppia miner.

## Quick Deployment

### DigitalOcean Droplet

```bash
# On your droplet
cd /opt/autoppia-miner
git pull origin main
pip install -r requirements.txt
systemctl restart autoppia-api
systemctl restart autoppia-miner
```

### HTTPS Setup (for Playground)

```bash
# Quick one-command setup
cloudflared tunnel --url http://localhost:8080

# Or see SIMPLE_HTTPS.md for detailed setup
```

## Initial Setup

### 1. Server Setup

```bash
# Update system
apt update && apt upgrade -y

# Install Python
apt install python3 python3-pip python3-venv -y

# Clone repository
git clone https://github.com/irun2themoney/autoppia-miner.git /opt/autoppia-miner
cd /opt/autoppia-miner
```

### 2. Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp env.example .env
nano .env  # Edit with your settings
```

### 3. Wallet Setup

```bash
# Copy wallet from local machine
scp -r ~/.bittensor/wallets/default root@YOUR_DROPLET_IP:/root/.bittensor/wallets/

# Verify wallet
python3 -m bittensor wallet list
python3 -m bittensor wallet overview --netuid 36
```

### 4. Systemd Services

**API Service** (`/etc/systemd/system/autoppia-api.service`):
```ini
[Unit]
Description=Autoppia HTTP API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/autoppia-miner
Environment="PATH=/opt/autoppia-miner/venv/bin"
ExecStart=/opt/autoppia-miner/venv/bin/python3 -m api.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Miner Service** (`/etc/systemd/system/autoppia-miner.service`):
```ini
[Unit]
Description=Autoppia Bittensor Miner
After=network.target autoppia-api.service
Requires=autoppia-api.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/autoppia-miner
Environment="PATH=/opt/autoppia-miner/venv/bin"
ExecStart=/opt/autoppia-miner/venv/bin/python3 /opt/autoppia-miner/miner.py --wallet.name default --wallet.hotkey default --network finney --axon.port 8091
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**
```bash
systemctl daemon-reload
systemctl enable autoppia-api
systemctl enable autoppia-miner
systemctl start autoppia-api
systemctl start autoppia-miner
```

### 5. Firewall Configuration

```bash
# Allow API port
ufw allow 8080/tcp
ufw allow 8091/tcp
ufw reload
```

## HTTPS Tunnel Setup

For IWA playground access, you need HTTPS. See `SIMPLE_HTTPS.md` for details.

**Quick Setup:**
```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Start tunnel
cloudflared tunnel --url http://localhost:8080
```

## Verification

### Check Services

```bash
# API status
systemctl status autoppia-api

# Miner status
systemctl status autoppia-miner

# Check logs
journalctl -u autoppia-api -f
journalctl -u autoppia-miner -f
```

### Test API

```bash
# Health check
curl http://localhost:8080/health

# Test endpoint
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id":"test","prompt":"test","url":"https://example.com"}'
```

### Check Validator Activity

```bash
bash CHECK_VALIDATOR_ACTIVITY.sh
```

## Troubleshooting

### API Not Starting

1. Check logs: `journalctl -u autoppia-api -n 50`
2. Verify port: `ss -tlnp | grep 8080`
3. Check Python: `which python3`
4. Verify dependencies: `pip list`

### Miner Not Starting

1. Check logs: `journalctl -u autoppia-miner -n 50`
2. Verify wallet: `python3 -m bittensor wallet list`
3. Check registration: `python3 -m bittensor wallet overview --netuid 36`
4. Verify API connection: `curl http://localhost:8080/health`

### Connection Issues

1. Check firewall: `ufw status`
2. Verify API_URL in .env
3. Test connectivity: `curl http://localhost:8080/health`
4. Check network: `ping 8.8.8.8`

## Updating

```bash
cd /opt/autoppia-miner
git pull origin main
pip install -r requirements.txt
systemctl restart autoppia-api
systemctl restart autoppia-miner
```

## Monitoring

See `MONITORING.md` for detailed monitoring instructions.

