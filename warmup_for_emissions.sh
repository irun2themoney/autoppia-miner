#!/usr/bin/env bash
# 🚀 EMISSIONS WARM-UP SCRIPT
# Run this exactly 10 minutes before emissions (10:50 AM)
# This primes the system for maximum performance

set -e

echo "🔥 EMISSIONS WARM-UP SEQUENCE"
echo "============================="
echo ""
echo "⏰ Running at: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🎯 Purpose: Prime system for optimal first-request performance"
echo ""

# Check miner is running
echo "✓ Checking miner status..."
pm2 status autoppia_miner | grep -q "online" && echo "  ✅ Miner is ONLINE" || echo "  ⚠️  Miner check skipped"

# Check worker health
echo "✓ Checking worker health..."
curl -s https://autoppia-miner.onrender.com/health > /dev/null && echo "  ✅ Worker is HEALTHY" || echo "  ⚠️  Worker check failed"

echo ""
echo "🔥 Starting warm-up requests (15 total)..."
echo "   This primes Render, caches, and connections"
echo ""

# Run 15 warm-up requests
success_count=0
for i in {1..15}; do
    response=$(curl -s -X POST https://autoppia-miner.onrender.com/solve_task \
        -H "Content-Type: application/json" \
        -d "{
            \"id\": \"warmup_pre_emissions_$i\",
            \"prompt\": \"Pre-emissions warmup request\",
            \"url\": \"https://example.com\"
        }" 2>/dev/null)
    
    if echo "$response" | grep -q "success"; then
        success_count=$((success_count + 1))
        echo "  ✅ Request $i/15 - Success"
    else
        echo "  ⚠️  Request $i/15 - Check response"
    fi
done

echo ""
echo "📊 Warm-up Complete!"
echo "   Successful warm-ups: $success_count/15"
echo ""

# Final verification
echo "✅ Final Health Check:"
curl -s https://autoppia-miner.onrender.com/health | python3 -m json.tool | head -8

echo ""
echo "🎉 SYSTEM READY FOR EMISSIONS!"
echo ""
echo "⏰ Current time: $(date '+%H:%M:%S')"
echo "⏳ Emissions start: 11:00 AM"
echo "✅ System status: PRIMED & READY"
echo ""
echo "Monitor dashboard at: http://localhost:8090"
echo ""

