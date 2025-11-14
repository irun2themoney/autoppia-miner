#!/bin/bash
# Test API with InfiniteWeb Arena-like requests

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🧪 TESTING API WITH INFINITEWEB ARENA FORMAT 🧪          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

API_URL="http://localhost:8080"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1: Login Task (with prompt, no URL)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -X POST ${API_URL}/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-login-001",
    "prompt": "First, authenticate with username testuser and password password123 to log in successfully.",
    "url": ""
  }' 2>&1 | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2: Film Detail Task (with prompt, no URL)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -X POST ${API_URL}/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-film-detail-001",
    "prompt": "Show details for a movie with a duration of LESS THAN 169 minutes",
    "url": ""
  }' 2>&1 | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 3: Search Task (with prompt, no URL)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -X POST ${API_URL}/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-search-001",
    "prompt": "Search for the movie that is NOT Goodfellas in the database",
    "url": ""
  }' 2>&1 | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 4: Form Fill Task (with prompt, no URL)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -X POST ${API_URL}/solve_task \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-form-fill-001",
    "prompt": "Go to the contact page and fill out the form with a name that equals William.",
    "url": ""
  }' 2>&1 | python3 -m json.tool

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All tests complete! Check the responses above."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

