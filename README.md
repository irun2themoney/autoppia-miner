# Autoppia Miner - Minimal IWA Implementation

Minimal IWA miner based on official ApifiedWebAgent pattern from `autoppia_iwa`.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp env.example .env
# Edit .env with your settings (API_URL, CHUTES_API_KEY if needed)

# Start API server
python3 api.py
# API runs on http://localhost:8080

# Test API (in another terminal)
python3 test_api.py

# Start Miner (for Bittensor network)
python3 miner.py --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY --network finney --axon.port 8091
```

## Project Structure

```
autoppia-miner/
├── api.py              # HTTP API server (ApifiedWebAgent endpoint)
├── miner.py            # Bittensor miner (Subnet 36)
├── test_api.py         # Quick test script
├── requirements.txt    # Dependencies
├── .env               # Configuration (your keys)
└── README.md          # This file
```

## API Endpoints

- `POST /solve_task` - Main endpoint (returns IWA BaseAction format)
- `GET /health` - Health check

## Features

- ✅ Official IWA BaseAction format
- ✅ Smart selector generation (tagContainsSelector, attributeValueSelector)
- ✅ Context-aware action sequences
- ✅ Minimal dependencies (5 packages)
- ✅ Fast response times

## Configuration

Edit `.env`:
- `API_URL` - API endpoint URL (default: http://localhost:8080)
- `CHUTES_API_KEY` - Optional (if needed for future features)

## Testing

```bash
# Test locally
python3 test_api.py

# Test on IWA Playground
# Go to: https://infinitewebarena.autoppia.com/playground
# Enter: http://YOUR_IP:8080
```

## Deployment

See `scripts/` directory for deployment scripts.
