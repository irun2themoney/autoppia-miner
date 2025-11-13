# 🚀 Autoppia Miner - Complete Setup & Mining Guide

> **Current Status**: ✅ **FULLY OPERATIONAL**
> - Worker deployed on Render: https://autoppia-miner.onrender.com
> - Miner running on local Mac via PM2
> - Hotkey registered on Subnet 36 (Autoppia)

---

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the System](#running-the-system)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

---

## ⚡ Quick Start

### Prerequisites
- macOS or Linux
- Python 3.8+
- Node.js (for PM2 process management)

### Get Up and Running (5 minutes)

```bash
# 1. Navigate to project directory
cd /Users/illfaded2022/Desktop/WORKSPACE/autoppia-miner

# 2. Check if miner is already running
pm2 status autoppia_miner

# 3. If not running, start it
pm2 start ecosystem.config.js

# 4. Monitor in real-time
pm2 monit autoppia_miner

# 5. View recent logs
pm2 logs autoppia_miner --lines 20 --nostream
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Bittensor Network                      │
│              (Subnet 36: Autoppia/Web Agents)            │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼────┐         ┌─────▼─────┐
   │ Validator│         │  Miner    │
   │          │         │(Your Mac) │
   └──────────┘         └─────┬─────┘
                              │
                    ┌─────────▼────────┐
                    │  Miner Process   │
                    │  (PM2 managed)   │
                    └─────────┬────────┘
                              │
                    ┌─────────▼────────┐
                    │ Worker Endpoint  │
                    │ /solve_task      │
                    └─────────┬────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Render Deployment │
                    │ https://autoppia-  │
                    │ miner.onrender.com │
                    └────────────────────┘
```

### How It Works

1. **Validators** on Subnet 36 send tasks to your miner
2. **Miner** (running locally) receives tasks via Bittensor protocol
3. **Miner** forwards tasks to **Worker** via HTTP `/solve_task` endpoint
4. **Worker** (deployed on Render) processes tasks using AI
5. **Worker** returns action sequences to miner
6. **Miner** sends results back to validators on Bittensor

---

## 💾 Installation

### Step 1: Clone Repository (if not already done)
```bash
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner
```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Autoppia Miner
```bash
# Clone the Autoppia subnet repository
cd ~
git clone https://github.com/opentensor/autoppia_web_agents_subnet.git
cd autoppia_web_agents_subnet

# Initialize submodules
git submodule update --init --recursive

# Create miner environment
python3 -m venv miner_env
source miner_env/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
cd autoppia_iwa_module && pip install -e . && cd ..
pip install -e .

# Install Bittensor CLI
pip install bittensor
```

### Step 4: Install Node.js and PM2 (if not already installed)
```bash
# Check if Node.js is installed
node --version

# If not, install via Homebrew
brew install node

# Install PM2 globally
npm install -g pm2
```

---

## ⚙️ Configuration

### 1. Worker Configuration (.env)

Located at: `/Users/illfaded2022/Desktop/WORKSPACE/autoppia-miner/.env`

```env
# Chutes API Configuration
CHUTES_API_KEY=cpk_10041a5a8517400ba3c5690ab89ae279.97cdedde58e45965820657bd8ec790fa.jAcea2MMpmVk7u0Iv0HLFfWczYv8IT7L
CHUTES_API_URL=https://api.chutes.ai

# Worker Configuration
WORKER_NAME=autoppia-miner
WORKER_VERSION=0.1.0
WORKER_DESCRIPTION=An Autoppia AI Worker for mining and processing tasks

# Logging
LOG_LEVEL=INFO
```

### 2. Miner Configuration (.env)

Located at: `~/autoppia_web_agents_subnet/.env`

```env
WALLET_NAME=default
HOTKEY_NAME=default
LLM_PROVIDER="local"
LOCAL_MODEL_ENDPOINT="https://autoppia-miner.onrender.com/solve_task"
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""
LOG_LEVEL="INFO"
```

### 3. PM2 Configuration (ecosystem.config.js)

Located at: `~/autoppia_web_agents_subnet/ecosystem.config.js`

```javascript
module.exports = {
  apps: [{
    name: 'autoppia_miner',
    cwd: '/Users/illfaded2022/autoppia_web_agents_subnet',
    script: './miner_env/bin/python',
    args: 'neurons/miner.py --netuid 36 --subtensor.network finney --wallet.name default --wallet.hotkey default --axon.port 8091',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M'
  }]
};
```

---

## 🏃 Running the System

### Start the Worker (Render)

The worker is already deployed and running on Render at:
```
https://autoppia-miner.onrender.com
```

To redeploy or update:
```bash
cd /Users/illfaded2022/Desktop/WORKSPACE/autoppia-miner
git push origin main  # Will auto-trigger Render deployment
```

### Start the Miner (Local)

```bash
# Navigate to miner directory
cd ~/autoppia_web_agents_subnet

# Activate virtual environment
source miner_env/bin/activate

# Start with PM2
pm2 start ecosystem.config.js

# Or start directly (for debugging)
python neurons/miner.py --netuid 36 --subtensor.network finney --wallet.name default --wallet.hotkey default --axon.port 8091
```

### Verify Everything is Running

```bash
# Check PM2 status
pm2 status

# Check worker health
curl https://autoppia-miner.onrender.com/health

# Check recent miner logs
pm2 logs autoppia_miner --lines 20 --nostream
```

---

## 📊 Monitoring

### Real-time Monitoring

```bash
# Watch all processes in real-time
pm2 monit

# Or stream logs continuously
pm2 logs autoppia_miner
```

### Check System Status

```bash
# View Bittensor wallet balance
btcli wallet balance --wallet.name default

# Check subnet registration
btcli subnet list --wallet.name default

# View detailed miner info
pm2 show autoppia_miner
```

### Quick Status Script

```bash
# One-line status check
echo "=== MINER STATUS ===" && pm2 status autoppia_miner | tail -1 && echo "=== RECENT LOGS ===" && pm2 logs autoppia_miner --lines 5 --nostream && echo "=== WORKER HEALTH ===" && curl -s https://autoppia-miner.onrender.com/health | python3 -m json.tool
```

---

## 🔧 Troubleshooting

### Miner Not Starting

**Problem**: `pm2 start ecosystem.config.js` fails

**Solution**:
```bash
# Check Python path
which python
echo $PATH

# Verify miner_env is activated
source ~/autoppia_web_agents_subnet/miner_env/bin/activate
python --version

# Try starting manually first
cd ~/autoppia_web_agents_subnet
python neurons/miner.py --netuid 36 --subtensor.network finney --wallet.name default --wallet.hotkey default --axon.port 8091
```

### Worker Not Responding

**Problem**: Timeout when hitting `/solve_task`

**Solution**:
```bash
# Check if Render app is running
curl -I https://autoppia-miner.onrender.com/health

# Check worker logs in Render dashboard
# https://dashboard.render.com/

# Restart worker (from Render dashboard)
# Or redeploy via git push
cd /Users/illfaded2022/Desktop/WORKSPACE/autoppia-miner
git push origin main
```

### Hotkey Not Registered

**Problem**: See "Not Registered" on TAO Stats

**Solution**:
```bash
# Register hotkey on subnet 36
cd ~/autoppia_web_agents_subnet
source miner_env/bin/activate

btcli subnet register \
  --netuid 36 \
  --subtensor.network finney \
  --wallet.name default \
  --wallet.hotkey default
```

### Out of Memory

**Problem**: Process keeps restarting

**Solution**:
```bash
# Increase PM2 memory limit in ecosystem.config.js
# Change: max_memory_restart: '500M' to '1000M'

# Then restart
pm2 restart ecosystem.config.js

# Or kill all and restart
pm2 kill
pm2 start ecosystem.config.js
```

---

## 📝 API Reference

### Worker Endpoints

#### Health Check
```bash
curl -X GET https://autoppia-miner.onrender.com/health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-13T12:34:56Z",
  "uptime": 3600,
  "worker_name": "autoppia-miner"
}
```

#### Solve Task (Used by Miner)
```bash
curl -X POST https://autoppia-miner.onrender.com/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "task_123",
    "prompt": "Click the login button",
    "url": "https://example.com",
    "seed": 12345,
    "web_project_name": "example_project",
    "specifications": {}
  }'
```

**Response**:
```json
{
  "task_id": "task_123",
  "actions": [
    {"action_type": "navigate", "url": "https://example.com"},
    {"action_type": "wait", "duration": 2.0},
    {"action_type": "click", "x": 100, "y": 100}
  ],
  "success": true,
  "message": "Task processed successfully"
}
```

---

## 📚 Resources

- [Autoppia Docs](https://luxit.gitbook.io/autoppia-docs)
- [Bittensor Docs](https://docs.bittensor.com)
- [Subnet 36 Info](https://taostats.io/subnets/36/)
- [Render Dashboard](https://dashboard.render.com/)

---

## 🎯 Next Steps (Future Improvements)

- [ ] Deploy miner to cloud VPS for 24/7 operation
- [ ] Add advanced web automation capabilities
- [ ] Implement caching for frequently seen tasks
- [ ] Add custom reward tracking dashboard
- [ ] Optimize response times for faster task completion

---

**Last Updated**: November 13, 2025
**Status**: ✅ Production Ready

