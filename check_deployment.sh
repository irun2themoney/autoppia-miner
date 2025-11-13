#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🔍 DEPLOYMENT HEALTH CHECK 🔍                         ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

BASE_URL="https://autoppia-miner.onrender.com"
ERRORS=0
WARNINGS=0

# Function to check endpoint with detailed validation
check_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo "Testing: $name"
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo "   ✅ HTTP Status: $http_code OK"
        
        # Validate JSON structure
        if ! echo "$body" | python3 -m json.tool > /dev/null 2>&1; then
            echo "   ❌ Invalid JSON response"
            ERRORS=$((ERRORS + 1))
            echo ""
            return
        fi
        
        # Parse JSON for validation
        if echo "$body" | grep -q '"status"'; then
            status=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'N/A'))" 2>/dev/null)
            if [ "$status" = "healthy" ] || [ "$status" = "running" ] || [ "$status" = "operational" ]; then
                echo "   ✅ Status field: $status"
            elif [ "$status" = "unhealthy" ] || [ "$status" = "error" ]; then
                echo "   ❌ Status field: $status (UNHEALTHY)"
                ERRORS=$((ERRORS + 1))
            else
                echo "   ✅ Status field: $status"
            fi
        fi
        
        # Check for success field
        if echo "$body" | grep -q '"success"'; then
            success=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', 'N/A'))" 2>/dev/null)
            if [ "$success" = "True" ] || [ "$success" = "true" ]; then
                echo "   ✅ Success: true"
            elif [ "$success" = "False" ] || [ "$success" = "false" ]; then
                # Check if it's an expected error (like missing prompt)
                error_msg=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', ''))" 2>/dev/null)
                if [ -n "$error_msg" ]; then
                    echo "   ⚠️  Success: false (Error: $error_msg)"
                    WARNINGS=$((WARNINGS + 1))
                else
                    echo "   ❌ Success: false (Unexpected failure)"
                    ERRORS=$((ERRORS + 1))
                fi
            fi
        fi
        
        # Validate actions array if present
        if echo "$body" | grep -q '"actions"'; then
            actions_count=$(echo "$body" | python3 -c "import sys, json; actions = json.load(sys.stdin).get('actions', []); print(len(actions) if isinstance(actions, list) else 0)" 2>/dev/null)
            if [ "$actions_count" -gt 0 ]; then
                echo "   ✅ Actions: $actions_count generated"
                
                # Validate action structure
                missing_action_type=$(echo "$body" | python3 -c "
import sys, json
data = json.load(sys.stdin)
actions = data.get('actions', [])
if not isinstance(actions, list):
    print('invalid')
else:
    for i, action in enumerate(actions):
        if not isinstance(action, dict) or 'action_type' not in action:
            print(f'action_{i}_missing_type')
            break
    else:
        print('ok')
" 2>/dev/null)
                
                if [ "$missing_action_type" != "ok" ]; then
                    echo "   ❌ Actions missing 'action_type' field: $missing_action_type"
                    ERRORS=$((ERRORS + 1))
                else
                    echo "   ✅ All actions have 'action_type' field"
                fi
            else
                echo "   ⚠️  Actions: 0 (empty array)"
                WARNINGS=$((WARNINGS + 1))
            fi
        fi
        
        # Check for error field in successful responses
        if echo "$body" | grep -q '"error"'; then
            error=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', ''))" 2>/dev/null)
            success_val=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', True))" 2>/dev/null)
            if [ "$success_val" = "True" ] || [ "$success_val" = "true" ]; then
                echo "   ⚠️  Warning: Error field present in successful response"
                WARNINGS=$((WARNINGS + 1))
            fi
        fi
        
    else
        echo "   ❌ HTTP Status: $http_code ERROR"
        echo "   📄 Response: $(echo "$body" | head -3)"
        ERRORS=$((ERRORS + 1))
    fi
    echo ""
}

# 1. Health Check
check_endpoint "Health Check" "GET" "/health" ""

# 2. Root Endpoint
check_endpoint "Root Endpoint" "GET" "/" ""

# 3. Metadata
check_endpoint "Metadata" "GET" "/metadata" ""

# 4. Solve Task (Main Endpoint)
check_endpoint "Solve Task" "POST" "/solve_task" '{"id": "health_check", "prompt": "Click button", "url": "https://example.com"}'

# 5. Metrics
check_endpoint "Metrics" "GET" "/metrics" ""

# Additional validation: Check health endpoint details
echo "6️⃣  Detailed Health Check:"
health_response=$(curl -s "$BASE_URL/health")
chutes_status=$(echo "$health_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('chutes_api_status', 'N/A'))" 2>/dev/null)
if [ "$chutes_status" = "error" ]; then
    echo "   ⚠️  Chutes API: $chutes_status (non-critical - fallbacks available)"
    WARNINGS=$((WARNINGS + 1))
else
    echo "   ✅ Chutes API: $chutes_status"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED - Deployment is healthy!"
    echo "✅ No errors or warnings detected"
    echo "✅ Ready for validators"
elif [ $ERRORS -eq 0 ]; then
    echo "✅ DEPLOYMENT HEALTHY (with $WARNINGS warning(s))"
    echo "⚠️  Warnings are non-critical but should be reviewed"
    echo "✅ Ready for validators"
else
    echo "❌ $ERRORS ERROR(S) FOUND - Deployment has issues!"
    if [ $WARNINGS -gt 0 ]; then
        echo "⚠️  $WARNINGS WARNING(S) also present"
    fi
    echo "❌ NOT ready for validators - fix errors first"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
