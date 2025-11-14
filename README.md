# Autoppia Miner - Modular IWA Implementation

Minimal, fast, and effective IWA miner based on official ApifiedWebAgent pattern from `autoppia_iwa`.

## 🏗️ Architecture

Modular structure following best practices:

```
autoppia-miner/
├── api/                    # API server module
│   ├── server.py          # FastAPI app
│   ├── endpoints.py       # Route handlers
│   ├── agent/             # Agent implementations
│   │   ├── base.py        # Base interface
│   │   └── template.py    # Template agent
│   ├── actions/           # Action generation
│   │   ├── generator.py   # Action sequences
│   │   ├── converter.py   # IWA format conversion
│   │   └── selectors.py   # Selector strategies
│   └── utils/             # Utilities
│       ├── keywords.py
│       └── classification.py
├── miner/                  # Bittensor miner
│   └── miner.py
├── config/                 # Configuration
│   └── settings.py
└── tests/                  # Tests
    └── test_api.py
```

## Quick Start

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp env.example .env
# Edit .env with your settings
```

### 3. Start API Server

```bash
# New modular way
python3 -m api.server

# Or legacy way (still works)
python3 api.py
```

API runs on `http://localhost:8080`

### 4. Start Miner

```bash
# New modular way
python3 -m miner.miner --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY --network finney --axon.port 8091

# Or legacy way (still works)
python3 miner.py --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY --network finney --axon.port 8091
```

### 5. Test API

```bash
python3 tests/test_api.py
```

## Features

- ✅ **Official IWA BaseAction Format** - Compliant with IWA specifications
- ✅ **Modular Architecture** - Clean, maintainable code structure
- ✅ **Smart Selector Generation** - Multiple fallback strategies for robustness
- ✅ **Context-Aware Actions** - Intelligent action sequences based on prompts
- ✅ **Fast Response Times** - Optimized for speed
- ✅ **Minimal Dependencies** - Lightweight and efficient
- ✅ **Backward Compatible** - Old entry points still work

## API Endpoints

- `POST /solve_task` - Main endpoint (returns IWA BaseAction format)
- `GET /health` - Health check
- `GET /` - Root endpoint with API info

## Configuration

Edit `.env`:

```env
# API
API_HOST=0.0.0.0
API_PORT=8080

# Miner
SUBNET_UID=36
NETWORK=finney
AXON_PORT=8091
API_URL=http://localhost:8080

# Agent
AGENT_TYPE=template
```

## Testing

### Local Testing

```bash
python3 tests/test_api.py
```

### IWA Playground Testing

1. Set up HTTPS tunnel (see `SIMPLE_HTTPS.md`)
2. Go to: https://infinitewebarena.autoppia.com/playground
3. Enter your HTTPS API URL

## Deployment

### DigitalOcean Droplet

```bash
# On your droplet
cd /opt/autoppia-miner
git pull origin main
pip install -r requirements.txt
systemctl restart autoppia-api
systemctl restart autoppia-miner
```

### HTTPS Setup

For playground access, set up HTTPS tunnel:

```bash
# Quick setup (see SIMPLE_HTTPS.md)
cloudflared tunnel --url http://localhost:8080
```

## Monitoring

### Check Validator Activity

```bash
bash CHECK_VALIDATOR_ACTIVITY.sh
```

### Monitor Logs

```bash
# Miner logs
journalctl -u autoppia-miner -f

# API logs
journalctl -u autoppia-api -f
```

### Overnight Activity Report

```bash
bash CHECK_OVERNIGHT_ACTIVITY.sh
```

## Project Status

- ✅ Phase 1: Modular architecture (COMPLETE)
- ⏭️ Phase 2: Enhancements (as needed)
- ⏭️ Phase 3: Comprehensive testing
- ⏭️ Phase 4: Deployment optimization

## Documentation

- `REBUILD_PLAN.md` - Complete rebuild plan
- `IMPLEMENTATION_GUIDE.md` - Detailed implementation guide
- `IMPORTANT_LINKS.md` - Key resources and links
- `PHASE1_STATUS.md` - Phase 1 completion status

## References

- **Autoppia Docs**: https://luxit.gitbook.io/autoppia-docs
- **IWA Home**: https://infinitewebarena.autoppia.com/home
- **IWA Playground**: https://infinitewebarena.autoppia.com/playground
- **GitHub**: https://github.com/autoppia/autoppia_web_agents_subnet
