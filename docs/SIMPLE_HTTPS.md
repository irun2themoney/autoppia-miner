# 🚀 Simple HTTPS Tunnel - One Command

## Quickest Solution (No Setup Needed)

On your DigitalOcean droplet, run:

```bash
# Install cloudflared (one-time)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Start tunnel (gives you HTTPS URL immediately)
cloudflared tunnel --url http://localhost:8080
```

This will output something like:
```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
|  https://abc123-def456-ghi789.trycloudflare.com                                           |
+--------------------------------------------------------------------------------------------+
```

**Use that HTTPS URL in the IWA Playground!**

## Keep It Running

To keep the tunnel running in the background:

```bash
# Run in background
nohup cloudflared tunnel --url http://localhost:8080 > /tmp/cloudflared.log 2>&1 &

# Check the URL
grep "trycloudflare.com" /tmp/cloudflared.log
```

## Make It Permanent (systemd service)

```bash
cat > /etc/systemd/system/cloudflared-tunnel.service << 'EOF'
[Unit]
Description=Cloudflare Tunnel for IWA API
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/cloudflared tunnel --url http://localhost:8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cloudflared-tunnel
systemctl start cloudflared-tunnel

# Check status
systemctl status cloudflared-tunnel

# Get the URL from logs
journalctl -u cloudflared-tunnel | grep trycloudflare.com
```

## Test It

```bash
# Test the HTTPS endpoint
curl https://YOUR_TUNNEL_URL.trycloudflare.com/health
```

Then use `https://YOUR_TUNNEL_URL.trycloudflare.com` in the IWA Playground!

