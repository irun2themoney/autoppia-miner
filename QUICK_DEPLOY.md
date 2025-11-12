# ⚡ Quick Deploy Guide - Choose Your Platform

## 🚂 Railway (Easiest - Recommended)

**Time**: 5 minutes | **Cost**: Free tier available

### Steps:
1. Go to: https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select `irun2themoney/autoppia-miner`
5. Add environment variables (see below)
6. Done! Get your URL

**Full Guide**: See `DEPLOY_RAILWAY.md`

---

## 🎨 Render (Free Tier)

**Time**: 10 minutes | **Cost**: Free (with limitations)

### Steps:
1. Go to: https://render.com
2. Sign up with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect `irun2themoney/autoppia-miner` repo
5. Set Environment to **"Docker"**
6. Add environment variables (see below)
7. Deploy!

**Full Guide**: See `DEPLOY_RENDER.md`

---

## 🔑 Required Environment Variables

Add these in your platform's environment settings:

```
CHUTES_API_KEY=cpk_10041a5a8517400ba3c5690ab89ae279.97cdedde58e45965820657bd8ec790fa.jAcea2MMpmVk7u0Iv0HLFfWczYv8IT7L
CHUTES_API_URL=https://api.chutes.ai
WORKER_NAME=autoppia-miner
WORKER_VERSION=0.1.0
LOG_LEVEL=INFO
```

**Note**: `PORT` is automatically set by Railway/Render - don't set it manually!

---

## ✅ Test Your Deployment

Once deployed, test with:

```bash
# Replace with your deployment URL
WORKER_URL="https://your-app.up.railway.app"  # or .onrender.com

# Health check
curl $WORKER_URL/health

# Test process task
curl -X POST $WORKER_URL/process \
  -H "Content-Type: application/json" \
  -d '{"task": "process", "input_data": {"data": ["test"]}}'
```

---

## 🎯 Which Platform Should I Choose?

### Choose Railway if:
- ✅ You want the easiest deployment
- ✅ You want fastest setup (2-3 minutes)
- ✅ You want better free tier
- ✅ You want automatic HTTPS

### Choose Render if:
- ✅ You want completely free hosting
- ✅ You don't mind cold starts (15 min inactivity)
- ✅ You want simple configuration
- ✅ You're okay with slower first request after idle

---

## 📊 Comparison

| Feature | Railway | Render |
|---------|---------|--------|
| **Free Tier** | $5 credit/month | Free (limited) |
| **Setup Time** | ~3 minutes | ~5 minutes |
| **Always On** | Yes (with credit) | No (spins down) |
| **Cold Start** | None | ~30 seconds |
| **Auto-Deploy** | Yes | Yes |
| **Custom Domain** | Yes | Yes |

---

## 🚀 Quick Start (Railway - Fastest)

```bash
# 1. Go to railway.app and sign up
# 2. Click "New Project" → "Deploy from GitHub"
# 3. Select your repo
# 4. Add environment variables
# 5. Done! Copy your URL
```

**That's it!** Your worker is live in under 5 minutes.

---

## 🆘 Need Help?

- **Railway Issues**: Check `DEPLOY_RAILWAY.md`
- **Render Issues**: Check `DEPLOY_RENDER.md`
- **General Issues**: Check logs in platform dashboard

---

**Ready to deploy?** Pick a platform and follow the guide! 🚀

