# 🚀 Bittensor Miner Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create/Check Wallet
```bash
# List existing wallets
btcli wallet list

# Create new wallet (if needed)
btcli wallet create --name my_wallet
```

### 3. Register on Subnet 36
```bash
btcli subnet register \
  --netuid 36 \
  --wallet.name my_wallet \
  --wallet.hotkey default
```

⚠️ **Note**: Registration requires TAO tokens. Check current fees:
```bash
btcli subnet show --netuid 36
```

### 4. Configure Environment
```bash
cp env.example .env
# Edit .env and set:
# - CHUTES_API_KEY=your_key_here
# - API_URL=https://autoppia-miner.onrender.com
```

### 5. Start Miner

**Option A: Using start script**
```bash
./start_miner.sh my_wallet default
```

**Option B: Direct command**
```bash
python miner.py \
  --wallet.name my_wallet \
  --wallet.hotkey default \
  --network finney \
  --axon.port 8091
```

## How It Works

1. **Miner connects** to Bittensor subnet 36
2. **Validators discover** your miner via metagraph
3. **Validators send tasks** to your miner's axon
4. **Miner forwards** tasks to HTTP API (`api.py`)
5. **HTTP API processes** tasks and returns actions
6. **Miner sends** actions back to validators
7. **Validators evaluate** and reward you with TAO

## Architecture

```
Validator → Bittensor Network → Your Miner (miner.py) → HTTP API (api.py) → Response
```

## Requirements

- ✅ HTTP API must be running and accessible
- ✅ Miner must be registered on subnet 36
- ✅ Requires TAO tokens for registration
- ✅ Miner must stay online to receive requests
- ✅ Port forwarding may be needed for axon

## Troubleshooting

### Miner not registered
```bash
btcli wallet overview --netuid 36 --wallet.name my_wallet --wallet.hotkey default
```

### Check miner status
```bash
btcli wallet overview --netuid 36
```

### View logs
Miner logs are output to console. For HTTP API logs, check Render dashboard.

## Monitoring

- **Miner**: Check console output for validator requests
- **HTTP API**: Use `./monitor_once.sh` or `./monitor_loop.sh`
- **Metrics**: `curl https://autoppia-miner.onrender.com/metrics`

## Support

- [Autoppia Docs](https://luxit.gitbook.io/autoppia-docs)
- [Bittensor Docs](https://docs.bittensor.com)
- [Subnet 36 Stats](https://taostats.io/subnets/36/)
