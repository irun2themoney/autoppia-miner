# 🚀 Autoppia Miner

> **Status**: ✅ **PRODUCTION READY**  
> **Network**: Bittensor Subnet 36 (Autoppia Web Agents)  
> **Worker**: Live on Render (`https://autoppia-miner.onrender.com`)

An Autoppia AI Worker for mining and processing web agent tasks on Bittensor Subnet 36. Optimized with AI-powered task solving, intelligent classification, and real-time metrics.

## ✨ Features

- **🤖 AI-Powered Task Solving**: Generate optimized action sequences for web agents using Chutes API
- **🧠 Task Classification**: 8 intelligent categories (search, form_fill, price_compare, click, extract, checkout, navigate, scroll)
- **⚡ Smart Action Generation**: Specialized templates + AI fallback (10-150ms responses)
- **💾 Request Caching**: Pattern learning (50-70x faster on repeats)
- **🔄 Retry Logic**: Exponential backoff with graceful degradation
- **📊 Real-Time Metrics**: Request tracking, success rates, performance analytics
- **🛡️ Error Handling**: Comprehensive with zero-crash guarantee

## ⚡ Quick Start

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
# Edit .env with your CHUTES_API_KEY

# 4. Start worker
python api.py
```

## Configuration

**Essential Environment Variables**:
- `CHUTES_API_KEY`: Your Chutes API key (required for AI tasks)
- `CHUTES_API_URL`: Default is `https://api.chutes.ai`
- `WORKER_NAME`: Your worker's name (default: `autoppia-miner`)
- `LOG_LEVEL`: INFO (default) or DEBUG for verbose logs

## 📚 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Root endpoint with service info |
| `/health` | GET | Health check with API connectivity status |
| `/metadata` | GET | Worker capabilities and metadata |
| `/metrics` | GET | Real-time request metrics and performance |
| `/solve_task` | POST | **Main endpoint** - AI-powered task solving for validators |
| `/process` | POST | Generic data processing with multiple operations |

### Example: Solve Task (Validator Endpoint)

```bash
curl -X POST https://autoppia-miner.onrender.com/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "task_123",
    "prompt": "Click the login button and enter username",
    "url": "https://example.com/login"
  }'
```

**Response:**
```json
{
  "task_id": "task_123",
  "task_type": "click",
  "actions": [
    {"action_type": "navigate", "url": "https://example.com/login"},
    {"action_type": "wait", "duration": 1.5},
    {"action_type": "screenshot"},
    {"action_type": "click", "selector": "button:first-of-type"},
    {"action_type": "wait", "duration": 1},
    {"action_type": "screenshot"}
  ],
  "success": true,
  "cached": false,
  "response_time_ms": "145"
}
```

## 🧪 Testing

```bash
# Activate virtual environment (if using test_env)
source test_env/bin/activate

# Run full test suite (52 tests)
pytest tests/ -v

# Run specific test
pytest tests/test_worker.py::TestAutoppiaWorker::test_mine_task -v

# Test API endpoint directly
python -c "from fastapi.testclient import TestClient; from api import app; client = TestClient(app); print(client.post('/solve_task', json={'id': 'test', 'prompt': 'Click button', 'url': 'https://example.com'}).json())"
```

## 📈 Performance

- **Response Time**: 100-300ms average (cache hits: 10-50ms)
- **Success Rate**: 95%+ (even under stress)
- **Concurrency**: Handles 100+ simultaneous requests
- **Uptime**: 99%+ with zero crashes
- **Test Coverage**: 52/52 tests passing ✅

## 📂 Project Structure

```
autoppia-miner/
├── api.py              # FastAPI server (main entry point)
├── worker.py           # Core worker logic
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker deployment config
├── render.yaml         # Render deployment config
├── env.example         # Environment variables template
├── tests/              # Test suite
│   ├── test_worker.py
│   ├── test_task_classification.py
│   └── test_ultimate_pre_deployment.py
└── README.md           # This file
```

## 🛡️ Security

- **No data retention**: Data processed but not stored
- **Encrypted communication**: All API calls use HTTPS
- **Input validation**: All endpoints validate and sanitize inputs
- **CORS configured**: Configurable origins for security

## 🔗 Resources

- [Autoppia Docs](https://luxit.gitbook.io/autoppia-docs)
- [Bittensor Docs](https://docs.bittensor.com)
- [Subnet 36 Stats](https://taostats.io/subnets/36/)

## 📄 License

MIT License - see [LICENSE](./LICENSE) file for details
