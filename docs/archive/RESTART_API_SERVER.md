# Restart API Server Instructions

The API server needs to be restarted to pick up the new `/metrics` endpoint and ensure all routes are properly registered.

## Option 1: If running locally (development)

```bash
# Stop the current server (Ctrl+C if running in terminal)
# Then restart:
cd /Users/illfaded2022/Desktop/WORKSPACE/autoppia-miner
python3 -m api.server
```

## Option 2: If running on DigitalOcean (production)

SSH into your server and restart the systemd service:

```bash
# SSH into your server
ssh root@134.199.203.133

# Restart the API service
sudo systemctl restart autoppia-api

# Check status
sudo systemctl status autoppia-api

# View logs if needed
sudo journalctl -u autoppia-api -f
```

## Option 3: Quick restart script

Create and run this script:

```bash
#!/bin/bash
# restart_api.sh

# If local
if [ -f "api/server.py" ]; then
    echo "Restarting local API server..."
    pkill -f "api.server" || true
    sleep 2
    python3 -m api.server &
    echo "API server restarted"
fi

# If on server (check for systemd)
if systemctl is-active --quiet autoppia-api 2>/dev/null; then
    echo "Restarting systemd service..."
    sudo systemctl restart autoppia-api
    echo "API service restarted"
fi
```

## Verify endpoints are working

After restarting, test the endpoints:

```bash
# Test /metrics endpoint
curl http://localhost:8080/metrics

# Test /api/dashboard/metrics endpoint
curl http://localhost:8080/api/dashboard/metrics

# Test /health endpoint
curl http://localhost:8080/health
```

All should return JSON responses (not 404).

