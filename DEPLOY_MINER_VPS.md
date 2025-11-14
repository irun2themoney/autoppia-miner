# 🚀 Deploy Miner to VPS (24/7 Operation)

## Why Deploy to VPS?

- ✅ Runs 24/7 without your computer
- ✅ More reliable uptime
- ✅ Professional setup
- ✅ Lower electricity costs
- ✅ Better for long-term mining

## Quick Setup Guide

### 1. Choose a VPS Provider

**Recommended (Cheapest):**
- **Hetzner**: €4-8/month (best value)
- **DigitalOcean**: $6-12/month
- **Linode**: $5-10/month
- **AWS EC2**: Pay as you go

### 2. Set Up VPS

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install python3 python3-pip git -y

# Clone your repository
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner

# Install dependencies
pip3 install -r requirements.txt

# Install bittensor
pip3 install bittensor
```

### 3. Configure Environment

```bash
# Copy environment file
cp env.example .env

# Edit .env with your settings
nano .env
# Set: CHUTES_API_KEY, API_URL
```

### 4. Set Up Wallet on VPS

```bash
# Install btcli
pip3 install bittensor

# Copy wallet from local machine OR create new one
# Option A: Copy wallet files
scp -r ~/.bittensor/wallets/default root@your-vps-ip:~/.bittensor/wallets/

# Option B: Create new wallet (if you want separate)
btcli wallet create --name default
```

### 5. Run Miner with Screen/Tmux

```bash
# Install screen
apt install screen -y

# Start screen session
screen -S miner

# Run miner
python3 miner.py \
  --wallet.name default \
  --wallet.hotkey default \
  --network finney \
  --axon.port 8091

# Detach: Press Ctrl+A then D
# Reattach: screen -r miner
```

### 6. Set Up Auto-Start (Systemd)

```bash
# Create service file
nano /etc/systemd/system/autoppia-miner.service
```

Add this content:
```ini
[Unit]
Description=Autoppia Bittensor Miner
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/autoppia-miner
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /root/autoppia-miner/miner.py --wallet.name default --wallet.hotkey default --network finney --axon.port 8091
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl daemon-reload
systemctl enable autoppia-miner
systemctl start autoppia-miner
systemctl status autoppia-miner
```

### 7. Monitor

```bash
# View logs
journalctl -u autoppia-miner -f

# Check status
systemctl status autoppia-miner

# Restart if needed
systemctl restart autoppia-miner
```

## Port Forwarding

Make sure port 8091 (or your axon port) is open:
- Open in VPS firewall
- Configure in VPS provider's dashboard

## Security

- Use SSH keys (not passwords)
- Keep system updated
- Use firewall (ufw)
- Don't expose unnecessary ports

## Cost Estimate

- VPS: $5-12/month
- Electricity saved: ~$10-20/month (vs running local computer)
- **Net savings: ~$5-15/month + 24/7 reliability**

## Alternative: Keep Local

If you want to keep running locally:
- Keep computer on 24/7
- Use screen/tmux to keep miner running
- Disable sleep mode
- Monitor occasionally
