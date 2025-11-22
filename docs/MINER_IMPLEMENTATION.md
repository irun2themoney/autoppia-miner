# 🏗️ Miner Implementation Guide

**Based on Official Autoppia Template**  
**Source**: https://github.com/autoppia/autoppia_web_agents_subnet

---

## 📋 Core Requirements

### **1. ApifiedWebAgent Pattern**

Your miner must expose an HTTP API that validators call (not direct Bittensor synapse processing).

**Architecture**:
```
Validator → HTTP API → Your Agent → Actions → Validator
```

**Not**:
```
Validator → Bittensor Synapse → Your Agent (direct)
```

---

### **2. API Endpoint**

**Endpoint**: `POST /solve_task`

**Request Format**:
```json
{
  "id": "string",
  "prompt": "string",
  "url": "string"
}
```

**Response Format**:
```json
{
  "actions": [...],
  "web_agent_id": "string",
  "recording": ""
}
```

**Critical**: 
- Always return `actions` array (never empty)
- Use IWA BaseAction format
- Return 200 OK even on errors (with fallback actions)

---

### **3. IWA BaseAction Format**

**Action Types**:
- `NavigateAction` - Navigate to URL
- `ClickAction` - Click element
- `TypeAction` - Type text
- `WaitAction` - Wait for time
- `ScreenshotAction` - Take screenshot
- `ScrollAction` - Scroll page

**Selector Types**:
- `tagContainsSelector` - Match by tag and text
- `attributeValueSelector` - Match by attribute
- `xpathSelector` - XPath expression
- `cssSelector` - CSS selector

**Example**:
```json
{
  "type": "ClickAction",
  "selector": {
    "type": "cssSelector",
    "value": "button.submit"
  }
}
```

---

### **4. Bittensor Miner**

**Requirements**:
- Subnet 36 (netuid=36)
- Axon serving to network
- Metagraph syncing
- Forward Bittensor synapses to HTTP API

**Official Pattern** (from `neurons/miner.py`):
```python
# Miner receives TaskSynapse
# Calls ApifiedWebAgent.solve_task()
# Returns actions in synapse
```

---

## 🎯 Implementation Checklist

### **API Server**
- [x] FastAPI server with `/solve_task` endpoint
- [x] CORS enabled for all origins
- [x] Returns IWA BaseAction format
- [x] Always returns non-empty actions
- [x] Handles errors gracefully

### **Agent**
- [x] TemplateAgent (simple, fast)
- [x] ActionGenerator (creates actions)
- [x] Task classification
- [x] Selector strategies

### **Miner**
- [x] Bittensor integration
- [x] Subnet 36 registration
- [x] Axon serving
- [x] Forwards to HTTP API

---

## 🚀 Quick Start

1. **Start API Server**:
   ```bash
   python3 -m api.server
   ```

2. **Start Miner**:
   ```bash
   python3 -m miner.miner --wallet.name default --wallet.hotkey default
   ```

3. **Test Endpoint**:
   ```bash
   curl -X POST http://localhost:8080/solve_task \
     -H "Content-Type: application/json" \
     -d '{"id":"test","prompt":"click button","url":"https://example.com"}'
   ```

---

## 📚 References

- [Official GitHub](https://github.com/autoppia/autoppia_web_agents_subnet)
- [IWA Platform](https://infinitewebarena.autoppia.com/subnet36/overview)
- [Dynamic Zero](https://autoppia.substack.com/p/dynamic-zero-the-overfitting-punisher)

