#!/usr/bin/env python3
import json
import sys

data = json.load(sys.stdin)

print("=== VALIDATOR METRICS (Localhost Excluded) ===")
print(f"Total Validator Requests: {data['overview']['total_requests']}")
print(f"Success Rate: {data['overview']['success_rate']}%")
print(f"Unique Validators: {data['validators']['unique_validators']}")

print("\nTop Validators:")
for v in data['validators']['top_validators'][:5]:
    print(f"  {v['ip']}: {v['requests']} requests")

print("\nRecent Activity (Last 5):")
for a in data['validators']['recent_activity'][:5]:
    status = "SUCCESS" if a['success'] else "FAIL"
    print(f"  {a['time'][:19]} - {a['ip']} - {status}")

