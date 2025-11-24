#!/bin/bash
# Comprehensive test script to verify miner is ready for validators
# Tests API, miner startup, and validator simulation

set -e

echo "🧪 Starting Validator Connection Test Suite..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if API is running
echo -e "${BLUE}📡 Checking if API server is running...${NC}"
if curl -s http://localhost:8080/solve_task > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API server is running${NC}"
    API_RUNNING=true
else
    echo -e "${YELLOW}⚠️  API server not running${NC}"
    echo -e "${YELLOW}   Starting API server in background...${NC}"
    python3 -m api.server > /tmp/api_test.log 2>&1 &
    API_PID=$!
    sleep 3
    
    if curl -s http://localhost:8080/solve_task > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API server started${NC}"
        API_RUNNING=true
    else
        echo -e "${RED}❌ Failed to start API server${NC}"
        API_RUNNING=false
    fi
fi

echo ""
echo -e "${BLUE}🧪 Running validator connection tests...${NC}"
echo ""

# Run Python test suite
python3 tests/test_validator_connection.py --api-url http://localhost:8080
TEST_RESULT=$?

echo ""
echo -e "${BLUE}🧪 Running miner startup tests...${NC}"
echo ""

python3 tests/test_miner_startup.py
STARTUP_RESULT=$?

echo ""
echo -e "${BLUE}📊 Final Results${NC}"
echo ""

if [ $TEST_RESULT -eq 0 ] && [ $STARTUP_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo -e "${GREEN}🎉 Miner is ready for validators!${NC}"
    
    if [ ! -z "$API_PID" ]; then
        echo ""
        echo -e "${YELLOW}⚠️  Stopping test API server (PID: $API_PID)${NC}"
        kill $API_PID 2>/dev/null || true
    fi
    
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo -e "${RED}⚠️  Fix issues before deploying to production${NC}"
    
    if [ ! -z "$API_PID" ]; then
        echo ""
        echo -e "${YELLOW}⚠️  Stopping test API server (PID: $API_PID)${NC}"
        kill $API_PID 2>/dev/null || true
    fi
    
    exit 1
fi

