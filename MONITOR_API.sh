#!/bin/bash
# Monitor API logs for solve_task requests

echo "🔍 API Activity Monitor (solve_task requests)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
journalctl -u autoppia-api -f --no-pager | grep --line-buffered "solve_task"

