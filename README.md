# 🚀 Autoppia Miner - Production Ready

> **Status**: ✅ **FULLY OPERATIONAL**  
> **Worker**: Deployed on Render  
> **Miner**: Running on Mac via PM2  
> **Network**: Bittensor Subnet 36 (Autoppia)

An Autoppia AI Worker for mining and processing web agent tasks. Currently competing on Subnet 36 with a registered hotkey earning TAO rewards.

## 🎯 Quick Start

**→ 👉 [READ: SETUP_AND_MINING_GUIDE.md](./SETUP_AND_MINING_GUIDE.md) ← For everything you need to know**

### One-Minute Status Check
```bash
pm2 status autoppia_miner  # Check if running
pm2 logs autoppia_miner --lines 5  # See recent activity
curl https://autoppia-miner.onrender.com/health  # Verify worker
```

## Overview

This worker is built according to the [Autoppia Documentation](https://luxit.gitbook.io/autoppia-docs) and implements:

- **Framework-agnostic design**: Works with any AI framework
- **Privacy-preserving**: No data retention, encrypted data handling
- **Modular architecture**: Easy to extend and customize
- **Production-ready**: Currently mining and earning TAO rewards
- **Integrated with Chutes API**: Advanced AI processing capabilities

## Features

- **Web Agent Tasks**: Process complex web automation tasks
- **AI Generation**: Generate action sequences using GPT-4 via Chutes API
- **Health Monitoring**: Built-in health checks and metrics
- **RESTful API**: HTTP API for integration with Bittensor validators
- **Process Management**: Stable operation via PM2 with auto-restart

## ⚡ Quick Start (Already Done!)

The system is already set up and running. For detailed setup instructions, see [SETUP_AND_MINING_GUIDE.md](./SETUP_AND_MINING_GUIDE.md).

### If Starting Fresh
```bash
# 1. Clone repository
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner

# 2. Set up environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure
cp env.example .env
# Edit .env with your Chutes API key

# 4. Start worker
python api.py
```

## Configuration

See [SETUP_AND_MINING_GUIDE.md](./SETUP_AND_MINING_GUIDE.md) for complete configuration details.

**Essential Environment Variables**:
- `CHUTES_API_KEY`: Your Chutes API key (required for AI tasks)
- `CHUTES_API_URL`: Default is `https://api.chutes.ai`
- `WORKER_NAME`: Your worker's name
- `LOG_LEVEL`: INFO (default) or DEBUG for verbose logs

## 📚 API Endpoints

- **`GET /`** - Root endpoint
- **`GET /health`** - Health check
- **`POST /solve_task`** - Main Bittensor mining endpoint (used by validators)
- **`GET /metadata`** - Worker metadata
- **`GET /metrics`** - Worker metrics

## 🧪 Testing

```bash
# Run full test suite
pytest tests/ -v

# Run specific test
pytest tests/test_worker.py::TestAutoppiaWorker::test_mine_task -v
```

## 🌐 Currently Running

This worker is currently:
- ✅ **Deployed on Render**: https://autoppia-miner.onrender.com
- ✅ **Mining on Subnet 36**: Autoppia Web Agents Subnet
- ✅ **Earning TAO rewards**: With registered hotkey
- ✅ **Processing tasks**: From Bittensor validators

See [PROJECT_STATUS.md](./PROJECT_STATUS.md) for current metrics and [SETUP_AND_MINING_GUIDE.md](./SETUP_AND_MINING_GUIDE.md) for detailed information.

## 📂 Project Structure

See [PROJECT_STATUS.md](./PROJECT_STATUS.md) for a detailed breakdown.

Key files:
- `worker.py` - Core worker logic
- `api.py` - FastAPI server with endpoints
- `requirements.txt` - Python dependencies
- `Dockerfile` / `render.yaml` - Deployment config

## 🛡️ Privacy & Security

- **No data retention**: Data processed but not stored
- **Encrypted communication**: All API calls use HTTPS
- **Privacy-preserving**: Following Autoppia standards
- **Audit logging**: Configurable log levels for security

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [SETUP_AND_MINING_GUIDE.md](./SETUP_AND_MINING_GUIDE.md) | **⭐ START HERE** - Complete comprehensive guide |
| [OPERATIONS_MANUAL.md](./OPERATIONS_MANUAL.md) | Daily operations & quick commands |
| [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) | Status, configs, troubleshooting, API keys |

## 🔗 Resources

- [Autoppia Docs](https://luxit.gitbook.io/autoppia-docs)
- [Bittensor Docs](https://docs.bittensor.com)
- [Subnet 36 Stats](https://taostats.io/subnets/36/)
- [GitHub - Autoppia](https://github.com/autoppia)

## 📄 License

MIT License - see [LICENSE](./LICENSE) file for details
