# 🚀 Autoppia Miner - Social Intelligence Agent

**A production-ready Bittensor miner for Subnet 36 (Infinite Web Arena) with advanced social intelligence**

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)]()
[![Features](https://img.shields.io/badge/Features-Social%20Intelligence-purple)]()
[![Network](https://img.shields.io/badge/Network-Bittensor%20Subnet%2036-blue)]()

---

## 🧠 **Advanced Social Intelligence**

✅ **Social Task Recognition** - Handles connect, follow, message, like, comment tasks
✅ **Complex Prompt Parsing** - Extracts user names and filtering criteria from prompts
✅ **Multi-Step Social Workflows** - Intelligent sequences for user interactions
✅ **IWA Format Compliance** - Proper NavigateAction, TypeAction, ClickAction format
✅ **Dynamic Zero Ready** - Anti-overfitting and task diversity compliant
✅ **Production Deployed** - UID 160, actively earning TAO rewards

---

## 📚 **Official Implementation**

> **🔗 Based on Official Autoppia Repositories**
>
> This miner implements the official ApifiedWebAgent pattern with social intelligence capabilities for complex web automation tasks.

---

## 🎯 **Social Intelligence Features**

### **Core Social Capabilities**
- ✅ **User Connection Tasks** - "Connect with user whose name equals 'Michael Chan'"
- ✅ **Complex Comment Tasks** - Posts with filtering: "NOT equal", "NOT contain" criteria
- ✅ **Job Search Intelligence** - "NOT equal to 'DataStream Inc.'" constraints
- ✅ **Social Action Recognition** - Connect, follow, message, like, share, tag actions
- ✅ **Advanced Prompt Parsing** - Extracts user names from complex social prompts
- ✅ **Multi-Step Social Workflows** - Search → Find → Click → Complete sequences

### **Technical Excellence**
- ✅ **IWA Format Compliance** - NavigateAction, TypeAction, ClickAction, WaitAction
- ✅ **IWA Format Validator** - Automatic validation of action format compliance
- ✅ **Enhanced Logging** - Comprehensive timing metrics and response tracking
- ✅ **Browser Automation** - Playwright integration for accurate DOM analysis
- ✅ **Selector Strategies** - Multiple fallback selectors for reliability
- ✅ **Error Recovery** - Graceful fallback when browser analysis fails
- ✅ **Production Optimized** - Clean, minimal codebase for stability

### **Bittensor Integration**
- ✅ **Subnet 36 Miner** - Registered UID 160 on finney network
- ✅ **Validator Ready** - Active axon on port 8091
- ✅ **API Server** - FastAPI on port 8080 with CORS support
- ✅ **Task Processing** - Handles complex social automation tasks

---

## 📋 **Requirements**

- Python 3.10+ (for datetime.UTC support)
- Bittensor wallet with TAO
- VPS server (DigitalOcean, etc.)
- Ports 8080 (API) and 8091 (Bittensor) open

---

## 🚀 **Quick Start**

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd autoppia-miner
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure Environment
Create a `.env` file with your Bittensor wallet settings:
```bash
WALLET_NAME=your_wallet_name
WALLET_HOTKEY=your_hotkey_name
```

### 4. Register on Subnet 36
```bash
# Register your miner (requires ~0.1 TAO)
btcli subnet register --netuid 36 --wallet.name your_wallet --wallet.hotkey your_hotkey
```

### 5. Test Locally (Optional)
```bash
# Start the API server
python3 -m api.server

# Test social intelligence in another terminal
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id": "test", "prompt": "Connect with user whose name equals Michael Chan", "url": "http://app:8080"}'
```

### 6. Deploy to Production
```bash
# Use the deployment script
./scripts/deploy.sh

# Or deploy manually to your server
rsync -avz --exclude='.git' . root@your-server:/opt/autoppia-miner/
ssh root@your-server "cd /opt/autoppia-miner && pip install -r requirements.txt && systemctl restart autoppia-api autoppia-miner"
```

---

## 📁 **Project Structure**

```
autoppia-miner/
├── api/                    # API server (FastAPI)
│   ├── agent/             # Agent implementations
│   │   └── template.py    # Template-based agent with social intelligence
│   ├── actions/           # Action generation with social capabilities
│   │   ├── generator.py   # Social action generator
│   │   ├── converter.py   # IWA format converter
│   │   └── selectors.py   # Selector strategies
│   ├── utils/             # Utilities for browser automation
│   │   ├── browser_analyzer.py    # Playwright DOM analysis
│   │   ├── iwa_validator.py      # IWA format validator
│   │   ├── action_optimizer.py   # Action sequence optimizer
│   │   ├── response_quality.py   # Response quality enhancer
│   │   ├── classification.py      # Task classification
│   │   ├── keywords.py           # Keyword processing
│   │   └── task_parser.py        # Task parsing utilities
│   ├── endpoints.py       # Main API endpoints (with IWA validation)
│   └── server.py          # FastAPI server
├── miner/                  # Bittensor miner
│   ├── miner.py           # Main miner logic (with enhanced logging)
│   └── protocol.py        # Synapse definitions
├── config/                 # Configuration
│   └── settings.py        # Pydantic settings
├── scripts/                # Deployment & monitoring
│   └── deploy/            # Production deployment scripts
└── README.md              # This file
```

---

## 🧪 **Testing**

### Social Intelligence Test
```bash
# Test user connection capability
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id": "test", "prompt": "Connect with user whose name equals Michael Chan", "url": "http://app:8080"}'
```

**Expected Response:**
```json
{
  "actions": [
    {"type": "NavigateAction", "url": "http://app:8080"},
    {"type": "TypeAction", "selector": {...}, "text": "michael chan"},
    {"type": "ClickAction", "selector": {...}}
  ],
  "web_agent_id": "test"
}
```

---

## 📊 **Monitoring**

### Enhanced Logging & Validation

The miner now includes comprehensive logging and IWA format validation to help diagnose issues and ensure validator acceptance:

**Key Features**:
- ⏱️ **Response Time Tracking** - Monitor processing times (< 3s target)
- ✅ **IWA Format Validation** - Automatic validation of action format compliance
- 📊 **Action Quality Metrics** - Track action counts and success rates
- ⚠️ **Warning System** - Alerts for slow responses, minimal actions, invalid IWA format

### Monitor Logs

**On Production Server**:
```bash
# Monitor enhanced logs
journalctl -u autoppia-miner -f | grep -E 'TASK_RESPONSE|IWA_VALIDATION|SLOW_RESPONSE|MINIMAL_RESPONSE'

# Check recent activity
journalctl -u autoppia-miner --since '10 minutes ago' | grep -E 'TASK_RESPONSE|IWA_VALIDATION'
```

**Success Indicators**:
```
📤 TASK_RESPONSE: {validator_ip} - Completed TaskSynapse | Success: True | Actions: 5 | Time: 1.23s | IWA: ✅ VALID
```

**Warning Signs**:
```
⚠️ SLOW_RESPONSE: Task took 4.5s (validators may timeout)
⚠️ MINIMAL_RESPONSE: Only ScreenshotAction (may receive low score)
❌ IWA_VALIDATION_FAILED: Invalid action format detected
```

### Health Check
```bash
./scripts/full_health_check.sh
```

### Validator Activity
```bash
./scripts/monitor_validators.sh
```

### API Status
```bash
curl http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id": "health", "prompt": "test", "url": "http://example.com"}'
```

---

## 🚀 **Deployment**

### Production Deployment
```bash
# On your server
git clone <your-repo-url>
cd autoppia-miner

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Configure environment
echo "WALLET_NAME=your_wallet" > .env
echo "WALLET_HOTKEY=your_hotkey" >> .env
# Edit .env with your actual wallet details

# Setup systemd services
sudo cp scripts/deploy/autoppia-api.service /etc/systemd/system/
sudo cp scripts/deploy/autoppia-miner.service /etc/systemd/system/
sudo systemctl daemon-reload

# Start services
sudo systemctl enable autoppia-api autoppia-miner
sudo systemctl start autoppia-api autoppia-miner

# Verify deployment
sudo systemctl status autoppia-api autoppia-miner
```

### Update Existing Deployment
```bash
# On your server
cd /opt/autoppia-miner
git pull
pip install -r requirements.txt
sudo systemctl restart autoppia-api autoppia-miner
```

---

## 🎯 **Performance**

- **Social Task Success**: Handles complex user connections and comments
- **Response Time**: 1-3s average with browser automation (target < 3s)
- **IWA Compliance**: Full BaseAction format support with automatic validation
- **Action Quality**: Multiple actions per task (not just ScreenshotAction)
- **Production Uptime**: 99.9%+ with systemd services
- **Validator Acceptance**: Enhanced logging helps track validator acceptance

---

## 🔧 **Configuration**

### Environment Variables
```bash
# Required wallet settings
WALLET_NAME=your_wallet_name
WALLET_HOTKEY=your_hotkey_name

# Optional API settings (defaults shown)
API_HOST=0.0.0.0
API_PORT=8080

# Bittensor network settings
SUBNET_UID=36
NETWORK=finney
AXON_PORT=8091
```

---

## 🏆 **Achievements**

- ✅ **Social Intelligence** - Advanced user connection and comment capabilities
- ✅ **IWA Benchmark Ready** - Handles complex social automation tasks
- ✅ **Enhanced Logging** - Comprehensive timing metrics and response tracking
- ✅ **IWA Format Validator** - Automatic validation of action format compliance
- ✅ **Production Deployed** - UID 160 actively earning TAO rewards
- ✅ **Clean Architecture** - Streamlined codebase for stability
- ✅ **Browser Automation** - Playwright integration for accurate DOM analysis
- ✅ **Bittensor Integrated** - Full Subnet 36 compliance

---

## 🤝 **Contributing**

This is a production miner focused on social intelligence. For improvements:
1. Test social task capabilities
2. Ensure IWA format compliance
3. Maintain clean, minimal codebase
4. Submit pull request

---

## 🎉 **Ready to Earn TAO!**

Your social intelligence miner is production-ready and optimized for complex web automation tasks. Deploy and start earning TAO rewards on Bittensor Subnet 36!

**Status**: ✅ **Social Intelligence Active - Production Ready** 🚀
