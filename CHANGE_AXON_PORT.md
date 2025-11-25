# 🔄 Changing Axon Port - Developer Recommendation

## Why Change the Port?

The developer suggested trying a different port because:
1. **Port conflicts**: Port 8091 might be filtered or blocked
2. **Network refresh**: Changing port might trigger network re-discovery
3. **Validator filtering**: Some validators might filter by port
4. **Fresh start**: New port = fresh network registration

---

## Current Configuration

- **Current Port**: `8091`
- **IP**: `134.199.203.133`
- **Current Endpoint**: `134.199.203.133:8091`

---

## How to Change Axon Port

### Option 1: Change via Command Line (Temporary)

```bash
# Stop current miner
systemctl stop autoppia-miner

# Start with new port (e.g., 8092)
python3 -m miner.miner \
  --wallet.name default \
  --wallet.hotkey default \
  --netuid 36 \
  --subtensor.network finney \
  --axon.port 8092
```

### Option 2: Change via Settings (Permanent)

**File**: `config/settings.py`

```python
axon_port: int = 8092  # Changed from 8091
```

### Option 3: Change via Environment Variable

**File**: `.env` (on server)

```bash
AXON_PORT=8092
```

### Option 4: Change via Systemd Service (Production)

**File**: `scripts/deploy/autoppia-miner.service`

```ini
ExecStart=/opt/autoppia-miner/venv/bin/python3 -m miner.miner \
  --wallet.name default \
  --wallet.hotkey default \
  --netuid 36 \
  --subtensor.network finney \
  --axon.port 8092
```

---

## Recommended Ports to Try

Based on common Bittensor ports:

1. **8092** - Next sequential port
2. **8093** - Another sequential option
3. **8090** - One port below current
4. **8081** - Close to API port
5. **9000** - Common alternative port range

**Avoid**: Ports < 1024 (require root), ports already in use

---

## Steps to Change Port

### 1. Choose New Port
```bash
# Check if port is available
netstat -tlnp | grep 8092
# or
ss -tlnp | grep 8092
```

### 2. Update Configuration
```bash
# On server
cd /opt/autoppia-miner

# Edit settings.py or .env
nano config/settings.py  # Change axon_port
# OR
nano .env  # Add AXON_PORT=8092
```

### 3. Update Systemd Service
```bash
# Edit service file
sudo nano /etc/systemd/system/autoppia-miner.service

# Change --axon.port 8091 to --axon.port 8092
```

### 4. Update Firewall
```bash
# Allow new port
sudo ufw allow 8092/tcp

# Optional: Remove old port (after confirming new port works)
# sudo ufw delete allow 8091/tcp
```

### 5. Restart Services
```bash
# Reload systemd
sudo systemctl daemon-reload

# Restart miner
sudo systemctl restart autoppia-miner

# Check status
sudo systemctl status autoppia-miner
```

### 6. Verify New Port
```bash
# Check if port is listening
netstat -tlnp | grep 8092
# or
ss -tlnp | grep 8092

# Check logs
journalctl -u autoppia-miner -f | grep -i axon
```

---

## What to Expect

### After Changing Port:

1. **Miner restarts** with new port
2. **Axon re-serves** to network with new port
3. **Metagraph updates** (may take a few minutes)
4. **Network re-discovers** your miner
5. **Validators may query** the new port

### Monitoring:

```bash
# Watch for axon serving
journalctl -u autoppia-miner -f | grep -E 'axon|port|served'

# Check on-chain status
python3 scripts/check_onchain_status.py
```

---

## Rollback Plan

If new port doesn't help:

```bash
# Change back to 8091
sudo nano /etc/systemd/system/autoppia-miner.service
# Change --axon.port back to 8091

sudo systemctl daemon-reload
sudo systemctl restart autoppia-miner
```

---

## Testing New Port

After changing port, test with:

```bash
# From your local machine
curl -X POST http://134.199.203.133:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id": "test", "url": "https://example.com", "prompt": "test"}'
```

The API endpoint (port 8080) doesn't change - only the axon port (for Bittensor queries).

---

## Important Notes

1. **API Port (8080) stays the same** - Only axon port changes
2. **Firewall must allow new port** - Update UFW rules
3. **Network may take time** - Metagraph updates can take 5-15 minutes
4. **Keep old port open temporarily** - Until new port is confirmed working
5. **Monitor logs** - Watch for any errors after port change

---

**Status**: Ready to change port  
**Recommendation**: Try port 8092 first (next sequential port)

