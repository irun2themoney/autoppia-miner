# 🤖 Agent Endpoint for IWA Playground

## Endpoint Information

### Server Details
- **IP Address**: `134.199.203.133`
- **API Port**: `8080`
- **Axon Port**: `8091` (Bittensor synapse queries only)

### Agent Endpoint
```
http://134.199.203.133:8080/solve_task
```

---

## Request Format

### HTTP Method
```
POST
```

### Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "id": "test-task-123",
  "url": "https://example.com",
  "prompt": "Click the link"
}
```

### Response Format
```json
{
  "actions": [
    {
      "type": "NavigateAction",
      "url": "https://example.com"
    },
    {
      "type": "WaitAction",
      "timeSeconds": 1.0
    },
    {
      "type": "ClickAction",
      "selector": {
        "type": "tagContainsSelector",
        "value": "link",
        "caseSensitive": false
      }
    }
  ],
  "web_agent_id": "test-task-123",
  "recording": ""
}
```

---

## Testing with cURL

```bash
curl -X POST http://134.199.203.133:8080/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-1",
    "url": "https://example.com",
    "prompt": "Click the link"
  }'
```

---

## Testing with Python

```python
import requests

url = "http://134.199.203.133:8080/solve_task"
payload = {
    "id": "test-1",
    "url": "https://example.com",
    "prompt": "Click the link"
}

response = requests.post(url, json=payload)
print(response.json())
```

---

## Health Check

```bash
curl http://134.199.203.133:8080/health
```

---

## Status

✅ **API Server**: Active on port 8080  
✅ **Miner Axon**: Active on port 8091  
✅ **Endpoint**: `/solve_task` ready for playground testing

---

**Last Updated**: Current  
**Status**: Ready for playground testing

