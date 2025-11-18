# 📁 Project Structure

## 🎯 **Clean, Organized Structure**

```
autoppia-miner/
├── api/                          # API server code
│   ├── agent/                    # Agent implementations
│   │   ├── base.py              # Base agent interface
│   │   ├── template.py          # Template agent (pattern-based)
│   │   ├── hybrid.py            # Enhanced template with learning
│   │   └── chutes.py            # Chutes LLM agent (deprecated)
│   ├── actions/                  # Action generation
│   │   ├── generator.py         # Enhanced action generator
│   │   ├── converter.py         # IWA format converter
│   │   └── selectors.py         # Selector strategies
│   ├── utils/                    # Utility modules
│   │   ├── task_parser.py       # Task parsing & extraction
│   │   ├── pattern_learner.py   # Pattern learning
│   │   ├── vector_memory.py     # Vector memory store
│   │   ├── task_complexity.py   # Complexity analysis
│   │   ├── action_validator.py  # Action validation
│   │   ├── action_sequencer.py  # Action sequencing
│   │   ├── action_optimizer.py  # Action optimization
│   │   ├── selector_enhancer.py # Selector enhancement
│   │   ├── error_recovery.py    # Error recovery
│   │   ├── smart_cache.py       # Response caching
│   │   ├── visual_selectors.py  # Visual selector generation
│   │   ├── feedback_loop.py     # Feedback learning
│   │   ├── ensemble_generator.py # Ensemble strategies
│   │   ├── performance_optimizer.py # Performance optimization
│   │   ├── adaptive_retry.py    # Adaptive retry logic
│   │   ├── mutation_detector.py # Mutation detection
│   │   ├── advanced_metrics.py  # Advanced metrics
│   │   └── metrics.py           # Basic metrics
│   ├── endpoints.py              # Main API endpoints
│   ├── endpoints_dashboard.py    # Dashboard endpoints
│   ├── endpoints_feedback.py     # Feedback endpoints
│   └── server.py                 # FastAPI server
│
├── miner/                        # Bittensor miner code
│   ├── miner.py                  # Main miner logic
│   └── protocol.py               # Synapse protocol handlers
│
├── config/                       # Configuration
│   └── settings.py               # Settings management
│
├── tests/                        # Test files
│   ├── test_official.py          # Official test suite
│   ├── test_official_robust.py   # Robust test suite
│   ├── test_api.py               # API tests
│   └── test_*.py                 # Other test files
│
├── scripts/                      # Utility scripts
│   ├── deploy_*.sh               # Deployment scripts
│   ├── monitor_*.sh              # Monitoring scripts
│   ├── check_*.sh                # Health check scripts
│   └── *.sh                      # Other utility scripts
│
├── docs/                         # Documentation
│   ├── chutes/                   # Chutes-related docs (archived)
│   ├── validator/                # Validator discovery docs
│   ├── playground/               # Playground testing docs
│   ├── status/                   # Status updates
│   ├── archive/                  # Archived documentation
│   └── *.md                      # Main documentation
│
├── README.md                     # Main README
├── requirements.txt              # Python dependencies
├── env.example                   # Environment template
├── LICENSE                       # License file
└── .gitignore                    # Git ignore rules
```

---

## 📂 **Directory Purposes**

### **`api/`** - API Server
- **`agent/`**: Agent implementations (template, hybrid, chutes)
- **`actions/`**: Action generation and conversion
- **`utils/`**: Utility modules for learning, optimization, metrics
- **`endpoints*.py`**: API endpoint handlers

### **`miner/`** - Bittensor Miner
- **`miner.py`**: Main miner logic, axon serving
- **`protocol.py`**: Synapse protocol handlers

### **`config/`** - Configuration
- **`settings.py`**: Settings management with Pydantic

### **`tests/`** - Testing
- Official test suites
- API tests
- Integration tests

### **`scripts/`** - Utilities
- Deployment scripts
- Monitoring scripts
- Health check scripts

### **`docs/`** - Documentation
- **`chutes/`**: Chutes-related docs (archived)
- **`validator/`**: Validator discovery documentation
- **`playground/`**: Playground testing guides
- **`status/`**: Status updates and reports
- **`archive/`**: Archived documentation

---

## 🎯 **Key Files**

### **Entry Points**:
- **`api/server.py`**: FastAPI server (runs on port 8080)
- **`miner/miner.py`**: Bittensor miner (serves axon on port 8091)

### **Core Logic**:
- **`api/agent/hybrid.py`**: Enhanced template agent with learning
- **`api/actions/generator.py`**: Action generation with 10+ patterns
- **`api/utils/task_parser.py`**: Task parsing and extraction
- **`api/utils/pattern_learner.py`**: Pattern learning system

### **Configuration**:
- **`config/settings.py`**: All settings
- **`env.example`**: Environment variable template
- **`.env`**: Local environment (not in git)

---

## 🧹 **Cleanup Rules**

### **What's Ignored**:
- `__pycache__/` - Python cache
- `venv/` - Virtual environment
- `.env` - Environment variables
- `*.log` - Log files
- `test_*.py` in root (moved to tests/)
- Old duplicate files (`miner.py`, `api.py` in root)

### **What's Organized**:
- All `.md` files → `docs/` (except README.md)
- All `test_*.py` → `tests/`
- All `*.sh` → `scripts/`
- Chutes docs → `docs/chutes/`
- Status docs → `docs/status/`

---

**Status**: ✅ **Project Cleaned and Organized!**

