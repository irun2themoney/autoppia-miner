# 🚀 YOLO MODE - QUICK DEPLOY

## Step 1: Make Repo Public (30 seconds)
1. Go to: https://github.com/irun2themoney/autoppia-miner/settings
2. Scroll to "Danger Zone" → "Change visibility" → "Make public"
3. Confirm

## Step 2: On Your Server (Copy/Paste All At Once)

```bash
git clone https://github.com/irun2themoney/autoppia-miner.git && cd autoppia-miner && pip3 install -r requirements.txt && cp env.example .env && nano .env
```

Add your CHUTES_API_KEY, then:

```bash
ufw allow 22/tcp && ufw allow 8080/tcp && ufw --force enable && cat > /etc/systemd/system/autoppia-api.service << 'SERVICEEOF'
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
SERVICEEOF
systemctl daemon-reload && systemctl enable autoppia-api && systemctl start autoppia-api && sleep 3 && systemctl status autoppia-api
```

## Step 3: Test
```bash
curl http://localhost:8080/health
```

## Step 4: Configure DigitalOcean Firewall
Dashboard → Networking → Firewalls → Allow port 8080

## Done! Use: 134.199.201.62:8080
