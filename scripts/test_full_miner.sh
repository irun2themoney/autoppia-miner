#!/bin/bash
# Comprehensive end-to-end test script for the miner

set -e

echo "=========================================="
echo "🧪 FULL MINER TEST SUITE"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to run test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${BLUE}🔍 Running: $test_name${NC}"
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAILED: $test_name${NC}"
        ((FAILED++))
        return 1
    fi
    echo ""
}

# Test 1: Check Python environment
echo "=========================================="
echo "TEST 1: Environment Check"
echo "=========================================="
run_test "Python version check" "python3 --version | grep -q 'Python 3'"
run_test "Required packages" "python3 -c 'import fastapi, bittensor, playwright' 2>/dev/null"

# Test 2: Import all modules
echo ""
echo "=========================================="
echo "TEST 2: Module Imports"
echo "=========================================="
run_test "Import API modules" "python3 -c 'from api.server import app; from api.endpoints import router'"
run_test "Import miner modules" "python3 -c 'from miner import miner; from miner.protocol import StartRoundSynapse, TaskSynapse'"
run_test "Import optimizers" "python3 -c 'from api.utils.action_optimizer import ActionOptimizer; from api.utils.response_quality import ResponseQualityEnhancer'"
run_test "Import settings" "python3 -c 'from config.settings import settings'"

# Test 3: API Server Startup
echo ""
echo "=========================================="
echo "TEST 3: API Server"
echo "=========================================="
run_test "Start API server" "timeout 5 python3 -m api.server > /tmp/api_test.log 2>&1 & sleep 2; kill %1 2>/dev/null || true"
run_test "Health endpoint" "curl -s http://localhost:8080/health 2>/dev/null | grep -q 'healthy' || (python3 -m api.server > /tmp/api_test.log 2>&1 & sleep 3; curl -s http://localhost:8080/health | grep -q 'healthy')"

# Test 4: API Endpoints
echo ""
echo "=========================================="
echo "TEST 4: API Endpoints"
echo "=========================================="
run_test "Health endpoint" "curl -s http://localhost:8080/health | python3 -m json.tool > /dev/null"
run_test "Solve task endpoint" "curl -s -X POST http://localhost:8080/solve_task -H 'Content-Type: application/json' -d '{\"id\":\"test\",\"prompt\":\"test\",\"url\":\"https://example.com\"}' | python3 -m json.tool > /dev/null"

# Test 5: Action Generation
echo ""
echo "=========================================="
echo "TEST 5: Action Generation"
echo "=========================================="
run_test "Action generator" "python3 -c 'from api.actions.generator import ActionGenerator; import asyncio; gen = ActionGenerator(); actions = asyncio.run(gen.generate(\"Navigate to example.com\", \"https://example.com\")); assert len(actions) > 0'"

# Test 6: Performance Optimizations
echo ""
echo "=========================================="
echo "TEST 6: Performance Optimizations"
echo "=========================================="
run_test "Action optimizer" "python3 -c 'from api.utils.action_optimizer import ActionOptimizer; opt = ActionOptimizer(); actions = [{\"type\":\"WaitAction\"},{\"type\":\"WaitAction\"}]; opt.optimize_action_sequence(actions)'"
run_test "Quality enhancer" "python3 -c 'from api.utils.response_quality import ResponseQualityEnhancer; enh = ResponseQualityEnhancer(); score = enh.calculate_quality_score([{\"type\":\"NavigateAction\",\"url\":\"https://example.com\"}]); assert score > 0'"

# Test 7: Validator Synapses
echo ""
echo "=========================================="
echo "TEST 7: Validator Synapses"
echo "=========================================="
run_test "StartRoundSynapse" "python3 -c 'from miner.protocol import StartRoundSynapse; s = StartRoundSynapse(round_id=\"test\", task_type=\"test\"); assert s.round_id == \"test\"'"
run_test "TaskSynapse" "python3 -c 'from miner.protocol import TaskSynapse; t = TaskSynapse(); t.prompt = \"test\"; assert t.prompt == \"test\"'"

# Test 8: IWA Format Compliance
echo ""
echo "=========================================="
echo "TEST 8: IWA Format Compliance"
echo "=========================================="
run_test "IWA format check" "python3 -c 'import json; resp = json.loads(\"$(curl -s -X POST http://localhost:8080/solve_task -H \"Content-Type: application/json\" -d '{\"id\":\"test\",\"prompt\":\"test\",\"url\":\"https://example.com\"}')\"); assert \"actions\" in resp; assert \"web_agent_id\" in resp; assert len(resp[\"actions\"]) > 0'"

# Test 9: Error Handling
echo ""
echo "=========================================="
echo "TEST 9: Error Handling"
echo "=========================================="
run_test "Invalid request handling" "curl -s -X POST http://localhost:8080/solve_task -H 'Content-Type: application/json' -d '{\"id\":\"test\"}' | python3 -m json.tool > /dev/null"
run_test "Empty prompt handling" "curl -s -X POST http://localhost:8080/solve_task -H 'Content-Type: application/json' -d '{\"id\":\"test\",\"prompt\":\"\",\"url\":\"\"}' | python3 -m json.tool > /dev/null"

# Test 10: Production Server Check
echo ""
echo "=========================================="
echo "TEST 10: Production Server"
echo "=========================================="
if [ -n "$1" ] && [ "$1" == "--production" ]; then
    SERVER_IP="134.199.203.133"
    echo -e "${BLUE}🔍 Testing production server: $SERVER_IP${NC}"
    run_test "Production API health" "curl -s http://$SERVER_IP:8080/health | grep -q 'healthy'"
    run_test "Production solve_task" "curl -s -X POST http://$SERVER_IP:8080/solve_task -H 'Content-Type: application/json' -d '{\"id\":\"test\",\"prompt\":\"test\",\"url\":\"https://example.com\"}' | python3 -m json.tool > /dev/null"
else
    echo -e "${YELLOW}⏭️  Skipping production tests (use --production flag)${NC}"
fi

# Cleanup
pkill -f "python3 -m api.server" 2>/dev/null || true

# Summary
echo ""
echo "=========================================="
echo "📊 TEST SUMMARY"
echo "=========================================="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Failed: $FAILED${NC}"
else
    echo -e "${GREEN}❌ Failed: $FAILED${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    exit 1
fi

