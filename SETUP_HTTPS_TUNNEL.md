# 🔒 Setup HTTPS Tunnel for IWA Playground

## Problem
The IWA Playground is HTTPS, but our API is HTTP. Modern browsers block mixed content (HTTPS → HTTP), causing "Failed to fetch" errors.

## Solution: Use Cloudflare Tunnel (Free & Easy)

### Option 1: Cloudflare Tunnel (Recommended)

```bash
# On your DigitalOcean droplet:

# 1. Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# 2. Create tunnel (run once)
cloudflared tunnel create autoppia-api

# 3. Create config file
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << EOF
tunnel: <TUNNEL_ID>
credentials-file: /root/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: autoppia-api.yourdomain.com  # Replace with your domain
    service: http://localhost:8080
  - service: http_status:404
EOF

# 4. Run tunnel
cloudflared tunnel run autoppia-api

# 5. Create systemd service (optional, for auto-start)
cat > /etc/systemd/system/cloudflared.service << 'EOF'
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/cloudflared tunnel run autoppia-api
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cloudflared
systemctl start cloudflared
```

### Option 2: ngrok (Quick Test)

```bash
# On your DigitalOcean droplet:

# 1. Install ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list
apt update && apt install ngrok

# 2. Get auth token from https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_AUTH_TOKEN

# 3. Start tunnel
ngrok http 8080

# 4. Use the HTTPS URL shown (e.g., https://abc123.ngrok.io)
```

### Option 3: Let's Encrypt + nginx (Permanent Solution)

```bash
# On your DigitalOcean droplet:

# 1. Install nginx and certbot
apt update
apt install -y nginx certbot python3-certbot-nginx

# 2. Configure nginx
cat > /etc/nginx/sites-available/autoppia-api << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -s /etc/nginx/sites-available/autoppia-api /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# 3. Get SSL certificate
certbot --nginx -d YOUR_DOMAIN_OR_IP

# 4. Auto-renewal
systemctl enable certbot.timer
```

## Quick Test

After setting up HTTPS tunnel, test:

```bash
# Test HTTPS endpoint
curl https://YOUR_HTTPS_URL/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id": "test", "prompt": "test", "url": "https://example.com"}'
```

## Use in Playground

Enter your HTTPS URL in the IWA Playground:
- Cloudflare Tunnel: `https://autoppia-api.yourdomain.com`
- ngrok: `https://abc123.ngrok.io`
- Let's Encrypt: `https://YOUR_DOMAIN_OR_IP`

