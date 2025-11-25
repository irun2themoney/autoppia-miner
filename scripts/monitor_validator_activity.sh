#!/bin/bash
# Monitor validator activity

echo "=== 📊 Validator Activity Monitor ==="
echo ""

echo "Last Hour:"
REQUESTS=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no root@134.199.203.133 "journalctl -u autoppia-api --since '1 hour ago' | grep 'solve_task' | wc -l" 2>/dev/null)
echo "   API Requests: $REQUESTS"
echo ""

echo "Last 24 Hours:"
REQUESTS_24H=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no root@134.199.203.133 "journalctl -u autoppia-api --since '24 hours ago' | grep 'solve_task' | wc -l" 2>/dev/null)
echo "   API Requests: $REQUESTS_24H"
echo ""

echo "Last 7 Days:"
REQUESTS_7D=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no root@134.199.203.133 "journalctl -u autoppia-api --since '7 days ago' | grep 'solve_task' | wc -l" 2>/dev/null)
echo "   API Requests: $REQUESTS_7D"
echo ""

echo "Service Status:"
sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no root@134.199.203.133 "systemctl is-active autoppia-api autoppia-miner 2>/dev/null | head -2"
echo ""

echo "Recent Errors (last hour):"
ERRORS=$(sshpass -p 'DigitalOcean4life' ssh -o StrictHostKeyChecking=no root@134.199.203.133 "journalctl -u autoppia-api --since '1 hour ago' | grep -i error | wc -l" 2>/dev/null)
echo "   Errors: $ERRORS"
