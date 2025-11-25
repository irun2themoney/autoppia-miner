# 📦 Code Review Package for Expert LLM Analysis

## Purpose
This package contains all core code files requested for flaw detection, focusing on **Performance** and **Protocol Compliance**.

---

## 1. IWA Protocol and Validation (Strict Compliance Check)

### File: `miner/protocol.py` - Synapse Definitions

```python
"""
Synapse protocol definitions for Autoppia Subnet 36
Based on official Autoppia patterns
"""
import bittensor as bt
from typing import List, Dict, Any, Optional


class StartRoundSynapse(bt.Synapse):
    """
    Synapse for starting a new round
    Used by validators to initiate task rounds
    
    Note: Bittensor may deserialize this as a generic Synapse.
    The miner handles this by checking for round_id and task_type attributes.
    """
    # Round information
    round_id: Optional[str] = None
    task_type: Optional[str] = None
    
    # Response fields
    success: bool = False
    message: Optional[str] = None
    
    def deserialize(self) -> "StartRoundSynapse":
        """Deserialize synapse data"""
        return self


class TaskSynapse(bt.Synapse):
    """
    Main task synapse for processing IWA tasks
    Matches ApifiedWebAgent pattern
    """
    # Task input (from task.clean_task())
    id: str = ""
    prompt: str = ""
    url: str = ""
    
    # Task response
    actions: List[Dict[str, Any]] = []
    web_agent_id: str = ""
    recording: str = ""
    task_id: str = ""
    success: bool = False
    task_type: str = "generic"
    
    def deserialize(self) -> "TaskSynapse":
        """Deserialize synapse data"""
        return self
```

### File: `api/utils/iwa_validator.py` - Core Validation Logic

```python
"""IWA Format Validator - Ensures actions comply with Autoppia IWA format"""
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Valid IWA action types
VALID_ACTION_TYPES = {
    "ClickAction",
    "TypeAction",
    "WaitAction",
    "NavigateAction",
    "ScreenshotAction",
    "ScrollAction"
}

# Valid selector types
VALID_SELECTOR_TYPES = {
    "tagContainsSelector",
    "attributeValueSelector",
    "cssSelector",
    "xpathSelector"
}


def validate_iwa_action(action: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate a single IWA action format
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(action, dict):
        return False, "Action must be a dictionary"
    
    # Check required 'type' field
    if "type" not in action:
        return False, "Action missing required 'type' field"
    
    action_type = action["type"]
    if action_type not in VALID_ACTION_TYPES:
        return False, f"Invalid action type '{action_type}'. Must be one of {VALID_ACTION_TYPES}"
    
    # Validate action-specific fields
    if action_type == "WaitAction":
        if "time_seconds" not in action:
            return False, "WaitAction missing required 'time_seconds' field"
        if not isinstance(action["time_seconds"], (int, float)):
            return False, "WaitAction 'time_seconds' must be a number"
    
    elif action_type == "TypeAction":
        if "text" not in action:
            return False, "TypeAction missing required 'text' field"
        if "selector" not in action:
            return False, "TypeAction missing required 'selector' field"
        selector_valid, selector_error = validate_selector(action["selector"])
        if not selector_valid:
            return False, f"TypeAction selector invalid: {selector_error}"
    
    elif action_type == "ClickAction":
        if "selector" not in action:
            return False, "ClickAction missing required 'selector' field"
        selector_valid, selector_error = validate_selector(action["selector"])
        if not selector_valid:
            return False, f"ClickAction selector invalid: {selector_error}"
    
    elif action_type == "NavigateAction":
        if "url" not in action:
            return False, "NavigateAction missing required 'url' field"
        if not isinstance(action["url"], str):
            return False, "NavigateAction 'url' must be a string"
    
    elif action_type == "ScrollAction":
        # Must have at least one direction
        directions = ["down", "up", "left", "right"]
        has_direction = any(action.get(d) for d in directions)
        if not has_direction:
            return False, "ScrollAction must have at least one direction (down, up, left, right)"
    
    # ScreenshotAction has no required fields
    
    return True, ""


def validate_selector(selector: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate IWA selector format
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(selector, dict):
        return False, "Selector must be a dictionary"
    
    if "type" not in selector:
        return False, "Selector missing required 'type' field"
    
    selector_type = selector["type"]
    if selector_type not in VALID_SELECTOR_TYPES:
        return False, f"Invalid selector type '{selector_type}'. Must be one of {VALID_SELECTOR_TYPES}"
    
    # Validate selector-specific fields
    if selector_type == "tagContainsSelector":
        if "value" not in selector:
            return False, "tagContainsSelector missing required 'value' field"
    
    elif selector_type == "attributeValueSelector":
        if "attribute" not in selector:
            return False, "attributeValueSelector missing required 'attribute' field"
        if "value" not in selector:
            return False, "attributeValueSelector missing required 'value' field"
    
    elif selector_type == "cssSelector":
        if "value" not in selector:
            return False, "cssSelector missing required 'value' field"
    
    elif selector_type == "xpathSelector":
        if "value" not in selector:
            return False, "xpathSelector missing required 'value' field"
    
    return True, ""


def validate_iwa_action_sequence(actions: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate a sequence of IWA actions
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(actions, list):
        return False, ["Actions must be a list"]
    
    if len(actions) == 0:
        return False, ["Actions list cannot be empty"]
    
    for i, action in enumerate(actions):
        is_valid, error = validate_iwa_action(action)
        if not is_valid:
            errors.append(f"Action {i}: {error}")
    
    return len(errors) == 0, errors
```

### Example Invalid Action (Correctly Flagged)

**Syntactically Correct but IWA-Invalid**:
```python
{
    "type": "ClickAction",
    # Missing required "selector" field - validator correctly flags this
}
```

**Validation Error**:
```
Action 0: ClickAction missing required 'selector' field
```

**Another Example**:
```python
{
    "type": "TypeAction",
    "text": "hello",
    "selector": {
        "type": "invalidSelectorType"  # Not in VALID_SELECTOR_TYPES
    }
}
```

**Validation Error**:
```
Action 0: TypeAction selector invalid: Invalid selector type 'invalidSelectorType'. Must be one of {'tagContainsSelector', 'attributeValueSelector', 'cssSelector', 'xpathSelector'}
```

---

## 2. Core Action Generation (Quality and Speed Check)

### File: `api/endpoints.py` - The Wrapper (solve_task endpoint)

**Key Section** (lines 161-388):
```python
@router.post("/solve_task")
async def solve_task(request: TaskRequest, http_request: Request):
    """
    Main endpoint - matches ApifiedWebAgent expectations
    Input: task.clean_task() format
    Output: {actions: [], web_agent_id: str, recording: str}
    """
    start_time = time.time()
    
    # ... (request validation, IP extraction, task parsing) ...
    
    try:
        # Call action generator
        actions = await asyncio.wait_for(
            agent.solve_task(
                task_id=request.id,
                prompt=request.prompt,
                url=request.url
            ),
            timeout=timeout_seconds  # 30s (fast_mode) or 90s
        )
        
        # CRITICAL: Ensure actions is never None or empty
        if not actions or len(actions) == 0:
            logger.warning(f"⚠️ Empty actions returned, generating fallback actions")
            actions = await _generate_fallback_actions(request.prompt, request.url or "", max_actions=20)
        
        # Validate IWA format before returning
        try:
            from api.utils.iwa_validator import validate_iwa_action_sequence
            is_valid, errors = validate_iwa_action_sequence(actions)
            if not is_valid:
                logger.error(f"❌ IWA Validation Failed for task {request.id}:")
                for error in errors[:5]:
                    logger.error(f"   - {error}")
                logger.warning(f"⚠️ Returning invalid IWA actions - validators may reject")
            else:
                logger.info(f"✅ IWA Validation Passed: {len(actions)} actions valid")
        except ImportError:
            logger.warning("⚠️ IWA validator not available - skipping validation")
        
        # Return response
        response_content = {
            "actions": actions,
            "web_agent_id": request.id,
            "recording": "",
        }
        
        return JSONResponse(
            content=response_content,
            status_code=200,
            headers=CORS_HEADERS
        )
    
    except asyncio.TimeoutError:
        # Generate fallback actions on timeout
        fallback_actions = await _generate_fallback_actions(request.prompt, request.url or "", max_actions=10)
        return JSONResponse(
            content={
                "actions": fallback_actions,
                "web_agent_id": request.id,
                "recording": "",
            },
            status_code=200,
            headers=CORS_HEADERS
        )
```

### File: `api/actions/generator.py` - The Heart

**Function Signature**:
```python
async def generate(self, prompt: str, url: str, task_id: str = None) -> List[Dict[str, Any]]:
    """Generate action sequence based on prompt"""
```

**Browser Instance Management** (Critical for < 1.5s target):

```python
# Browser instance is cached globally (singleton pattern)
# Initialized at server startup in api/server.py lifespan function

# Usage in generate():
if settings.enable_browser_automation and PLAYWRIGHT_AVAILABLE:
    try:
        browser_analyzer = await get_browser_analyzer()  # Uses cached browser
        if browser_analyzer:
            # Fetch page with full browser automation
            browser_timeout = getattr(settings, 'browser_fetch_timeout', 3.0)
            dom_timeout = getattr(settings, 'dom_analysis_timeout', 1.5)
            
            page_data = await browser_analyzer.fetch_page(url, timeout=browser_timeout)
            # ... use page_data for selector generation ...
    except Exception as e:
        logger.warning(f"Browser automation failed: {e}")
```

**Browser Caching Implementation** (`api/utils/browser_analyzer.py`):
```python
# Global browser instance (singleton)
_browser: Optional[Browser] = None
_playwright = None

async def _get_browser() -> Optional[Browser]:
    """Get or create browser instance (singleton pattern)"""
    global _browser, _playwright
    
    if _browser is None:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
    
    return _browser  # Returns cached instance
```

**Server Startup** (`api/server.py`):
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # EXPERT LLM FEEDBACK: Initialize browser at startup
    browser = await _get_browser()  # Pre-initialize (saves 2-4s per request)
    yield
    await close_browser()  # Cleanup
```

---

## 3. Log Output Examples

### Successful Response:
```
2025-11-25 01:10:23,456 - api.endpoints - INFO - 🚀 solve_task called: id=abc123, prompt_length=45
2025-11-25 01:10:23,457 - api.endpoints - INFO - 🔍 FULL REQUEST: id=abc123, prompt=Click the login button, url=https://example.com
2025-11-25 01:10:23,500 - api.actions.generator - INFO - 🔍 Attempting browser automation: enabled=True, playwright_available=True
2025-11-25 01:10:24,410 - api.endpoints - INFO - ✅ agent.solve_task returned: type=<class 'list'>, length=5 for task abc123
2025-11-25 01:10:24,411 - api.endpoints - INFO - ✅ IWA Validation Passed: 5 actions valid
2025-11-25 01:10:24,412 - api.endpoints - INFO - ✅ RETURNING RESPONSE: task_id=abc123, actions_count=5, first_action={'type': 'NavigateAction', 'url': 'https://example.com'}
2025-11-25 01:10:24,413 - miner.miner - INFO - 📤 TASK_RESPONSE: 192.168.1.1 - Completed TaskSynapse | Success: True | Actions: 5 | Time: 0.96s | IWA: ✅ VALID
```

### Slow Response Warning:
```
2025-11-25 01:15:30,123 - miner.miner - INFO - 📋 TASK_RECEIVED: 192.168.1.1 - Processing TaskSynapse | ID: xyz789 | URL: https://slow-site.com...
2025-11-25 01:15:34,567 - miner.miner - WARNING - ⚠️ SLOW_RESPONSE: 192.168.1.1 - Task xyz789 took 4.44s (validators may timeout if > 3s)
2025-11-25 01:15:34,568 - miner.miner - INFO - 📤 TASK_RESPONSE: 192.168.1.1 - Completed TaskSynapse | Success: True | Actions: 3 | Time: 4.44s | IWA: ✅ VALID
```

### Minimal Response Warning:
```
2025-11-25 01:20:10,234 - miner.miner - INFO - 📋 TASK_RECEIVED: 192.168.1.1 - Processing TaskSynapse | ID: def456
2025-11-25 01:20:11,123 - miner.miner - WARNING - ⚠️ MINIMAL_RESPONSE: 192.168.1.1 - Task def456 returned only ScreenshotAction (may receive low score from validators)
2025-11-25 01:20:11,124 - miner.miner - INFO - 📤 TASK_RESPONSE: 192.168.1.1 - Completed TaskSynapse | Success: True | Actions: 1 | Time: 0.89s | IWA: ✅ VALID
```

### IWA Validation Failed:
```
2025-11-25 01:25:15,789 - api.endpoints - ERROR - ❌ IWA Validation Failed for task ghi789:
2025-11-25 01:25:15,790 - api.endpoints - ERROR -    - Action 0: ClickAction missing required 'selector' field
2025-11-25 01:25:15,791 - api.endpoints - WARNING - ⚠️ Returning invalid IWA actions - validators may reject
2025-11-25 01:25:15,792 - miner.miner - INFO - 📤 TASK_RESPONSE: 192.168.1.1 - Completed TaskSynapse | Success: True | Actions: 2 | Time: 1.12s | IWA: ❌ INVALID (1 errors)
```

---

## 4. Selector Format Examples

### Valid Selector Formats (as we generate them):

**tagContainsSelector**:
```python
{
    "type": "tagContainsSelector",
    "value": "Login",
    "case_sensitive": False
}
```

**attributeValueSelector**:
```python
{
    "type": "attributeValueSelector",
    "attribute": "id",
    "value": "login-button",
    "case_sensitive": False
}
```

**cssSelector**:
```python
{
    "type": "cssSelector",
    "value": "#login-button"
}
```

**xpathSelector**:
```python
{
    "type": "xpathSelector",
    "value": "//button[@id='login-button']"
}
```

---

## 5. Action Converter Logic

**File**: `api/actions/converter.py`

**Key Conversion Logic**:
- Converts `action_type` → `type` (normalizes)
- Maps action types: `"click"` → `"ClickAction"`
- Converts selectors to IWA format
- Handles both old and new formats

**Potential Issue**: The converter may be creating selectors with different casing than expected by validators.

---

## 🔍 Potential Flaw Hypotheses

### Hypothesis 1: Selector Casing/Key Mismatch
- **Issue**: We use `tagContainsSelector` (camelCase)
- **Validator might expect**: `tag_contains_selector` (snake_case) or different casing
- **Check**: Need to verify exact casing in official Autoppia validator code

### Hypothesis 2: Selector Structure Mismatch
- **Issue**: Our selectors have `case_sensitive` field (snake_case)
- **Validator might expect**: `caseSensitive` (camelCase) or different structure
- **Check**: Need to verify exact selector schema

### Hypothesis 3: Action Field Names
- **Issue**: We use `time_seconds` (snake_case) for WaitAction
- **Validator might expect**: `timeSeconds` (camelCase) or different field name
- **Check**: Need to verify exact action field names

### Hypothesis 4: Cold Start Performance
- **Issue**: First request after server restart may be slow (browser initialization)
- **Impact**: Validator's first check hits cold instance, times out
- **Mitigation**: Browser cached at startup (implemented), but first request still slower

---

## 📝 Questions for Expert Review

1. **Selector Casing**: Is `tagContainsSelector` correct, or should it be `tag_contains_selector`?
2. **Selector Fields**: Should `case_sensitive` be `caseSensitive` or different?
3. **Action Fields**: Is `time_seconds` correct, or should it be `timeSeconds`?
4. **Selector Structure**: Are we nesting selectors correctly?
5. **Performance**: Is 0.9s average fast enough, or do we need < 0.5s?

---

**Status**: Ready for expert review  
**Focus**: IWA format compliance and performance bottlenecks  
**Goal**: Identify exact flaw preventing validator acceptance

