#!/bin/bash
set -euo pipefail

# In-process E2E (no server): validates response shape + IWA action validity.
# Uses FastAPI TestClient so it’s deterministic and fast.

export ENABLE_BROWSER_AUTOMATION="${ENABLE_BROWSER_AUTOMATION:-false}"
export LEARNING_ENABLED="${LEARNING_ENABLED:-false}"

python3 - <<'PY'
import os, json

from fastapi.testclient import TestClient

from api.server import app
from api.utils.iwa_validator import validate_iwa_action_sequence

client = TestClient(app)

print("== E2E: /health ==")
r = client.get("/health")
print("status", r.status_code)
print("body", r.json())
assert r.status_code == 200
assert r.json().get("status") == "healthy"

print("\n== E2E: /solve_task ==")
payload = {
    "id": "e2e-1",
    "prompt": "Navigate to https://example.com and take a screenshot",
    "url": "https://example.com",
}
resp = client.post("/solve_task", json=payload)
print("status", resp.status_code)
assert resp.status_code == 200

data = resp.json()
print("keys", sorted(list(data.keys())))
assert set(data.keys()) == {"actions", "web_agent_id", "recording"}, data.keys()
assert data["web_agent_id"] == "e2e-1"
assert isinstance(data["actions"], list) and len(data["actions"]) > 0
assert "webAgentId" not in data

ok, errs = validate_iwa_action_sequence(data["actions"])
print("iwa_valid", ok)
if not ok:
    print("iwa_errors", errs[:10])
assert ok, errs

actions_json = json.dumps(data["actions"])
assert "time_seconds" not in actions_json
assert "case_sensitive" not in actions_json

print("\n✅ E2E passed (shape + IWA validity)")
PY

