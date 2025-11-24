# 🧪 Testing Guide - Validator Connection Verification

This guide shows you how to test your miner **before deploying** to ensure it will connect correctly and get graded by validators.

## Quick Start

Run the comprehensive test suite:

```bash
# Make sure API server is running first
python3 -m api.server &

# Run all tests
./scripts/test_validator_connection.sh
```

Or run tests individually:

```bash
# Test validator connection (API endpoint)
python3 tests/test_validator_connection.py

# Test miner startup
python3 tests/test_miner_startup.py
```

## What Gets Tested

### 1. **Synapse Structure Tests**
- ✅ StartRoundSynapse can be created and serialized
- ✅ TaskSynapse can be created and serialized
- ✅ All required fields are present

### 2. **API Endpoint Tests**
- ✅ API responds to validator requests
- ✅ Response format matches IWA requirements
- ✅ Actions array is never empty
- ✅ Actions are in correct IWA format (NavigateAction, ClickAction, etc.)
- ✅ Error handling returns actions (never empty)

### 3. **Action Format Tests**
- ✅ All actions have `type` field ending with "Action"
- ✅ Selectors are in correct IWA format
- ✅ Valid action types: NavigateAction, ClickAction, TypeAction, WaitAction, ScreenshotAction, ScrollAction

### 4. **Task Type Tests**
- ✅ Login tasks handled
- ✅ Search tasks handled
- ✅ Form tasks handled
- ✅ Navigation tasks handled

### 5. **Miner Startup Tests**
- ✅ Miner can be initialized
- ✅ Registration check works
- ✅ Synapse detection works
- ✅ API connection configured

## Test Output

When tests pass, you'll see:

```
🧪 VALIDATOR CONNECTION TEST SUITE
============================================================

🧪 Testing StartRoundSynapse handling...
✅ StartRoundSynapse structure valid

🧪 Testing TaskSynapse handling...
✅ TaskSynapse structure valid

🧪 Testing API endpoint...
✅ API endpoint working correctly
   - Received 5 actions
   - Action types: ['NavigateAction', 'WaitAction', 'ClickAction']

📊 TEST SUMMARY
============================================================
  ✅ PASS start_round_synapse
  ✅ PASS task_synapse
  ✅ PASS api_endpoint
  ✅ PASS api_error_handling
  ✅ PASS iwa_format
  ✅ PASS multiple_task_types

Results: 6/6 tests passed

🎉 All tests passed! Miner is ready for validators.
```

## Manual Testing

### Test API Endpoint Directly

```bash
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-validator-001",
    "prompt": "Navigate to homepage and click login button",
    "url": "https://autobooks.autoppia.com"
  }'
```

**Expected Response:**
```json
{
  "actions": [
    {"type": "NavigateAction", "url": "https://autobooks.autoppia.com"},
    {"type": "WaitAction", "time_seconds": 1.0},
    {"type": "ClickAction", "selector": {...}},
    ...
  ],
  "web_agent_id": "test-validator-001",
  "recording": ""
}
```

### Test with Different Task Types

```bash
# Login task
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id": "test", "prompt": "Login to the website", "url": "https://autobooks.autoppia.com"}'

# Search task
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id": "test", "prompt": "Search for books", "url": "https://autobooks.autoppia.com"}'

# Form task
curl -X POST http://localhost:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id": "test", "prompt": "Fill out registration form", "url": "https://autobooks.autoppia.com"}'
```

## What Validators Check

Validators will verify:

1. **Response Format**: Must match `{actions: [], web_agent_id: str, recording: str}`
2. **Actions Never Empty**: Must have at least one action
3. **IWA Format**: Actions must be in BaseAction format
4. **Action Types**: Must be valid IWA action types
5. **Selector Format**: Selectors must be in IWA Selector format
6. **Response Time**: Should respond within 90 seconds
7. **Error Handling**: Should return actions even on errors

## Troubleshooting

### API Not Running
```bash
# Start API server
python3 -m api.server

# Or in background
python3 -m api.server > api.log 2>&1 &
```

### Tests Fail
1. Check API is running: `curl http://localhost:8080/solve_task`
2. Check logs: `tail -f api.log`
3. Verify dependencies: `pip install -r requirements.txt`
4. Check port 8080 is available: `lsof -i :8080`

### Miner Not Registered
If registration test fails, register your miner:
```bash
btcli subnet register --netuid 36 --wallet.name YOUR_WALLET --wallet.hotkey YOUR_HOTKEY
```

## Pre-Deployment Checklist

Before deploying to production, verify:

- [ ] All tests pass: `./scripts/test_validator_connection.sh`
- [ ] API responds correctly to test requests
- [ ] Actions are never empty
- [ ] IWA format is correct
- [ ] Miner can start without errors
- [ ] Registration check works (if registered)

## Continuous Testing

Add to your CI/CD pipeline:

```bash
# In your deployment script
./scripts/test_validator_connection.sh || exit 1
```

This ensures you never deploy broken code!

