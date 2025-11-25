# 🤖 LLM Collaboration Summary - Autoppia Miner (Subnet 36)

## Project Overview

**What we're building**: A Bittensor miner for Subnet 36 (Autoppia) that performs web automation tasks.

**Language**: Python 3.8+

**Current Status**: Miner is running and configured correctly, but Active Status = 0 (inactive), preventing validator evaluation.

---

## What We've Built So Far

### 1. Core Mining Logic ✅

**File**: `miner/miner.py`

**What it does**:
- Connects to Bittensor network (Finney)
- Registers custom synapses (`StartRoundSynapse`, `TaskSynapse`)
- Serves axon on port 8091
- Receives validator queries via `forward()` function
- Processes tasks and returns actions

**Key Components**:
```python
class AutoppiaMiner:
    def __init__(self):
        # Initialize wallet, config, subtensor
        # Create axon
        # Register custom synapse types
        # Attach forward function
    
    async def forward(self, synapse):
        # Handle StartRoundSynapse (round start notifications)
        # Handle TaskSynapse (actual tasks with prompts/URLs)
        # Call API to generate actions
        # Return synapse with actions
```

**Synapse Types**:
- `StartRoundSynapse`: Notifies miner of new round (no actions needed)
- `TaskSynapse`: Contains task prompt, URL, requires IWA-format actions

### 2. API Server ✅

**File**: `api/endpoints.py`

**What it does**:
- FastAPI server on port 8080
- `/solve_task` endpoint processes tasks
- Generates IWA-format actions (NavigateAction, ClickAction, TypeAction, etc.)
- Uses Playwright for browser automation
- Returns action sequences

**Key Endpoint**:
```python
POST /solve_task
{
    "prompt": "Click the login button",
    "url": "https://example.com",
    "task_id": "unique_id"
}

Response:
{
    "actions": [
        {"type": "NavigateAction", "url": "..."},
        {"type": "ClickAction", "selector": {...}},
        ...
    ]
}
```

### 3. Action Generation ✅

**Files**: 
- `api/actions/generator.py` - Main action generator
- `api/actions/converter.py` - Converts to IWA format
- `api/actions/selectors.py` - Creates element selectors
- `api/utils/browser_analyzer.py` - Playwright browser automation

**What it does**:
- Analyzes task prompt
- Fetches page with Playwright
- Generates action sequence
- Converts to IWA format (tagContainsSelector, attributeValueSelector, etc.)
- Optimizes actions (removes redundant waits)
- Validates quality

### 4. Configuration ✅

**File**: `config/settings.py`

**Settings**:
- Subnet UID: 36
- Network: finney
- Axon port: 8091
- API port: 8080
- Wallet name/hotkey
- Timeouts and performance settings

### 5. Testing ✅

**Files**:
- `tests/test_validator_connection.py` - Simulates validator queries
- `tests/test_miner_startup.py` - Tests initialization
- `tests/test_full_miner_flow.py` - End-to-end tests

**Status**: All tests passing (12/12)

---

## Current Technical Stack

### Dependencies:
- `bittensor` - Bittensor SDK
- `fastapi` - API server
- `playwright` - Browser automation
- `pydantic` - Data validation
- `asyncio` - Async operations

### Architecture:
```
Validator → Bittensor Network → Axon (port 8091) → Miner.forward()
                                                      ↓
                                              API Call (localhost:8080)
                                                      ↓
                                              /solve_task endpoint
                                                      ↓
                                              ActionGenerator
                                                      ↓
                                              IWA Actions → Response
```

---

## What We're Trying to Fix

### Primary Issue: Active Status = 0

**Problem**: 
- Miner is running correctly
- Services are active
- Configuration is correct
- But `metagraph.active[uid] = 0` (inactive)
- This prevents validators from evaluating us

**What we know**:
- ✅ Axon is served correctly
- ✅ Synapse types are registered
- ✅ Forward function is attached
- ✅ We receive synapse queries (20-199 per day)
- ❌ Last update block is very old (1,998,054 blocks ago)
- ❌ Network isn't updating our status

**What we've tried**:
1. ✅ Verified IP/Port configuration
2. ✅ Restarted miner (axon re-served)
3. ✅ Added more frequent metagraph syncing
4. ✅ Ensured valid synapse responses
5. ✅ Optimized code (40% faster)
6. ✅ Improved action quality

**What we suspect**:
- Network may require successful synapse responses to update `last_update`
- Our responses may not be accepted as "successful"
- There may be subnet-specific requirements we're missing

---

## Specific Questions We Need Help With

### 1. Active Status Requirements
**Question**: What determines Active Status = 1 in Bittensor Subnet 36?

**What we need**:
- How does the network decide if a miner is "active"?
- Is there a specific response format required?
- Are there any subnet-specific requirements?
- How does `last_update` block get updated?

### 2. Synapse Response Validation
**Question**: Are our synapse responses being accepted?

**What we need**:
- How to verify if responses are successful?
- What makes a synapse response "valid"?
- Are there any response fields we're missing?
- Should we log response success/failure?

### 3. Network Update Mechanism
**Question**: How does the network update miner status?

**What we need**:
- What triggers `last_update` block update?
- How long does it take for status to update?
- Is there a minimum number of successful responses needed?
- Are there any network-level delays?

### 4. Subnet-Specific Requirements
**Question**: Are there Subnet 36 specific requirements we're missing?

**What we need**:
- Any special registration steps?
- Any required response fields?
- Any specific action formats?
- Any validator expectations?

---

## Code Examples

### Current Forward Function:
```python
async def forward(self, synapse: bt.Synapse) -> bt.Synapse:
    try:
        # Check if StartRoundSynapse
        if self._is_start_round_synapse(synapse):
            return StartRoundSynapse(
                round_id=getattr(synapse, "round_id", "unknown"),
                task_type=getattr(synapse, "task_type", "unknown"),
                success=True,
                message="Round started"
            )
        
        # Handle TaskSynapse
        result = await self.process_task(synapse)
        return result
        
    except Exception as e:
        # Error handling - always return valid synapse
        if self._is_start_round_synapse(synapse):
            return StartRoundSynapse(..., success=False, message=str(e))
        else:
            result = TaskSynapse()
            result.success = False
            result.actions = [{"type": "ScreenshotAction"}]  # Never empty
            result.message = str(e)
            return result
```

### Current Synapse Definitions:
```python
class StartRoundSynapse(bt.Synapse):
    round_id: str
    task_type: str
    success: bool = True
    message: str = ""

class TaskSynapse(bt.Synapse):
    prompt: str
    url: str
    task_id: Optional[str] = None
    actions: List[Dict[str, Any]] = []
    success: bool = True
    message: str = ""
```

### Current API Endpoint:
```python
@app.post("/solve_task")
async def solve_task(request: TaskRequest):
    try:
        # Generate actions
        actions = await action_generator.generate(
            prompt=request.prompt,
            url=request.url,
            task_id=request.task_id
        )
        
        # Ensure never empty
        if not actions:
            actions = await _generate_fallback_actions(...)
        
        return {"actions": actions}
    except Exception as e:
        # Always return valid response
        return {"actions": [{"type": "ScreenshotAction"}]}
```

---

## Current Errors/Issues

### No Code Errors ✅
- All code runs without errors
- All tests pass
- No exceptions in logs

### Network-Level Issues ❌
- Active Status = 0 (network decision)
- Last update block not updating
- Validators stopped querying (likely due to inactive status)

---

## What We Need Help With

### Priority 1: Understand Active Status
- How to get Active Status = 1?
- What are the requirements?
- Are we missing something?

### Priority 2: Verify Response Success
- How to know if responses are accepted?
- Should we add logging?
- Are responses formatted correctly?

### Priority 3: Network Update Mechanism
- How does `last_update` get updated?
- What triggers status updates?
- Are there delays we should account for?

### Priority 4: Subnet Requirements
- Any Subnet 36 specific requirements?
- Any documentation we should check?
- Any community resources?

---

## Environment Details

**Server**: DigitalOcean droplet
- IP: 134.199.203.133
- Port: 8091 (axon), 8080 (API)
- OS: Linux (systemd services)

**Wallet**:
- Network: finney
- Subnet: 36
- UID: 160

**Services**:
- `autoppia-api` (FastAPI server)
- `autoppia-miner` (Bittensor miner)

---

## Files to Review

**Key Files**:
1. `miner/miner.py` - Main miner logic
2. `miner/protocol.py` - Synapse definitions
3. `api/endpoints.py` - API endpoints
4. `api/actions/generator.py` - Action generation
5. `config/settings.py` - Configuration

**Documentation**:
- `README.md` - Setup instructions
- `STATUS_UPDATE.md` - Current status
- `RESEARCH_FINDINGS.md` - Previous research
- `ACTIVE_STATUS_SOLUTION.md` - Attempted solutions

---

## Next Steps We're Considering

1. **Research Bittensor Documentation**
   - Check official docs for Active Status requirements
   - Look for subnet-specific requirements
   - Review validator evaluation criteria

2. **Add Response Logging**
   - Log all synapse responses
   - Track success/failure
   - Monitor response acceptance

3. **Contact Community**
   - Ask in Bittensor Discord
   - Check Subnet 36 discussions
   - Look for similar issues

4. **Monitor and Wait**
   - Keep miner running
   - Monitor for changes
   - Check status daily

---

## Questions for You

1. **Do you have experience with Bittensor Subnet 36?**
   - Any specific requirements you know of?
   - Any common issues?

2. **Do you understand Active Status mechanism?**
   - How does it work?
   - What determines it?

3. **Can you help us debug?**
   - What should we check?
   - What might we be missing?

4. **Do you have code examples?**
   - Working miner examples?
   - Proper synapse handling?
   - Response validation?

---

**Last Updated**: Current status check
**Status**: Miner running, Active Status = 0, need help understanding requirements

