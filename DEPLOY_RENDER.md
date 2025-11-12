# 🎨 Deploy to Render - Step by Step Guide

Render offers a free tier perfect for deploying your Autoppia worker. Here's how:

## Prerequisites

- GitHub account (your code is already there!)
- Render account (free signup)

---

## Step 1: Sign Up for Render

1. Go to: **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with GitHub (recommended)
4. Authorize Render to access your GitHub

---

## Step 2: Create a New Web Service

1. In Render Dashboard, click **"New +"**
2. Select **"Web Service"**
3. Connect your GitHub account (if not already)
4. Find and select **`irun2themoney/autoppia-miner`** repository
5. Click **"Connect"**

---

## Step 3: Configure Your Service

Fill in the form:

### Basic Settings:
- **Name**: `autoppia-miner` (or any name you like)
- **Region**: Choose closest to you (Oregon, Frankfurt, etc.)
- **Branch**: `main`
- **Root Directory**: Leave empty (or `.`)

### Build & Deploy:
- **Environment**: `Docker`
- **Dockerfile Path**: `Dockerfile` (should auto-detect)
- **Docker Context**: `.` (root directory)

### Advanced Settings:
- **Instance Type**: `Free` (or upgrade if needed)
- **Auto-Deploy**: `Yes` (deploys on every push)

Click **"Create Web Service"**

---

## Step 4: Configure Environment Variables

1. In your service dashboard, go to **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Add these variables one by one:

```
CHUTES_API_KEY = cpk_10041a5a8517400ba3c5690ab89ae279.97cdedde58e45965820657bd8ec790fa.jAcea2MMpmVk7u0Iv0HLFfWczYv8IT7L
CHUTES_API_URL = https://api.chutes.ai
WORKER_NAME = autoppia-miner
WORKER_VERSION = 0.1.0
LOG_LEVEL = INFO
```

4. Render will automatically redeploy with new variables

---

## Step 5: Get Your Public URL

1. Once deployment starts, Render shows your URL
2. It will be something like:
   - `https://autoppia-miner.onrender.com`
3. Wait for deployment to complete (2-5 minutes)
4. Copy your URL!

---

## Step 6: Test Your Deployed Worker

```bash
# Replace with your Render URL
WORKER_URL="https://autoppia-miner.onrender.com"

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

## Step 7: Custom Domain (Optional)

1. In **Settings** → **Custom Domains**
2. Add your domain
3. Follow DNS configuration instructions

---

## Render Free Tier Notes

⚠️ **Important**: Render free tier has some limitations:
- **Spins down after 15 minutes of inactivity**
- First request after spin-down takes ~30 seconds (cold start)
- **512MB RAM limit**
- **0.1 CPU share**

**For production**, consider upgrading to:
- **Starter Plan**: $7/month (always on, more resources)

---

## Monitoring & Logs

- **View Logs**: Click on your service → **"Logs"** tab
- **Metrics**: Render shows CPU, Memory, Request metrics
- **Events**: See deployment history and events

---

## Auto-Deploy

Render automatically deploys when you push to GitHub:
1. Push changes to `main` branch
2. Render detects the push
3. Automatically rebuilds and redeploys
4. Your worker updates automatically!

---

## Troubleshooting

### Build Fails
- Check logs in Render dashboard
- Ensure Dockerfile is correct
- Verify all dependencies in requirements.txt
- Check Docker build logs

### App Won't Start
- Check environment variables are set correctly
- Verify PORT is set (Render sets this automatically)
- Check logs for Python errors
- Ensure `api.py` starts correctly

### 502 Bad Gateway
- Wait for deployment to complete (can take 2-5 minutes)
- Check health endpoint: `/health`
- Verify start command in Dockerfile
- Check if service spun down (free tier)

### Service Spun Down (Free Tier)
- First request after 15 min inactivity takes ~30 seconds
- This is normal for free tier
- Upgrade to paid plan for always-on service

---

## Using render.yaml (Alternative)

We've included a `render.yaml` file in your repo. You can use it:

1. **Create Blueprint**:
   - In Render, click **"New +"** → **"Blueprint"**
   - Connect your GitHub repo
   - Render will read `render.yaml` automatically
   - Click **"Apply"**

This method uses the configuration file instead of manual setup.

---

## Success! 🎉

Your worker is now live at: `https://your-app.onrender.com`

**Next Steps:**
- Share your worker URL
- Test all endpoints
- Integrate into other projects
- Monitor usage in Render dashboard

---

## Render Pricing

- **Free**: $0/month (with limitations)
- **Starter**: $7/month (always on, better performance)
- **Professional**: $25/month (production-ready)

---

**Need Help?**
- Render Docs: https://render.com/docs
- Render Support: https://render.com/support

