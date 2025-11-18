# 📁 Project Organization

**Last Updated**: November 18, 2025  
**Status**: ✅ **FULLY ORGANIZED**

---

## 📂 **Directory Structure**

```
autoppia-miner/
├── README.md                    # Main project README
├── LICENSE                      # License file
├── requirements.txt             # Python dependencies
├── env.example                  # Environment variable template
├── .gitignore                   # Git ignore rules
│
├── api/                         # API Server Module
│   ├── server.py               # FastAPI application
│   ├── endpoints.py            # Main API endpoints
│   ├── endpoints_dashboard.py  # Dashboard endpoints
│   ├── endpoints_feedback.py   # Feedback endpoints
│   ├── agent/                  # Agent implementations
│   │   ├── base.py            # Base agent interface
│   │   ├── template.py        # Template agent
│   │   ├── hybrid.py          # Enhanced template agent
│   │   └── chutes.py          # Chutes agent (deprecated)
│   ├── actions/                # Action generation
│   │   ├── generator.py       # Action sequence generation
│   │   ├── converter.py       # IWA format conversion
│   │   └── selectors.py       # Selector strategies
│   └── utils/                  # Utility modules
│       ├── task_parser.py
│       ├── action_validator.py
│       ├── pattern_learner.py
│       ├── context_aware.py
│       ├── task_planner.py
│       ├── selector_intelligence.py
│       ├── website_detector.py
│       ├── error_recovery.py
│       ├── smart_waits.py
│       ├── advanced_metrics.py
│       └── [20+ more utilities]
│
├── miner/                       # Bittensor Miner
│   ├── miner.py                # Main miner logic
│   └── protocol.py             # Synapse protocol handlers
│
├── config/                      # Configuration
│   └── settings.py             # Settings management
│
├── tests/                       # Test Suites
│   ├── test_official.py        # Official compliance tests
│   ├── test_official_robust.py # Robust test suite
│   ├── test_api.py             # API tests
│   ├── test_ultimate.py        # Ultimate compliance test
│   ├── chutes/                 # Chutes-related tests
│   └── temp/                   # Temporary test files
│
├── scripts/                     # Utility Scripts
│   ├── deploy/                 # Deployment scripts
│   │   ├── deploy.sh
│   │   ├── deploy_to_server.sh
│   │   └── [other deploy scripts]
│   ├── monitor/                # Monitoring scripts
│   │   ├── auto_monitor.sh
│   │   ├── monitor_validator_discovery.sh
│   │   └── [other monitor scripts]
│   ├── test/                   # Testing scripts
│   │   ├── test_official.sh
│   │   ├── test_miner_directly.sh
│   │   └── [other test scripts]
│   └── utils/                  # Utility scripts
│       ├── check_*.sh
│       ├── verify_*.sh
│       └── [other utility scripts]
│
└── docs/                        # Documentation
    ├── README.md               # Documentation index
    ├── PROJECT_ORGANIZATION.md # This file
    ├── SECURITY_AUDIT.md       # Security audit report
    ├── QUICK_START_GUIDE.md    # Quick start guide
    ├── deployment/             # Deployment documentation
    ├── ratings/                # Rating & compliance docs
    ├── chutes/                 # Chutes-related docs
    ├── validator/              # Validator discovery docs
    ├── playground/             # Playground testing docs
    ├── status/                 # Status updates
    └── archive/                # Archived documentation
```

---

## 📋 **Key Directories**

### **`api/`** - API Server
- **Purpose**: HTTP API server for handling validator requests
- **Key Files**:
  - `server.py`: FastAPI application setup
  - `endpoints.py`: Main `/solve_task` endpoint
  - `endpoints_dashboard.py`: Dashboard endpoints
  - `agent/hybrid.py`: Enhanced template agent (main agent)
  - `actions/generator.py`: Action generation with 15+ patterns
  - `utils/`: 26 utility modules for intelligence, learning, optimization

### **`miner/`** - Bittensor Miner
- **Purpose**: Bittensor network integration
- **Key Files**:
  - `miner.py`: Main miner logic, axon serving
  - `protocol.py`: Synapse protocol handlers

### **`config/`** - Configuration
- **Purpose**: Application settings
- **Key Files**:
  - `settings.py`: Pydantic-based settings management

### **`tests/`** - Testing
- **Purpose**: Test suites for compliance and functionality
- **Key Files**:
  - `test_official.py`: Official compliance tests
  - `test_ultimate.py`: Ultimate compliance test suite
  - `test_api.py`: API functionality tests

### **`scripts/`** - Utility Scripts
- **Purpose**: Deployment, monitoring, and utility scripts
- **Organization**:
  - `deploy/`: Deployment scripts
  - `monitor/`: Monitoring scripts
  - `test/`: Testing scripts
  - `utils/`: Utility scripts (checks, verification, etc.)

### **`docs/`** - Documentation
- **Purpose**: All project documentation
- **Organization**:
  - `deployment/`: Deployment guides
  - `ratings/`: Rating and compliance docs
  - `chutes/`: Chutes-related documentation
  - `validator/`: Validator discovery docs
  - `playground/`: Playground testing guides
  - `status/`: Status updates
  - `archive/`: Archived documentation

---

## 🎯 **Entry Points**

### **API Server**
```bash
python -m api.server
# or
uvicorn api.server:app --host 0.0.0.0 --port 8080
```

### **Miner**
```bash
python -m miner.miner
```

---

## 📝 **File Naming Conventions**

### **Python Files**
- `snake_case.py` for all Python files
- `__init__.py` in all package directories

### **Scripts**
- `snake_case.sh` for shell scripts
- Organized by function (deploy, monitor, test, utils)

### **Documentation**
- `UPPER_CASE.md` for important docs
- `snake_case.md` for specific topics
- Organized in subdirectories by topic

---

## 🧹 **Cleanup Rules**

### **What's Ignored** (`.gitignore`)
- `__pycache__/` - Python cache
- `venv/` - Virtual environment
- `.env` - Environment variables (sensitive)
- `*.log` - Log files
- `*.pyc` - Compiled Python files

### **What's Organized**
- All `.md` files → `docs/` (except `README.md` in root)
- All `test_*.py` → `tests/`
- All `*.sh` → `scripts/` (organized by function)
- Chutes docs → `docs/chutes/`
- Deployment docs → `docs/deployment/`
- Status docs → `docs/status/`

---

## ✅ **Organization Status**

- ✅ **Code**: Fully organized in `api/`, `miner/`, `config/`
- ✅ **Tests**: Organized in `tests/` with subdirectories
- ✅ **Scripts**: Organized by function in `scripts/`
- ✅ **Documentation**: Organized in `docs/` with subdirectories
- ✅ **Root**: Clean with only essential files

---

## 📚 **Documentation Index**

See `docs/README.md` for a complete documentation index.

---

**Status**: ✅ **PROFESSIONALLY ORGANIZED & MAINTAINABLE**
