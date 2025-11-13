#!/usr/bin/env bash
# Quick health check for Autoppia Miner
set -e

echo "=== Miner Status ==="
pm2 status autoppia_miner 2>/dev/null || echo "⚠️  PM2 not running or autoppia_miner process not found"

echo ""
echo "=== Recent Activity (Last 10 lines) ==="
pm2 logs autoppia_miner --lines 10 --nostream 2>&1 | tail -10 || echo "⚠️  Could not fetch logs"

echo ""
echo "=== Wallet Balance ==="
if command -v btcli &> /dev/null; then
    btcli wallet balance --wallet.name default 2>&1 | grep -E "(Free|Total|Stake)" || echo "⚠️  Could not fetch wallet balance"
else
    echo "⚠️  btcli not found"
fi

echo ""
echo "=== Worker Health ==="
if command -v python3 &> /dev/null; then
    curl -s https://autoppia-miner.onrender.com/health 2>&1 | python3 -m json.tool 2>/dev/null || curl -s https://autoppia-miner.onrender.com/health 2>/dev/null || echo "⚠️  Worker not responding"
else
    curl -s https://autoppia-miner.onrender.com/health 2>&1 || echo "⚠️  Could not reach worker"
fi

echo ""
echo "=== Check Complete ==="
