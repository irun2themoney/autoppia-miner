#!/bin/bash
# 🎯 Comprehensive Verification Script for Autoppia Miner
# Verifies everything is up to par with official Autoppia standards

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🔍 AUTOPPIA MINER - COMPREHENSIVE VERIFICATION 🔍        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

ERRORS=0
WARNINGS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅${NC} $1"
    else
        echo -e "${RED}❌${NC} $1"
        ERRORS=$((ERRORS + 1))
    fi
}

warn() {
    echo -e "${YELLOW}⚠️${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

echo "📦 1. Checking Python Dependencies..."
if python3 -c "import bittensor" 2>/dev/null; then
    BT_VERSION=$(python3 -c "import bittensor; print(bittensor.__version__)" 2>/dev/null || echo "unknown")
    info "Bittensor version: $BT_VERSION"
    if python3 -c "import bittensor; assert bittensor.__version__ >= '7.0.0'" 2>/dev/null; then
        check "Bittensor >= 7.0.0 installed"
    else
        warn "Bittensor version may be outdated (recommended: >= 7.0.0)"
    fi
else
    warn "Bittensor not installed"
fi

python3 -c "import fastapi" 2>/dev/null && check "FastAPI installed" || warn "FastAPI not installed"
python3 -c "import httpx" 2>/dev/null && check "httpx installed" || warn "httpx not installed"
python3 -c "import loguru" 2>/dev/null && check "loguru installed" || warn "loguru not installed"
python3 -c "import pydantic" 2>/dev/null && check "pydantic installed" || warn "pydantic not installed"

echo ""
echo "🔐 2. Checking Wallet Configuration..."
if [ -f ~/.bittensor/wallets ]; then
    WALLETS=$(btcli wallet list 2>/dev/null | wc -l || echo "0")
    if [ "$WALLETS" -gt 0 ]; then
        check "Wallets found: $WALLETS"
        btcli wallet list 2>/dev/null | head -5
    else
        warn "No wallets found"
    fi
else
    warn "Bittensor wallet directory not found"
fi

echo ""
echo "🌐 3. Checking Network Configuration..."
if [ -f .env ]; then
    check ".env file exists"
    
    if grep -q "CHUTES_API_KEY" .env && ! grep -q "CHUTES_API_KEY=your_chutes_api_key_here" .env; then
        check "CHUTES_API_KEY configured"
    else
        warn "CHUTES_API_KEY not configured"
    fi
    
    if grep -q "API_URL" .env; then
        API_URL=$(grep "API_URL" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'" | xargs)
        info "API_URL: $API_URL"
        if [[ "$API_URL" == *"134.199.201.62"* ]] || [[ "$API_URL" == *"http://"* ]]; then
            check "API_URL points to DigitalOcean VPS"
        else
            warn "API_URL may not be configured correctly"
        fi
    else
        warn "API_URL not found in .env"
    fi
else
    warn ".env file not found"
fi

echo ""
echo "📡 4. Checking API Connectivity..."
if [ -f .env ] && grep -q "API_URL" .env; then
    API_URL=$(grep "API_URL" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'" | xargs)
    if curl -s --max-time 5 "${API_URL}/health" > /dev/null 2>&1; then
        check "API health endpoint responding"
        HEALTH=$(curl -s --max-time 5 "${API_URL}/health" 2>/dev/null)
        if echo "$HEALTH" | grep -q "healthy"; then
            check "API reports healthy status"
        else
            warn "API health check returned unexpected response"
        fi
    else
        warn "API not responding at $API_URL"
    fi
else
    warn "Cannot check API - API_URL not configured"
fi

echo ""
echo "🔧 5. Checking Code Structure..."
[ -f "miner.py" ] && check "miner.py exists" || warn "miner.py missing"
[ -f "api.py" ] && check "api.py exists" || warn "api.py missing"
[ -f "worker.py" ] && check "worker.py exists" || warn "worker.py missing"
[ -f "requirements.txt" ] && check "requirements.txt exists" || warn "requirements.txt missing"

echo ""
echo "🧪 6. Checking Test Suite..."
if [ -d "tests" ]; then
    check "tests directory exists"
    TEST_COUNT=$(find tests -name "test_*.py" 2>/dev/null | wc -l)
    info "Found $TEST_COUNT test files"
    if [ "$TEST_COUNT" -gt 0 ]; then
        check "Test files present"
    fi
else
    warn "tests directory not found"
fi

echo ""
echo "🚀 7. Checking Deployment Configuration..."
if [ -f "deploy_miner_digitalocean.sh" ]; then
    check "Deployment script exists"
    if grep -q "WALLET_NAME" deploy_miner_digitalocean.sh; then
        check "Deployment script preserves wallet/hotkey"
    fi
else
    warn "Deployment script not found"
fi

echo ""
echo "📊 8. Checking Subnet Registration..."
if command -v btcli &> /dev/null; then
    if btcli wallet overview --netuid 36 2>/dev/null | grep -q "UID:"; then
        check "Registered on subnet 36"
        btcli wallet overview --netuid 36 2>/dev/null | grep "UID:" | head -1
    else
        warn "Not registered on subnet 36 (or wallet not configured)"
    fi
else
    warn "btcli not available - cannot check registration"
fi

echo ""
echo "🔒 9. Checking Firewall Configuration..."
if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        check "UFW firewall is active"
        if ufw status | grep -q "8091"; then
            check "Port 8091 (axon) is open"
        else
            warn "Port 8091 may not be open in firewall"
        fi
        if ufw status | grep -q "8080"; then
            check "Port 8080 (API) is open"
        else
            warn "Port 8080 may not be open in firewall"
        fi
    else
        warn "UFW firewall is not active"
    fi
else
    warn "UFW not installed - cannot check firewall"
fi

echo ""
echo "⚙️  10. Checking Systemd Services..."
if systemctl list-units --type=service 2>/dev/null | grep -q "autoppia"; then
    if systemctl is-active --quiet autoppia-api 2>/dev/null; then
        check "autoppia-api service is running"
    else
        warn "autoppia-api service is not running"
    fi
    
    if systemctl is-active --quiet autoppia-miner 2>/dev/null; then
        check "autoppia-miner service is running"
    else
        warn "autoppia-miner service is not running (may be intentional)"
    fi
else
    warn "No Autoppia systemd services found"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    VERIFICATION SUMMARY                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Your miner is ready to go!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS warning(s) found. Review above and fix if needed.${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS error(s) and $WARNINGS warning(s) found.${NC}"
    echo ""
    echo "Please fix the errors above before deploying."
    exit 1
fi

