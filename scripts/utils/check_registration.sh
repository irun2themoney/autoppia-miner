#!/bin/bash
# Check Bittensor miner registration status on subnet 36
# Usage: ./check_registration.sh [wallet_name] [hotkey_name]

set -e

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Get wallet name and hotkey from args or env
WALLET_NAME="${1:-${WALLET_NAME:-default}}"
HOTKEY_NAME="${2:-${WALLET_HOTKEY:-default}}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Checking Miner Registration Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Wallet: $WALLET_NAME"
echo "Hotkey: $HOTKEY_NAME"
echo "Subnet: 36 (Infinite Web Arena)"
echo ""

# Check if btcli is installed
if ! command -v btcli &> /dev/null; then
    echo "❌ btcli not found!"
    echo "   Install with: pip install bittensor"
    exit 1
fi

# Check if wallet exists
echo "📋 Step 1: Checking if wallet exists..."
if btcli wallet list 2>/dev/null | grep -q "$WALLET_NAME"; then
    echo "   ✅ Wallet '$WALLET_NAME' found"
else
    echo "   ❌ Wallet '$WALLET_NAME' not found!"
    echo ""
    echo "   Create wallet with:"
    echo "   btcli wallet create --wallet.name $WALLET_NAME"
    echo ""
    exit 1
fi
echo ""

# Check if hotkey exists
echo "📋 Step 2: Checking if hotkey exists..."
if btcli wallet list 2>/dev/null | grep -A 10 "$WALLET_NAME" | grep -q "$HOTKEY_NAME"; then
    echo "   ✅ Hotkey '$HOTKEY_NAME' found"
else
    echo "   ❌ Hotkey '$HOTKEY_NAME' not found in wallet '$WALLET_NAME'!"
    echo ""
    echo "   Create hotkey with:"
    echo "   btcli wallet new_hotkey --wallet.name $WALLET_NAME --wallet.hotkey $HOTKEY_NAME"
    echo ""
    exit 1
fi
echo ""

# Get wallet overview
echo "📋 Step 3: Checking registration on subnet 36..."
OVERVIEW=$(btcli wallet overview --netuid 36 --wallet.name "$WALLET_NAME" --wallet.hotkey "$HOTKEY_NAME" 2>&1 || true)

if echo "$OVERVIEW" | grep -q "UID:"; then
    echo "   ✅ Miner is REGISTERED on subnet 36!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Registration Details:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$OVERVIEW"
    echo ""
    
    # Extract UID
    UID=$(echo "$OVERVIEW" | grep "UID:" | awk '{print $2}')
    echo "Your UID: $UID"
    echo ""
    
    # Check metagraph position
    echo "📋 Step 4: Checking metagraph position..."
    echo ""
    btcli subnet metagraph --netuid 36 2>/dev/null | grep -A 2 -B 2 "^$UID " || echo "   ⚠️  Could not find UID in metagraph (may need to sync)"
    echo ""
    
else
    echo "   ❌ Miner is NOT registered on subnet 36!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Registration Required"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "To register your miner, you need:"
    echo "  1. At least 0.1 TAO in your wallet"
    echo "  2. Run the registration command:"
    echo ""
    echo "     btcli subnet register --netuid 36 --wallet.name $WALLET_NAME --wallet.hotkey $HOTKEY_NAME"
    echo ""
    echo "Current wallet balance:"
    btcli wallet balance --wallet.name "$WALLET_NAME" 2>/dev/null || echo "   ⚠️  Could not fetch balance"
    echo ""
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Registration Check Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
