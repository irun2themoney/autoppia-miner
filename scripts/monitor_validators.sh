#!/bin/bash
# Monitor for validator requests in real-time

echo "🔍 Monitoring for validator requests on UID 160..."
echo "Press Ctrl+C to stop"
echo ""
echo "Watching for:"
echo "  - Incoming synapses"
echo "  - Task processing"
echo "  - Validator activity"
echo ""
echo "----------------------------------------"

ssh root@134.199.203.133 'journalctl -u autoppia-miner -f | grep --line-buffered -iE "synapse|processing|task|validator|request|forward"'
