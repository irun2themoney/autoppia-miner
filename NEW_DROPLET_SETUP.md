# 🚀 New Droplet Setup - Quick Start

## Your New Droplet Info

- **Name**: autoppia-miner
- **IP Address**: `134.199.203.133` (NEW - updated from old IP)
- **Location**: Atlanta 1 (ATL1)
- **OS**: Ubuntu 22.04 (LTS) x64
- **Specs**: 1 GB RAM, 1 vCPU, 35 GB Disk

---

## ⚡ Quick Deploy (Copy & Paste)

### Step 1: SSH Into New Droplet

```bash
ssh root@134.199.203.133
```

### Step 2: Run Complete Deployment

**Copy and paste this entire block:**

```bash
# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip git curl ufw

# Clone repository
cd /opt
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file with NEW IP
cat > .env << 'EOF'
# AI Provider (Chutes API)
CHUTES_API_KEY=cpk_384e5ee3477b4345be53ecb6cf5336d6.97cdedde58e45965820657bd8ec790fa.Op9UfWviGGaAKmInl8xqTeKHTUjx8z2n
CHUTES_API_URL=https://api.chutes.ai

# Worker Configuration
WORKER_NAME=autoppia-miner
WORKER_VERSION=0.1.0
WORKER_DESCRIPTION=Autoppia AI Worker

# Miner Configuration
API_URL=http://134.199.203.133:8080
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
echo "🌐 API accessible at: http://134.199.203.133:8080"
```

---

## 🔥 Configure DigitalOcean Firewall

1. **Go to**: https://cloud.digitalocean.com/networking/firewalls
2. **Create/Edit firewall** for your droplet
3. **Inbound Rules:**
   - SSH (22) - All IPv4
   - Custom TCP (8080) - All IPv4 ← **Critical!**
   - Custom TCP (8091) - All IPv4 (for miner)
4. **Outbound Rules:**
   - All TCP, UDP, ICMP - All IPv4/IPv6
5. **Apply** to your droplet

---

## ✅ Verify Deployment

### Test API Health:

```bash
# From your local machine
curl http://134.199.203.133:8080/health
```

**Should return:**
```json
{"status":"healthy","worker":"autoppia-miner",...}
```

### Check Service Status:

```bash
# SSH into droplet
ssh root@134.199.203.133

# Check service
systemctl status autoppia-api

# View logs
journalctl -u autoppia-api -f
```

---

## 🌐 Use in InfiniteWeb Arena

**Endpoint to use:**
```
134.199.203.133:8080
```

**Or with protocol:**
```
http://134.199.203.133:8080
```

---

## 🔐 Set Up Miner (If Needed)

If you need to run the Bittensor miner:

### Option 1: Copy Wallet from Local

```bash
# On your LOCAL machine:
scp -r ~/.bittensor/wallets/YOUR_WALLET_NAME root@134.199.203.133:~/.bittensor/wallets/
```

### Option 2: Create New Wallet

```bash
# On VPS:
pip install bittensor
btcli wallet create --name YOUR_WALLET_NAME
```

### Deploy Miner:

```bash
cd /opt/autoppia-miner
chmod +x deploy_miner_digitalocean.sh
sudo ./deploy_miner_digitalocean.sh YOUR_WALLET_NAME YOUR_HOTKEY_NAME
```

---

## 📋 Quick Checklist

- [ ] SSH into new droplet: `ssh root@134.199.203.133`
- [ ] Run deployment script above
- [ ] Configure DigitalOcean Firewall (port 8080)
- [ ] Test API: `curl http://134.199.203.133:8080/health`
- [ ] Update InfiniteWeb Arena endpoint: `134.199.203.133:8080`
- [ ] Copy wallet (if running miner)
- [ ] Deploy miner (if needed)

---

## 🚨 Troubleshooting

### API Not Starting:

```bash
# Check logs
journalctl -u autoppia-api -n 50

# Common fixes:
# - Missing CHUTES_API_KEY → Check .env file
# - Port in use → Check: netstat -tuln | grep 8080
# - Python errors → Check logs above
```

### Can't Access API:

```bash
# Test locally on VPS
curl http://localhost:8080/health

# Test externally
curl http://134.199.203.133:8080/health

# If local works but external doesn't → Check DigitalOcean Firewall
```

---

## 📝 Important Notes

- **New IP**: `134.199.203.133` (updated from old IP)
- **API Port**: `8080`
- **Miner Port**: `8091` (if running miner)
- **All configuration files updated** with new IP

---

**Ready to deploy?** Just SSH in and run the deployment script above! 🚀

