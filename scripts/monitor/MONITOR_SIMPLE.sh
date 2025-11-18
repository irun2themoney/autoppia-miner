#!/bin/bash
# Simple validator monitor - shows both logs side by side

echo "🔍 Validator Activity Monitor (Simple)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Miner Logs (validator activity):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
journalctl -u autoppia-miner -f --no-pager | grep --line-buffered -E "forward|synapse|process_task|validator|Forward|Synapse" -i

