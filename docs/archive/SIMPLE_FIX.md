# Simple Fix for "Failed to fetch" Error

## What's Happening?

The IWA Playground (which runs on HTTPS) is trying to connect to your API, but it's failing.

## The Problem

- Your API is at: `http://134.199.203.133:8080` (HTTP)
- Playground is at: `https://infinitewebarena.autoppia.com` (HTTPS)
- Browsers block HTTP requests from HTTPS pages (security)

## The Solution

Use the HTTPS tunnel URL instead of the direct IP.

## Step-by-Step Fix

### Step 1: Go to IWA Playground
https://infinitewebarena.autoppia.com/playground

### Step 2: In the "Agent Endpoint" field, enter:
```
got-pen-mass-subdivision.trycloudflare.com
```

**Important**: 
- ✅ DO enter: `got-pen-mass-subdivision.trycloudflare.com`
- ❌ DON'T enter: `https://got-pen-mass-subdivision.trycloudflare.com`
- ❌ DON'T enter: `134.199.203.133:8080` (this won't work from HTTPS page)

### Step 3: Click "Run Benchmark"

That's it!

## Why This Works

The tunnel (`got-pen-mass-subdivision.trycloudflare.com`) provides HTTPS access to your HTTP API, so the playground can connect to it.

## If It Still Doesn't Work

Run this command to get the latest tunnel URL:
```bash
bash scripts/fix_playground_access.sh
```

Then use the URL it shows you in the playground.

