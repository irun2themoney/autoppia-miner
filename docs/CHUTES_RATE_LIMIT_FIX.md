# Chutes API Rate Limit Issue & Fix

## The Problem

We're getting immediate 429 (Rate Limited) errors even though:
- Daily quota shows 0/5000 used
- We just started using the API

## Root Cause

Chutes API has **separate rate limits**:
1. **Daily quota**: 5000 requests/day (we have 0/5000 used ✅)
2. **Per-minute/per-second limits**: Much stricter (likely 10-20 requests/minute)
3. **Per-IP limits**: May also apply

During testing, we made many requests quickly and hit the **per-minute rate limits**, which are separate from the daily quota.

## The Fix

Updated the code to:
1. **Increase wait time**: 3 seconds between requests (was 1 second)
2. **Exponential backoff**: Wait 60s, 120s, 240s after 429 errors
3. **Track consecutive errors**: Reset counter on success
4. **Better logging**: Show wait times and retry attempts

## What Changed

- `min_request_interval`: 1.0s → 3.0s (20 req/min max)
- Added `consecutive_429_errors` tracking
- Added `last_429_time` tracking
- Exponential backoff: 60s → 120s → 240s → 300s max

## Next Steps

1. **Wait 5-10 minutes** for rate limits to reset
2. **Test again** - should work after rate limit window resets
3. **Monitor usage** - stay under 20 requests/minute

## Testing

After waiting, test with:
```bash
./check_chutes_status.sh
```

Or wait automatically:
```bash
./wait_for_chutes.sh
```

## Expected Behavior

- **First request after reset**: Should work ✅
- **Subsequent requests**: 3+ seconds apart
- **If 429 occurs**: Wait 60+ seconds before retry
- **After success**: Reset error counter

The system will now handle rate limits much better and automatically recover when limits reset.

