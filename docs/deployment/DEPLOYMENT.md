# 🚀 Deployment Guide

**Official deployment guide for Autoppia Miner**

---

## 📋 **Pre-Deployment Checklist**

- [ ] Wallet configured with TAO
- [ ] Server (DigitalOcean droplet) ready
- [ ] Port 8080 open
- [ ] Python 3.8+ installed
- [ ] Git repository cloned

---

## 🖥️ **Server Setup**

### **1. Initial Server Setup**

```bash
# SSH to server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install -y python3 python3-pip python3-venv git

# Install systemd (if not already installed)
apt install -y systemd
```

### **2. Clone Repository**

```bash
cd /opt
git clone <your-repo-url> autoppia-miner
cd autoppia-miner
```

### **3. Create Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ **Configuration**

### **1. Environment Setup**

```bash
cp env.example .env
nano .env
```

### **2. Required Configuration**

```bash
# Wallet (REQUIRED)
WALLET_NAME=your_wallet_name
WALLET_HOTKEY=your_hotkey_name

# Network (REQUIRED)
SUBTENSOR_NETWORK=finney
NETUID=36

# API (REQUIRED)
API_HOST=0.0.0.0
API_PORT=8080

# Logging
LOG_LEVEL=INFO
```

### **3. Verify Configuration**

```bash
python3 -c "from config.settings import settings; print(f'Wallet: {settings.wallet_name}')"
```

---

## 🔧 **Systemd Services**

### **1. Create API Service**

```bash
sudo nano /etc/systemd/system/autoppia-api.service
```

**Content:**
```ini
[Unit]
Description=Autoppia API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/autoppia-miner
Environment="PATH=/opt/autoppia-miner/venv/bin"
ExecStart=/opt/autoppia-miner/venv/bin/python -m api.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **2. Create Miner Service**

```bash
sudo nano /etc/systemd/system/autoppia-miner.service
```

**Content:**
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
ExecStart=/opt/autoppia-miner/venv/bin/python -m miner.miner
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **3. Enable and Start Services**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable autoppia-api
sudo systemctl enable autoppia-miner

# Start services
sudo systemctl start autoppia-api
sudo systemctl start autoppia-miner
```

---

## 🔍 **Verification**

### **1. Check Service Status**

```bash
# Check API
sudo systemctl status autoppia-api

# Check Miner
sudo systemctl status autoppia-miner
```

### **2. Check Logs**

```bash
# API logs
sudo journalctl -u autoppia-api -f

# Miner logs
sudo journalctl -u autoppia-miner -f
```

### **3. Test API**

```bash
# Health check
curl http://localhost:8080/health

# Dashboard
curl http://localhost:8080/api/dashboard
```

### **4. Test from External**

```bash
# From your local machine
curl http://your-server-ip:8080/health
```

---

## 🔥 **Firewall Configuration**

### **UFW (Ubuntu)**

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow API port
sudo ufw allow 8080/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### **DigitalOcean Firewall**

1. Go to DigitalOcean Dashboard
2. Networking → Firewalls
3. Create/Edit firewall
4. Add rule: Allow TCP 8080

---

## 📊 **Monitoring**

### **1. Real-Time Dashboard**

Access at: `http://your-server-ip:8080/dashboard`

### **2. Metrics API**

```bash
curl http://your-server-ip:8080/api/dashboard | jq
```

### **3. Service Monitoring**

```bash
# Watch API service
watch -n 5 'systemctl status autoppia-api'

# Watch miner service
watch -n 5 'systemctl status autoppia-miner'
```

---

## 🔄 **Updates & Maintenance**

### **Update Code**

```bash
cd /opt/autoppia-miner
git pull
source venv/bin/activate
pip install -r requirements.txt

# Restart services
sudo systemctl restart autoppia-api
sudo systemctl restart autoppia-miner
```

### **View Recent Logs**

```bash
# Last 100 lines
sudo journalctl -u autoppia-api -n 100
sudo journalctl -u autoppia-miner -n 100

# Since boot
sudo journalctl -u autoppia-api -b
sudo journalctl -u autoppia-miner -b
```

---

## 🐛 **Troubleshooting**

### **Service Won't Start**

```bash
# Check logs
sudo journalctl -u autoppia-api -n 50
sudo journalctl -u autoppia-miner -n 50

# Check configuration
python3 -c "from config.settings import settings; print(settings)"

# Test manually
cd /opt/autoppia-miner
source venv/bin/activate
python -m api.server  # Test API
python -m miner.miner  # Test miner
```

### **Port Already in Use**

```bash
# Find process using port 8080
sudo lsof -i :8080

# Kill process
sudo kill -9 <PID>
```

### **Permission Issues**

```bash
# Check file permissions
ls -la /opt/autoppia-miner

# Fix if needed
chmod +x /opt/autoppia-miner/scripts/*.sh
```

---

## ✅ **Post-Deployment Verification**

### **1. Run Ultimate Test**

```bash
cd /opt/autoppia-miner
./scripts/run_ultimate_test.sh
```

### **2. Check IWA Playground**

1. Visit: https://infinitewebarena.autoppia.com/home
2. Use your server IP:port (e.g., `134.199.203.133:8080`)
3. Run benchmark tests

### **3. Monitor Validator Activity**

```bash
# Watch for validator requests
sudo journalctl -u autoppia-api -f | grep "validator"
```

---

## 🎯 **Success Indicators**

✅ API responds to health checks  
✅ Miner connects to subtensor  
✅ Services stay running  
✅ Dashboard shows metrics  
✅ Validator requests appear in logs  

---

## 📞 **Support**

If issues persist:
1. Check logs: `journalctl -u autoppia-api -f`
2. Run tests: `./scripts/run_ultimate_test.sh`
3. Verify configuration: Check `.env` file

---

**Ready to mine! Let's get this TAO! 🚀**

