# 🏗️ Complete Miner Rebuild Plan - From Ground Up

## Research Summary

Based on official Autoppia documentation and top miner analysis:

### Key Findings:
1. **Official Pattern**: ApifiedWebAgent (HTTP API pattern)
2. **Top Agent**: `browser-use` agent for competitive performance
3. **LLM Provider**: External APIs (OpenAI) recommended over local
4. **Architecture**: HTTP API server + Bittensor miner
5. **Process Management**: PM2 for reliability
6. **IWA Format**: Strict BaseAction format required

## Step-by-Step Rebuild Plan

### Phase 1: Foundation & Architecture

#### Step 1.1: Project Structure
```
autoppia-miner/
├── api/                    # API server module
│   ├── __init__.py
│   ├── server.py          # FastAPI server
│   ├── agent.py           # Web agent logic
│   ├── actions.py         # Action generation
│   └── selectors.py       # Selector strategies
├── miner/                  # Bittensor miner module
│   ├── __init__.py
│   ├── miner.py           # Main miner class
│   └── synapse.py         # Synapse handling
├── config/                 # Configuration
│   ├── settings.py        # Settings management
│   └── env.example        # Environment template
├── tests/                  # Tests
│   ├── test_api.py
│   └── test_miner.py
├── scripts/                # Deployment scripts
│   ├── setup.sh
│   └── deploy.sh
├── requirements.txt
├── .env
└── README.md
```

#### Step 1.2: Environment Setup
```bash
# Python 3.11+ required
python3 --version

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Phase 2: Core API Implementation

#### Step 2.1: FastAPI Server Setup
**File**: `api/server.py`

**Requirements:**
- FastAPI with CORS middleware
- `/solve_task` endpoint (POST)
- `/health` endpoint (GET)
- Proper error handling
- Request/response logging

**Key Features:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="IWA Miner API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.post("/solve_task")
async def solve_task(request: TaskRequest) -> TaskResponse:
    # Process task and return IWA BaseAction format
    pass
```

#### Step 2.2: Web Agent Implementation
**File**: `api/agent.py`

**Options:**
1. **Browser-Use Agent** (Recommended - Top Performance)
   - Official browser-use library
   - Advanced web interaction
   - Better success rates

2. **Custom Agent** (Current - Template-based)
   - Lightweight
   - Fast response
   - Template-driven

**Decision**: Start with custom (lightweight), add browser-use later if needed

#### Step 2.3: Action Generation
**File**: `api/actions.py`

**Requirements:**
- IWA BaseAction format compliance
- Multiple selector strategies
- Context-aware generation
- Fallback mechanisms

**Action Types:**
- NavigateAction
- ClickAction
- TypeAction
- WaitAction
- ScreenshotAction
- ScrollAction

#### Step 2.4: Selector Strategies
**File**: `api/selectors.py`

**Requirements:**
- Multiple selector types:
  - `tagContainsSelector`
  - `attributeValueSelector`
  - `xpathSelector` (if needed)
- Fallback chain
- Dynamic environment support (D1-D4)

### Phase 3: Bittensor Miner

#### Step 3.1: Miner Class
**File**: `miner/miner.py`

**Requirements:**
- Bittensor integration
- Axon setup
- Synapse processing
- API forwarding
- Error handling
- Logging

#### Step 3.2: Synapse Handling
**File**: `miner/synapse.py`

**Requirements:**
- Extract task data from synapse
- Forward to API
- Map response to synapse
- Handle errors gracefully

### Phase 4: Configuration & Settings

#### Step 4.1: Settings Management
**File**: `config/settings.py`

**Configuration:**
- API settings
- Miner settings
- Agent settings
- LLM settings (if using)
- Logging settings

#### Step 4.2: Environment Variables
**File**: `.env`

```env
# API
API_HOST=0.0.0.0
API_PORT=8080

# Miner
SUBNET_UID=36
NETWORK=finney
AXON_PORT=8091

# Agent
AGENT_TYPE=custom  # or browser-use
LLM_PROVIDER=none  # or openai

# Logging
LOG_LEVEL=INFO
```

### Phase 5: Testing & Validation

#### Step 5.1: Unit Tests
- Test action generation
- Test selector strategies
- Test API endpoints
- Test miner integration

#### Step 5.2: Integration Tests
- Test full flow (validator → miner → API → response)
- Test IWA format compliance
- Test error handling

#### Step 5.3: Playground Testing
- Test on IWA playground
- Verify action format
- Check success rates
- Monitor performance

### Phase 6: Deployment

#### Step 6.1: Process Management
- Use systemd (current) or PM2 (official)
- Auto-restart on failure
- Log rotation
- Health checks

#### Step 6.2: Monitoring
- Log aggregation
- Metrics collection
- Error tracking
- Performance monitoring

#### Step 6.3: HTTPS Setup
- Cloudflare Tunnel (quick)
- Let's Encrypt (permanent)
- SSL certificate

## Implementation Priority

### MVP (Minimum Viable Product)
1. ✅ Basic API server with `/solve_task`
2. ✅ IWA BaseAction format compliance
3. ✅ Basic action generation
4. ✅ Bittensor miner integration
5. ✅ Error handling

### Phase 1 Improvements
1. Multiple selector strategies
2. Fallback mechanisms
3. Better task classification
4. Improved action sequences

### Phase 2 Enhancements
1. Browser-use agent integration
2. LLM integration (if needed)
3. Advanced selector strategies
4. Performance optimization

### Phase 3 Optimization
1. Caching (if beneficial)
2. Request optimization
3. Response time improvements
4. Success rate optimization

## Key Differences from Current Implementation

### What to Keep:
- ✅ ApifiedWebAgent pattern (HTTP API)
- ✅ IWA BaseAction format
- ✅ Fast response times
- ✅ Minimal dependencies

### What to Improve:
- 🔄 Better code organization (modules)
- 🔄 More robust selector strategies
- 🔄 Better error handling
- 🔄 Comprehensive testing
- 🔄 Better logging
- 🔄 Configuration management

### What to Add:
- ➕ Browser-use agent option
- ➕ LLM integration option
- ➕ Better monitoring
- ➕ Performance metrics
- ➕ Comprehensive tests

## Next Steps

1. **Review this plan** - Confirm approach
2. **Start Phase 1** - Set up project structure
3. **Implement Phase 2** - Build API server
4. **Implement Phase 3** - Build miner
5. **Test & Deploy** - Validate and deploy

## References

- Official Docs: https://luxit.gitbook.io/autoppia-docs
- IWA Home: https://infinitewebarena.autoppia.com/home
- GitHub: https://github.com/autoppia/autoppia_web_agents_subnet
- IWA Module: https://github.com/autoppia/autoppia_iwa

