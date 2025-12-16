#!/bin/bash
set -euo pipefail

# Bounded stress test (no server): concurrent /solve_task calls via TestClient.
# Tunables:
#   REQUESTS=300 CONCURRENCY=30 ./scripts/run_stress.sh

export ENABLE_BROWSER_AUTOMATION="${ENABLE_BROWSER_AUTOMATION:-false}"
export LEARNING_ENABLED="${LEARNING_ENABLED:-false}"
export REQUESTS="${REQUESTS:-300}"
export CONCURRENCY="${CONCURRENCY:-30}"

python3 - <<'PY'
import os, time, statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi.testclient import TestClient
from api.server import app
from api.utils.iwa_validator import validate_iwa_action_sequence

N = int(os.environ.get("REQUESTS", "300"))
CONC = int(os.environ.get("CONCURRENCY", "30"))

client = TestClient(app)

payloads = [
    {
        "id": f"stress-{i}",
        "prompt": "Navigate to https://example.com and take a screenshot",
        "url": "https://example.com",
    }
    for i in range(N)
]

latencies = []
errors = 0
err_kinds = {}

def one(p):
    t0 = time.time()
    r = client.post("/solve_task", json=p)
    dt = time.time() - t0
    if r.status_code != 200:
        return False, dt, f"http_{r.status_code}"
    d = r.json()
    if set(d.keys()) != {"actions", "web_agent_id", "recording"}:
        return False, dt, "bad_keys"
    if not d.get("actions"):
        return False, dt, "empty_actions"
    ok, _ = validate_iwa_action_sequence(d["actions"])
    if not ok:
        return False, dt, "iwa_invalid"
    return True, dt, None

start = time.time()
with ThreadPoolExecutor(max_workers=CONC) as ex:
    futs = [ex.submit(one, p) for p in payloads]
    for f in as_completed(futs):
        ok, dt, err = f.result()
        latencies.append(dt)
        if not ok:
            errors += 1
            err_kinds[err] = err_kinds.get(err, 0) + 1
end = time.time()

total = end - start
rps = N / total if total else 0.0
lat_sorted = sorted(latencies)
idx95 = max(0, int(0.95 * len(lat_sorted)) - 1)
idx99 = max(0, int(0.99 * len(lat_sorted)) - 1)

print(f"requests={N} concurrency={CONC} duration={total:.2f}s rps={rps:.1f} errors={errors}")
print(
    "latency_s "
    f"p50={statistics.median(latencies):.3f} "
    f"p95={lat_sorted[idx95]:.3f} "
    f"p99={lat_sorted[idx99]:.3f} "
    f"max={max(latencies):.3f}"
)
if errors:
    print("error_breakdown", err_kinds)
    raise SystemExit(1)

print("✅ Stress passed (0 errors)")
PY

