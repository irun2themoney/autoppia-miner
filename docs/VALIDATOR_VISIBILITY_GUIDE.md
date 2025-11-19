# Validator Visibility Guide

## How Validators Discover Miners

Validators on Bittensor subnet 36 (Infinite Web Arena) discover miners through the **metagraph**, which is a distributed registry of all active miners on the network. For validators to see and query your miner:

1. **Registration**: Your miner must be registered on subnet 36 with a unique UID
2. **Axon Serving**: Your miner's axon (network endpoint) must be served to the subtensor network
3. **Network Accessibility**: Your axon port must be accessible from the internet
4. **Active Status**: Your miner must be running and responding to health checks

## Registration Requirements

### Prerequisites

- **Bittensor Wallet**: Created with coldkey and hotkey
- **TAO Balance**: At least **0.1 TAO** for registration fee
- **Network Access**: Ports 8080 (API) and 8091 (axon) open to internet

### Registration Process

1. **Create Wallet** (if you don't have one):
   ```bash
   btcli wallet create --wallet.name your_wallet
   btcli wallet new_hotkey --wallet.name your_wallet --wallet.hotkey your_hotkey
   ```

2. **Fund Wallet**:
   - Transfer at least 0.1 TAO to your wallet
   - Check balance: `btcli wallet balance --wallet.name your_wallet`

3. **Register on Subnet 36**:
   ```bash
   btcli subnet register --netuid 36 --wallet.name your_wallet --wallet.hotkey your_hotkey
   ```

4. **Verify Registration**:
   ```bash
   cd /opt/autoppia-miner
   ./scripts/utils/check_registration.sh your_wallet your_hotkey
   ```

## Common Visibility Issues

### Issue 1: Miner Not Registered

**Symptoms**:
- No UID assigned
- Validators never query your miner
- `check_registration.sh` shows "NOT registered"

**Solution**:
```bash
# Check if registered
./scripts/utils/check_registration.sh

# If not registered, register now
btcli subnet register --netuid 36 --wallet.name $WALLET_NAME --wallet.hotkey $WALLET_HOTKEY
```

### Issue 2: Wallet Configuration Missing

**Symptoms**:
- Miner starts but doesn't register
- Logs show "Miner not registered" error
- No wallet name/hotkey in environment

**Solution**:
```bash
# Edit .env file
nano /opt/autoppia-miner/.env

# Add these lines:
WALLET_NAME=your_wallet_name
WALLET_HOTKEY=your_hotkey_name

# Restart miner
sudo systemctl restart autoppia-miner
```

### Issue 3: Axon Not Served to Network

**Symptoms**:
- Miner registered but validators don't query
- Logs don't show "Axon served to network"
- UID exists but no incoming requests

**Solution**:
```bash
# Check miner logs for "served to network" message
journalctl -u autoppia-miner | grep -i "served\|axon"

# If not found, restart miner
sudo systemctl restart autoppia-miner

# Verify visibility
./scripts/utils/verify_visibility.sh
```

### Issue 4: Firewall Blocking Ports

**Symptoms**:
- Axon served but no validator requests
- Ports not accessible from internet
- External connectivity tests fail

**Solution**:
```bash
# Open required ports (Ubuntu/Debian with UFW)
sudo ufw allow 8080/tcp  # API port
sudo ufw allow 8091/tcp  # Axon port
sudo ufw reload

# For CentOS/RHEL with firewalld
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=8091/tcp
sudo firewall-cmd --reload

# Test from external machine
curl http://YOUR_SERVER_IP:8080/health
```

### Issue 5: Incorrect External IP

**Symptoms**:
- Miner shows 0.0.0.0 or local IP in metagraph
- Validators can't reach your miner
- Axon IP doesn't match server IP

**Solution**:
```bash
# Check current external IP
curl ifconfig.me

# Verify metagraph shows correct IP
btcli subnet metagraph --netuid 36 | grep YOUR_UID

# If incorrect, restart miner (it auto-detects IP)
sudo systemctl restart autoppia-miner
```

## Monitoring Validator Activity

### Check Recent Validator Requests

```bash
# Watch miner logs in real-time
journalctl -u autoppia-miner -f

# Look for these indicators:
# - "Processing task" - Validator sent a task
# - "Task ... processed successfully" - Task completed
# - "actions generated" - Your miner responded
```

### View Dashboard Metrics

Access your miner's dashboard at:
```
http://YOUR_SERVER_IP:8080/dashboard
```

The dashboard shows:
- Total tasks processed
- Success rate
- Active validators
- Recent performance

### Check Metagraph Position

```bash
# View your position in the metagraph
btcli subnet metagraph --netuid 36 | grep YOUR_UID

# Shows: UID, stake, IP, port, and other miners
```

## Troubleshooting Checklist

Run through this checklist if validators aren't seeing you:

- [ ] **Registration**: Run `./scripts/utils/check_registration.sh` - shows UID?
- [ ] **Wallet Config**: Check `.env` has `WALLET_NAME` and `WALLET_HOTKEY`
- [ ] **Services Running**: `systemctl status autoppia-api autoppia-miner` - both active?
- [ ] **API Health**: `curl http://localhost:8080/health` - returns JSON?
- [ ] **Axon Listening**: `netstat -tuln | grep 8091` - port listening?
- [ ] **Firewall**: Ports 8080 and 8091 open to internet?
- [ ] **External IP**: `curl ifconfig.me` matches metagraph IP?
- [ ] **Axon Served**: `journalctl -u autoppia-miner | grep "served to network"` - found?
- [ ] **Recent Logs**: `journalctl -u autoppia-miner -n 100` - any errors?
- [ ] **Visibility Check**: Run `./scripts/utils/verify_visibility.sh` - all green?

## Expected Timeline

After fixing visibility issues:

- **0-2 minutes**: Miner starts, axon served to network
- **2-5 minutes**: Metagraph syncs, validators discover your miner
- **5-10 minutes**: First validator requests arrive
- **10-30 minutes**: Regular validator activity established

If you don't see validator requests after 30 minutes, review the troubleshooting checklist above.

## Getting Help

If you've followed this guide and still have visibility issues:

1. **Collect Diagnostics**:
   ```bash
   ./scripts/utils/check_registration.sh > registration.log
   ./scripts/utils/verify_visibility.sh > visibility.log
   journalctl -u autoppia-miner -n 200 > miner.log
   ```

2. **Check Common Issues**:
   - Insufficient TAO balance (need 0.1+ for registration)
   - Wrong network (should be "finney" not "test")
   - Wallet files not copied to server
   - VPS provider blocking ports

3. **Verify Basics**:
   - Can you SSH to your server?
   - Can you access the dashboard from your browser?
   - Does `btcli wallet overview` show your registration?
