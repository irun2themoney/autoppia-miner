#!/bin/bash
# Script to help check Chutes dashboard and diagnose rate limiting

echo "🔍 Chutes API Rate Limit Diagnostic"
echo "===================================="
echo ""

# Check API key
if [ -f .env ]; then
    API_KEY=$(grep CHUTES_API_KEY .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    if [ ! -z "$API_KEY" ]; then
        echo "✅ API Key found: ${API_KEY:0:30}..."
    else
        echo "❌ API Key not found in .env"
        exit 1
    fi
else
    echo "❌ .env file not found"
    exit 1
fi

echo ""
echo "📊 What to Check in Chutes Dashboard:"
echo "======================================"
echo ""
echo "1. Log into your Chutes account: https://chutes.ai (or your dashboard URL)"
echo ""
echo "2. Check Account Usage:"
echo "   - Look for 'Usage' or 'API Usage' section"
echo "   - Check total requests today"
echo "   - Check requests per minute/hour"
echo ""
echo "3. Check API Keys:"
echo "   - List all API keys in your account"
echo "   - See if this key is used elsewhere"
echo "   - Check if any other keys are active"
echo ""
echo "4. Check Rate Limits:"
echo "   - Look for 'Rate Limits' or 'Limits' section"
echo "   - Check per-minute limits"
echo "   - Check per-hour limits"
echo "   - Check if account is rate limited"
echo ""
echo "5. Check Account Status:"
echo "   - Verify account is active"
echo "   - Check if account has restrictions"
echo "   - Verify plan is 5000 requests/day"
echo ""
echo "6. Check IP Restrictions:"
echo "   - See if server IP is blocked"
echo "   - Check if IP whitelisting is enabled"
echo ""
echo "📧 If Still Rate Limited:"
echo "   - Use contact_chutes_support.md template"
echo "   - Contact Chutes support with details"
echo "   - Request rate limit reset"
echo ""
echo "🧪 Test API Key:"
echo "   Run: python3 test_fresh_api_key.py"
echo ""

