# 🚀 Quick Redeploy After Droplet Rebuild

## Your Droplet Was Rebuilt - Let's Get Everything Running Again

---

## ⚡ Fast Track Deployment (5 Minutes)

### Step 1: SSH Into Your Droplet

```bash
ssh root@134.199.201.62
```

**Note:** If the IP changed, use the new IP from DigitalOcean dashboard.

---

### Step 2: Run Complete Deployment Script

**Copy and paste this entire block:**

```bash
# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip git curl ufw

# Clone repository
cd /opt
rm -rf autoppia-miner 2>/dev/null || true
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
# AI Provider (Chutes API)
CHUTES_API_KEY=cpk_384e5ee3477b4345be53ecb6cf5336d6.97cdedde58e45965820657bd8ec790fa.Op9UfWviGGaAKmInl8xqTeKHTUjx8z2n
CHUTES_API_URL=https://api.chutes.ai

# Worker Configuration
WORKER_NAME=autoppia-miner
WORKER_VERSION=0.1.0
WORKER_DESCRIPTION=Autoppia AI Worker

# Miner Configuration
API_URL=http://134.199.201.62:8080
PORT=8080

# Logging
LOG_LEVEL=INFO
CORS_ORIGINS=*
EOF

# Create logs directory
mkdir -p logs

# Configure firewall
ufw allow 22/tcp
ufw allow 8080/tcp
ufw allow 8091/tcp
ufw --force enable

# Create systemd service for API
cat > /etc/systemd/system/autoppia-api.service << 'SERVICEEOF'
[Unit]
Description=Autoppia HTTP API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/autoppia-miner
Environment="PATH=/opt/autoppia-miner/venv/bin:/usr/bin:/usr/local/bin"
Environment="PORT=8080"
ExecStart=/opt/autoppia-miner/venv/bin/python3 /opt/autoppia-miner/api.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Enable and start API service
systemctl daemon-reload
systemctl enable autoppia-api
systemctl start autoppia-api

# Wait for service to start
sleep 5

# Check status
echo "=== API Service Status ==="
systemctl status autoppia-api --no-pager | head -10

# Test API
echo -e "\n=== Testing API ==="
curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8080/health

echo -e "\n✅ Deployment complete!"
echo "🌐 API should be accessible at: http://134.199.201.62:8080"
```

---

## 🔍 Verify Everything Works

### Test API Health:

```bash
curl http://134.199.201.62:8080/health
```

### Check Service Status:

```bash
systemctl status autoppia-api
```

### View Logs:

```bash
journalctl -u autoppia-api -f
```

---

## 🔐 If You Need to Set Up Wallet/Miner

### Option 1: Copy Wallet from Local Machine

```bash
# On your LOCAL machine:
scp -r ~/.bittensor/wallets/YOUR_WALLET_NAME root@134.199.201.62:~/.bittensor/wallets/
```

### Option 2: Create New Wallet on VPS

```bash
# On VPS:
pip install bittensor
btcli wallet create --name YOUR_WALLET_NAME
```

### Deploy Miner (if needed):

```bash
cd /opt/autoppia-miner
chmod +x deploy_miner_digitalocean.sh
sudo ./deploy_miner_digitalocean.sh YOUR_WALLET_NAME YOUR_HOTKEY_NAME
```

---

## ⚙️ Configure DigitalOcean Firewall

1. Go to: https://cloud.digitalocean.com/networking/firewalls
2. Create/Edit firewall for your droplet
3. **Inbound Rules:**
   - SSH (22) - All IPv4
   - Custom TCP (8080) - All IPv4 ← **Critical for API**
   - Custom TCP (8091) - All IPv4 ← **For miner (if running)**
4. **Outbound Rules:**
   - All TCP, UDP, ICMP - All IPv4/IPv6
5. Apply to your droplet

---

## ✅ Quick Checklist

- [ ] Droplet is running
- [ ] SSH access works
- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] .env file created with Chutes API key
- [ ] API service running
- [ ] Port 8080 open in UFW
- [ ] Port 8080 open in DigitalOcean Firewall
- [ ] API responds to health check
- [ ] InfiniteWeb Arena can reach endpoint

---

## 🚨 Troubleshooting

### API Not Starting:

```bash
# Check logs
journalctl -u autoppia-api -n 50

# Common issues:
# - Missing CHUTES_API_KEY → Check .env file
# - Port already in use → Check: netstat -tuln | grep 8080
# - Python errors → Check logs above
```

### Can't Access API:

```bash
# Test locally
curl http://localhost:8080/health

# Test externally
curl http://134.199.201.62:8080/health

# If local works but external doesn't → Firewall issue
# Check DigitalOcean Firewall settings
```

---

## 📋 Your Configuration

- **Droplet IP**: `134.199.201.62` (or new IP if changed)
- **API Port**: `8080`
- **API Endpoint**: `http://134.199.201.62:8080`
- **Chutes API Key**: Already in .env file above

---

**Once deployed, test in InfiniteWeb Arena with:**
```
134.199.201.62:8080
```

