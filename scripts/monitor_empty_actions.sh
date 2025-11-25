#!/bin/bash
# Monitor Empty Actions Diagnostic System

SERVER_IP="134.199.203.133"
API_PORT="8080"

echo "🔍 Empty Actions Diagnostic Monitor"
echo "===================================="
echo ""

# Get diagnostic report
echo "📊 Diagnostic Report:"
curl -s "http://${SERVER_IP}:${API_PORT}/diagnostic/empty-actions" | python3 -m json.tool

echo ""
echo "📋 Recent Empty Events:"
curl -s "http://${SERVER_IP}:${API_PORT}/diagnostic/empty-actions" | python3 -c "
import sys, json
d = json.load(sys.stdin)
events = d.get('recent_empty_events', [])
if events:
    for event in events[-5:]:
        print(f\"  Stage: {event['stage']} | Task: {event['task_id']} | Time: {event['timestamp']}\")
else:
    print('  ✅ No empty events recorded')
"

echo ""
echo "📈 Stage Analysis:"
curl -s "http://${SERVER_IP}:${API_PORT}/diagnostic/empty-actions" | python3 -c "
import sys, json
d = json.load(sys.stdin)
stages = d.get('stage_analysis', {})
if stages:
    for stage, data in stages.items():
        print(f\"  {stage}: {data['count']} empty events\")
else:
    print('  ✅ No empty events in any stage')
"

echo ""
echo "💡 To monitor in real-time:"
echo "   ssh root@${SERVER_IP} 'journalctl -u autoppia-api -f | grep -E \"checkpoint|EMPTY|validation\"'"

