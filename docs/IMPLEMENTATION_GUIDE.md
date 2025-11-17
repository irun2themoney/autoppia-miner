# 🏗️ Complete Implementation Guide - Building from Ground Up

## Executive Summary

Based on official Autoppia documentation and top miner analysis, this guide provides a step-by-step approach to building a competitive miner following best practices.

## Key Insights from Research

### Official Pattern: ApifiedWebAgent
- **Architecture**: HTTP API server that validators call
- **Endpoint**: `POST /solve_task` 
- **Input**: `{id, prompt, url}` (from `task.clean_task()`)
- **Output**: `{actions: [], web_agent_id: str, recording: str}`
- **Format**: IWA BaseAction objects

### Top Miner Strategies
1. **Browser-Use Agent**: Advanced web interaction (recommended for top performance)
2. **External LLM**: OpenAI API (better than local for reliability)
3. **PM2 Management**: Process management for reliability
4. **Fast Response**: < 1 second response times
5. **Robust Selectors**: Multiple fallback strategies

### Current Implementation Status
- ✅ ApifiedWebAgent pattern (correct)
- ✅ IWA BaseAction format (correct)
- ✅ Fast response times (good)
- ⚠️ Template-based (could use browser-use)
- ⚠️ Code organization (could be modular)
- ⚠️ Testing (needs improvement)

## Phase 1: Project Restructure

### Step 1.1: Create Modular Structure

```
autoppia-miner/
├── api/
│   ├── __init__.py
│   ├── server.py          # FastAPI app
│   ├── endpoints.py       # Route handlers
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── base.py        # Base agent interface
│   │   ├── template.py    # Template-based agent (current)
│   │   └── browser_use.py # Browser-use agent (future)
│   ├── actions/
│   │   ├── __init__.py
│   │   ├── generator.py   # Action generation
│   │   ├── converter.py   # IWA format conversion
│   │   └── selectors.py   # Selector strategies
│   └── utils/
│       ├── __init__.py
│       ├── classification.py
│       └── keywords.py
├── miner/
│   ├── __init__.py
│   ├── miner.py           # Main miner class
│   ├── synapse.py         # Synapse handling
│   └── config.py          # Miner config
├── config/
│   ├── __init__.py
│   ├── settings.py        # Settings management
│   └── env.example
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_actions.py
│   └── test_miner.py
├── scripts/
│   ├── setup.sh
│   ├── deploy.sh
│   └── monitor.sh
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

### Step 1.2: Update Requirements

```txt
# Core
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
bittensor>=7.0.0
python-dotenv>=1.0.0
httpx>=0.25.0
pydantic>=2.0.0

# Optional (for browser-use agent)
# browser-use>=0.1.0
# playwright>=1.40.0

# Development
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
mypy>=1.5.0
```

## Phase 2: API Server Implementation

### Step 2.1: Settings Management

**File**: `config/settings.py`

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    
    # Agent
    agent_type: str = "template"  # template or browser-use
    llm_provider: Optional[str] = None  # openai or None
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Step 2.2: Base Agent Interface

**File**: `api/agent/base.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAgent(ABC):
    """Base interface for web agents"""
    
    @abstractmethod
    async def solve_task(
        self, 
        task_id: str, 
        prompt: str, 
        url: str
    ) -> List[Dict[str, Any]]:
        """
        Solve a task and return IWA BaseAction format actions
        
        Args:
            task_id: Unique task identifier
            prompt: Task description
            url: Target URL
            
        Returns:
            List of IWA BaseAction objects
        """
        pass
```

### Step 2.3: Template Agent (Current Implementation)

**File**: `api/agent/template.py`

```python
from .base import BaseAgent
from ..actions.generator import ActionGenerator
from ..actions.converter import convert_to_iwa_action
from typing import Dict, Any, List

class TemplateAgent(BaseAgent):
    """Template-based agent (current implementation)"""
    
    def __init__(self):
        self.action_generator = ActionGenerator()
    
    async def solve_task(
        self, 
        task_id: str, 
        prompt: str, 
        url: str
    ) -> List[Dict[str, Any]]:
        # Generate actions using templates
        raw_actions = self.action_generator.generate(prompt, url)
        
        # Convert to IWA format
        iwa_actions = [
            convert_to_iwa_action(action) 
            for action in raw_actions
        ]
        
        # Ensure non-empty
        if not iwa_actions:
            iwa_actions = [{"type": "ScreenshotAction"}]
        
        return iwa_actions
```

### Step 2.4: Action Generator

**File**: `api/actions/generator.py`

```python
from typing import Dict, Any, List
from .selectors import SelectorStrategy
from ..utils.classification import TaskClassifier
from ..utils.keywords import extract_keywords

class ActionGenerator:
    """Generate action sequences based on task"""
    
    def __init__(self):
        self.classifier = TaskClassifier()
        self.selector_strategy = SelectorStrategy()
    
    def generate(self, prompt: str, url: str) -> List[Dict[str, Any]]:
        """Generate action sequence"""
        actions = []
        
        # Navigate if URL provided
        if url:
            actions.append({
                "action_type": "navigate",
                "url": url
            })
            actions.append({
                "action_type": "wait",
                "duration": 1.2
            })
        
        # Initial screenshot
        actions.append({"action_type": "screenshot"})
        
        # Classify task
        task_type = self.classifier.classify(prompt)
        
        # Generate task-specific actions
        if task_type == "click":
            actions.extend(self._generate_click_actions(prompt))
        elif task_type == "type":
            actions.extend(self._generate_type_actions(prompt))
        elif task_type == "search":
            actions.extend(self._generate_search_actions(prompt))
        else:
            actions.append({"action_type": "wait", "duration": 0.5})
            actions.append({"action_type": "screenshot"})
        
        return actions
    
    def _generate_click_actions(self, prompt: str) -> List[Dict[str, Any]]:
        """Generate click action sequence"""
        actions = []
        
        # Wait for elements
        actions.append({"action_type": "wait", "duration": 1.0})
        
        # Get selector strategies
        strategies = self.selector_strategy.get_strategies(prompt)
        
        # Try primary selector
        actions.append({
            "action_type": "click",
            "selector": strategies[0]
        })
        actions.append({"action_type": "wait", "duration": 0.3})
        
        # Add fallbacks (try 2-3 most likely)
        for selector in strategies[1:3]:
            actions.append({
                "action_type": "click",
                "selector": selector
            })
            actions.append({"action_type": "wait", "duration": 0.3})
        
        # Final wait and screenshot
        actions.append({"action_type": "wait", "duration": 2.5})
        actions.append({"action_type": "screenshot"})
        
        return actions
    
    def _generate_type_actions(self, prompt: str) -> List[Dict[str, Any]]:
        """Generate type action sequence"""
        # Implementation similar to current
        pass
    
    def _generate_search_actions(self, prompt: str) -> List[Dict[str, Any]]:
        """Generate search action sequence"""
        # Implementation similar to current
        pass
```

### Step 2.5: API Server

**File**: `api/server.py`

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .endpoints import router
from config.settings import settings

app = FastAPI(
    title="IWA Miner API",
    version="1.0.0",
    description="Infinite Web Arena Miner API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Routes
app.include_router(router)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agent_type": settings.agent_type
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port
    )
```

### Step 2.6: Endpoints

**File**: `api/endpoints.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from .agent.template import TemplateAgent
from config.settings import settings

router = APIRouter()
agent = TemplateAgent()

class TaskRequest(BaseModel):
    id: str
    prompt: str
    url: str

class TaskResponse(BaseModel):
    actions: List[Dict[str, Any]]
    web_agent_id: str
    recording: str
    id: str
    task_id: str

@router.options("/solve_task")
async def solve_task_options():
    """CORS preflight"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "600",
        }
    )

@router.post("/solve_task")
async def solve_task(request: TaskRequest) -> TaskResponse:
    """Main endpoint - matches ApifiedWebAgent pattern"""
    try:
        # Solve task using agent
        actions = await agent.solve_task(
            task_id=request.id,
            prompt=request.prompt,
            url=request.url
        )
        
        return TaskResponse(
            actions=actions,
            web_agent_id=request.id,
            recording="",
            id=request.id,
            task_id=request.id
        )
    
    except Exception as e:
        # Return empty actions on error
        return TaskResponse(
            actions=[],
            web_agent_id=request.id,
            recording="",
            id=request.id,
            task_id=request.id
        )
```

## Phase 3: Miner Implementation

### Step 3.1: Miner Class

**File**: `miner/miner.py`

```python
import asyncio
import httpx
from typing import Optional
import bittensor as bt
from config.settings import settings

class AutoppiaMiner:
    def __init__(self, config: Optional[bt.config] = None):
        self.config = config or self._load_config()
        self.wallet = bt.wallet(
            name=self.config.wallet.name,
            hotkey=self.config.wallet.hotkey
        )
        self.subtensor = bt.subtensor(network=self.config.network)
        self.metagraph = self.subtensor.metagraph(36)
        self.axon = None
        self.api_client = httpx.AsyncClient(
            base_url=f"http://localhost:{settings.api_port}",
            timeout=30.0
        )
    
    async def process_task(self, synapse: bt.Synapse) -> bt.Synapse:
        """Process validator request"""
        try:
            # Extract task data
            task_id = getattr(synapse, "id", None) or \
                     getattr(synapse, "task_id", None) or "unknown"
            prompt = getattr(synapse, "prompt", "")
            url = getattr(synapse, "url", "")
            
            # Call API
            response = await asyncio.wait_for(
                self.api_client.post(
                    "/solve_task",
                    json={
                        "id": task_id,
                        "prompt": prompt,
                        "url": url
                    }
                ),
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                synapse.actions = result.get("actions", [])
                synapse.success = True
            else:
                synapse.actions = []
                synapse.success = False
        
        except Exception as e:
            synapse.actions = []
            synapse.success = False
        
        return synapse
    
    async def run(self):
        """Start miner"""
        # Check registration
        if self.wallet.hotkey.ss58_address not in self.metagraph.hotkeys:
            print("❌ Miner not registered!")
            return
        
        # Create and start axon
        self.axon = bt.axon(
            wallet=self.wallet,
            port=self.config.axon.port
        )
        self.axon.attach(forward_fn=self.process_task)
        self.axon.start()
        
        print(f"✅ Miner started on port {self.config.axon.port}")
        
        # Serve forever
        await asyncio.Event().wait()
```

## Phase 4: Testing

### Step 4.1: Unit Tests

**File**: `tests/test_actions.py`

```python
import pytest
from api.actions.generator import ActionGenerator

def test_click_action_generation():
    generator = ActionGenerator()
    actions = generator.generate(
        prompt="Switch to month view",
        url="https://example.com"
    )
    
    assert len(actions) > 0
    assert any(a.get("action_type") == "click" for a in actions)
```

### Step 4.2: Integration Tests

**File**: `tests/test_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from api.server import app

client = TestClient(app)

def test_solve_task():
    response = client.post(
        "/solve_task",
        json={
            "id": "test-123",
            "prompt": "Click button",
            "url": "https://example.com"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "actions" in data
    assert len(data["actions"]) > 0
```

## Phase 5: Deployment

### Step 5.1: Systemd Services

**File**: `scripts/deploy.sh`

```bash
#!/bin/bash
# Deploy API and Miner services

# API Service
cat > /etc/systemd/system/autoppia-api.service << EOF
[Unit]
Description=Autoppia API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/autoppia-miner
Environment="PATH=/opt/autoppia-miner/venv/bin"
ExecStart=/opt/autoppia-miner/venv/bin/python3 -m api.server
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Miner Service
cat > /etc/systemd/system/autoppia-miner.service << EOF
[Unit]
Description=Autoppia Miner
After=network.target autoppia-api.service
Requires=autoppia-api.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/autoppia-miner
Environment="PATH=/opt/autoppia-miner/venv/bin"
ExecStart=/opt/autoppia-miner/venv/bin/python3 -m miner.miner
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable autoppia-api autoppia-miner
systemctl start autoppia-api autoppia-miner
```

## Implementation Checklist

### Phase 1: Foundation
- [ ] Create modular directory structure
- [ ] Set up configuration management
- [ ] Update requirements.txt
- [ ] Create base agent interface

### Phase 2: API Server
- [ ] Implement settings management
- [ ] Create FastAPI server
- [ ] Implement template agent
- [ ] Create action generator
- [ ] Implement selector strategies
- [ ] Add IWA format conversion
- [ ] Add error handling
- [ ] Add CORS support

### Phase 3: Miner
- [ ] Implement miner class
- [ ] Add synapse processing
- [ ] Add API integration
- [ ] Add error handling
- [ ] Add logging

### Phase 4: Testing
- [ ] Unit tests for actions
- [ ] Unit tests for selectors
- [ ] Integration tests for API
- [ ] Integration tests for miner
- [ ] Playground testing

### Phase 5: Deployment
- [ ] Create deployment scripts
- [ ] Set up systemd services
- [ ] Configure monitoring
- [ ] Set up HTTPS tunnel
- [ ] Test deployment

## Next Steps

1. **Review this guide** - Confirm approach
2. **Start Phase 1** - Restructure project
3. **Implement Phase 2** - Build API server
4. **Implement Phase 3** - Build miner
5. **Test & Deploy** - Validate and deploy

## References

- Official Docs: https://luxit.gitbook.io/autoppia-docs
- GitHub: https://github.com/autoppia/autoppia_web_agents_subnet
- IWA Module: https://github.com/autoppia/autoppia_iwa

