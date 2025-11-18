# 📧 Contact Chutes Support - Template Message

## Subject:
**API Key Rate Limited Despite No Usage - Need Rate Limit Reset**

## Message:

Hi Chutes Support Team,

I'm experiencing an issue with my Chutes API key where I'm getting 429 (Rate Limited) errors immediately, even though I haven't made any API calls recently.

**Details:**
- **API Key**: `cpk_384e5ee3477b4345be53ecb6cf5336d6...`
- **Plan**: 5000 requests/day
- **Issue**: Getting 429 errors on fresh requests with no prior usage
- **Error Response**: `<html><title>429 Too Many Requests</title><hr><center>nginx</center>`
- **No Rate Limit Headers**: No `Retry-After` or `X-RateLimit-*` headers provided

**What I've Tried:**
- Verified API key is correct
- Tested with fresh requests (no prior usage)
- Waited several hours for rate limit to reset
- Confirmed endpoint is correct: `https://api.chutes.ai/v1/chat/completions`

**Questions:**
1. Is the rate limit at the account level or API key level?
2. Is there IP-based rate limiting that might be blocking my server IP?
3. Can you reset the rate limit for my account/API key?
4. What are the actual per-minute/per-hour rate limits for my plan?
5. Why aren't rate limit headers (`Retry-After`, `X-RateLimit-*`) provided in 429 responses?

**Server IP** (if relevant): `134.199.203.133`

Please help me resolve this issue so I can use the API as intended.

Thank you!

---

## Where to Contact:
- **Email**: support@chutes.ai (or check their website)
- **Discord**: Check their Discord server if they have one
- **Website**: https://chutes.ai (look for support/contact page)

