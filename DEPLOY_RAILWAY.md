# 🚂 Deploy to Railway - Step by Step Guide

Railway is one of the easiest platforms to deploy Docker apps. Here's how to deploy your Autoppia worker:

## Prerequisites

- GitHub account (your code is already there!)
- Railway account (free signup)

---

## Step 1: Sign Up for Railway

1. Go to: **https://railway.app**
2. Click **"Start a New Project"**
3. Sign up with GitHub (recommended) or email
4. Authorize Railway to access your GitHub

---

## Step 2: Deploy Your Project

### Option A: Deploy from GitHub (Recommended - 2 minutes)

1. **In Railway Dashboard**, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select **`irun2themoney/autoppia-miner`**
4. Railway will automatically detect your Dockerfile
5. Click **"Deploy Now"**

That's it! Railway will:
- Build your Docker image
- Deploy your worker
- Give you a public URL

### Option B: Manual Deploy

1. Click **"New Project"** → **"Empty Project"**
2. Click **"Add Service"** → **"GitHub Repo"**
3. Select your `autoppia-miner` repo
4. Railway auto-detects Dockerfile
5. Deploy!

---

## Step 3: Configure Environment Variables

1. Click on your deployed service
2. Go to **"Variables"** tab
3. Add these environment variables:

```
CHUTES_API_KEY=cpk_10041a5a8517400ba3c5690ab89ae279.97cdedde58e45965820657bd8ec790fa.jAcea2MMpmVk7u0Iv0HLFfWczYv8IT7L
CHUTES_API_URL=https://api.chutes.ai
WORKER_NAME=autoppia-miner
WORKER_VERSION=0.1.0
LOG_LEVEL=INFO
```

4. Railway will automatically redeploy with new variables

---

## Step 4: Get Your Public URL

1. In your service, go to **"Settings"**
2. Under **"Domains"**, Railway gives you a URL like:
   - `https://autoppia-miner-production.up.railway.app`
3. Copy this URL - this is your worker's public endpoint!

---

## Step 5: Test Your Deployed Worker

```bash
# Replace with your Railway URL
WORKER_URL="https://your-app.up.railway.app"

# Health check
curl $WORKER_URL/health

# Metadata
curl $WORKER_URL/metadata

# Test process task
curl -X POST $WORKER_URL/process \
  -H "Content-Type: application/json" \
  -d '{
    "task": "process",
    "input_data": {
      "data": ["test1", "test2"]
    }
  }'
```

---

## Step 6: Custom Domain (Optional)

1. In **Settings** → **Domains**
2. Click **"Generate Domain"** or **"Add Custom Domain"**
3. Follow instructions to configure DNS

---

## Monitoring & Logs

- **View Logs**: Click on your service → **"Deployments"** → Click a deployment → **"View Logs"**
- **Metrics**: Railway shows CPU, Memory, Network usage
- **Restart**: Click **"Redeploy"** if needed

---

## Railway Pricing

- **Free Tier**: $5 credit/month (usually enough for small apps)
- **Hobby Plan**: $5/month for more resources
- **Pro Plan**: $20/month for production apps

---

## Troubleshooting

### Build Fails
- Check logs in Railway dashboard
- Ensure Dockerfile is correct
- Verify all dependencies in requirements.txt

### App Won't Start
- Check environment variables are set
- Verify PORT is set (Railway sets this automatically)
- Check logs for errors

### 502 Bad Gateway
- Wait a few minutes for deployment to complete
- Check health endpoint: `/health`
- Verify start command is correct

---

## Quick Commands

```bash
# Install Railway CLI (optional)
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# View logs
railway logs

# Open in browser
railway open
```

---

## Success! 🎉

Your worker is now live at: `https://your-app.up.railway.app`

**Next Steps:**
- Share your worker URL
- Integrate it into other projects
- Monitor usage in Railway dashboard
- When Autoppia Studio opens, you're ready!

---

**Need Help?**
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

