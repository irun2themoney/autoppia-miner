# 🔍 Empty Actions Investigation System

## Problem Statement

**Issue**: Playground reports `"actions": []` despite API returning 17+ actions  
**Impact**: Validators cannot execute empty actions → zero score  
**Status**: Miner is technically compliant, but empty actions issue needs investigation

---

## 🔧 Diagnostic System Implemented

### 1. **Empty Actions Diagnostic Module** (`api/utils/empty_actions_diagnostic.py`)

**Features:**
- **Checkpoint Tracking**: Records actions at every stage of processing
- **Response Validation**: Validates response before sending
- **Flow Tracing**: Tracks action flow through multiple stages
- **Event Logging**: Records all empty actions events with context

**Checkpoints Tracked:**
1. `before_agent_call` - Before calling agent.solve_task
2. `after_agent_returned` - After agent returns actions
3. `before_fallback` - Before generating fallback actions
4. `after_fallback` - After fallback actions generated
5. `after_cleanup` - After action cleanup/conversion
6. `before_jsonresponse` - Right before creating JSONResponse

### 2. **Response Validation**

**Validates:**
- ✅ Actions field exists
- ✅ Actions is a list (not None or other type)
- ✅ Actions array is not empty
- ✅ JSON serialization works correctly
- ✅ Serialized JSON doesn't contain empty actions

**If validation fails:**
- Logs critical error with full context
- Forces actions into response
- Regenerates JSONResponse with guaranteed actions

### 3. **JSONResponse Body Verification**

**After JSONResponse creation:**
- Decodes response body
- Parses JSON
- Verifies actions are present
- Regenerates response if empty

---

## 📊 Diagnostic Endpoint

### Get Diagnostic Report

```bash
GET /diagnostic/empty-actions?task_id=optional-task-id
```

**Response:**
```json
{
  "total_checkpoints": 50,
  "empty_actions_events": 2,
  "stage_analysis": {
    "before_jsonresponse": {
      "count": 1,
      "tasks": ["task-123"]
    }
  },
  "recent_empty_events": [...],
  "recent_checkpoints": [...]
}
```

---

## 🔍 Investigation Strategy

### Step 1: Monitor Checkpoints

When a task runs, checkpoints are recorded at each stage:

```python
# Example checkpoint data
{
  "timestamp": "2025-11-25T18:00:00",
  "stage": "after_agent_returned",
  "task_id": "task-123",
  "actions_count": 17,
  "actions_empty": false,
  "context": {"agent_type": "TemplateAgent"}
}
```

### Step 2: Identify Where Actions Become Empty

**If actions are empty at:**
- `after_agent_returned` → Agent is returning empty (check agent code)
- `after_fallback` → Fallback generation failed (check fallback logic)
- `after_cleanup` → Cleanup/conversion corrupted actions (check converter)
- `before_jsonresponse` → Actions lost during processing (check intermediate steps)
- `after_jsonresponse` → JSONResponse corrupted actions (check FastAPI)

### Step 3: Analyze Empty Events

Each empty event includes:
- Stage where it occurred
- Task ID
- Full actions array (should be empty)
- Context (prompt, URL, etc.)

### Step 4: Check Response Validation

Response validation logs will show:
- What validation failed
- Why it failed
- What was forced into response

---

## 🚨 Critical Safeguards Added

### 1. **Multiple Validation Layers**

```python
# Layer 1: After agent returns
if not actions or len(actions) == 0:
    actions = await _generate_fallback_actions(...)

# Layer 2: After cleanup
if not actions or len(actions) == 0:
    actions = [{"type": "ScreenshotAction"}]

# Layer 3: Before JSONResponse
if not response_content["actions"] or len(response_content["actions"]) == 0:
    response_content["actions"] = [guaranteed_actions]

# Layer 4: After JSONResponse creation
if parsed_body["actions"] is empty:
    regenerate response with forced actions
```

### 2. **Response Body Verification**

After creating JSONResponse, we:
- Decode the body
- Parse JSON
- Verify actions are present
- Regenerate if empty

### 3. **Diagnostic Checkpoints**

Every stage logs:
- Action count
- Whether actions are empty
- Context information

---

## 📝 How to Use

### 1. **Monitor During Playground Test**

```bash
# Watch logs in real-time
ssh root@134.199.203.133 "journalctl -u autoppia-api -f | grep -E 'DIAGNOSTIC|EMPTY|checkpoint'"
```

### 2. **Check Diagnostic Report**

```bash
# Get diagnostic report
curl http://134.199.203.133:8080/diagnostic/empty-actions

# Get report for specific task
curl http://134.199.203.133:8080/diagnostic/empty-actions?task_id=4318e05c-000d-4cef-8064-dbc5a81c5cb7
```

### 3. **Analyze Empty Events**

The diagnostic report shows:
- Which stage had empty actions
- How many times it happened
- Which tasks were affected
- Full context for each event

---

## 🎯 Expected Outcomes

### If Actions Are Empty at Agent Stage:
- **Check**: `api/agent/template.py` - agent.solve_task
- **Fix**: Ensure agent always returns non-empty actions

### If Actions Are Empty at Fallback Stage:
- **Check**: `api/endpoints.py` - `_generate_fallback_actions`
- **Fix**: Ensure fallback always generates actions

### If Actions Are Empty After Cleanup:
- **Check**: `api/endpoints.py` - cleanup/conversion logic
- **Fix**: Ensure cleanup doesn't remove all actions

### If Actions Are Empty in JSONResponse:
- **Check**: FastAPI JSONResponse serialization
- **Fix**: Verify response body after creation

---

## 🔬 Next Steps

1. **Run Playground Test** - Execute a test on the playground
2. **Check Diagnostic Report** - View `/diagnostic/empty-actions` endpoint
3. **Analyze Empty Events** - Identify which stage has empty actions
4. **Review Logs** - Check server logs for diagnostic checkpoints
5. **Fix Root Cause** - Address the specific stage where actions become empty

---

## 📊 Monitoring Commands

```bash
# Real-time diagnostic monitoring
ssh root@134.199.203.133 "journalctl -u autoppia-api -f | grep -E 'checkpoint|EMPTY|validation'"

# Get diagnostic report
curl http://134.199.203.133:8080/diagnostic/empty-actions | jq

# Test API directly
curl -X POST http://134.199.203.133:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id": "test-diagnostic", "url": "https://example.com", "prompt": "test"}' \
  | jq '.actions | length'
```

---

**Status**: ✅ **Diagnostic System Active**

The diagnostic system will now track every stage where actions could become empty, allowing us to pinpoint the exact cause of the empty actions issue.

