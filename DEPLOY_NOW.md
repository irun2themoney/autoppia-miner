# 🚀 Deploy Your Worker Right Now!

Since Autoppia Studio is on a waiting list, let's deploy your worker so you can use it immediately!

## Quick Deploy Options

### Option 1: Local Deployment (Easiest - 2 minutes)

```bash
# Start the API server
python3 api.py

# In another terminal, test it:
curl http://localhost:8080/health
```

**Your worker is now running at**: `http://localhost:8080`

---

### Option 2: Docker Deployment (Recommended - 5 minutes)

```bash
# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Test it
curl http://localhost:8080/health

# Stop it
docker-compose down
```

---

### Option 3: Cloud Deployment (Free Options)

#### Railway (Easiest Cloud Option)
1. Go to: https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `autoppia-miner` repo
5. Railway auto-detects Docker and deploys!
6. Your worker gets a public URL

#### Render (Free Tier)
1. Go to: https://render.com
2. Sign up
3. New → Web Service
4. Connect GitHub repo
5. Use Docker
6. Deploy!

#### Heroku (Free Tier Ended, but Paid Options)
1. Install Heroku CLI
2. `heroku create autoppia-miner`
3. `git push heroku main`
4. Done!

---

## Test Your Deployed Worker

Once deployed, test all endpoints:

```bash
# Health check
curl https://your-worker-url.com/health

# Metadata
curl https://your-worker-url.com/metadata

# Process task
curl -X POST https://your-worker-url.com/process \
  -H "Content-Type: application/json" \
  -d '{
    "task": "process",
    "input_data": {
      "data": ["item1", "item2", "item3"]
    }
  }'

# Mine task
curl -X POST https://your-worker-url.com/process \
  -H "Content-Type: application/json" \
  -d '{
    "task": "mine",
    "input_data": {
      "source": "test_source",
      "pattern": "test_pattern"
    }
  }'

# Generate task
curl -X POST https://your-worker-url.com/process \
  -H "Content-Type: application/json" \
  -d '{
    "task": "generate",
    "input_data": {
      "prompt": "Hello, world!"
    }
  }'
```

---

## Environment Variables for Cloud

Make sure to set these in your cloud platform:

```bash
CHUTES_API_KEY=cpk_10041a5a8517400ba3c5690ab89ae279.97cdedde58e45965820657bd8ec790fa.jAcea2MMpmVk7u0Iv0HLFfWczYv8IT7L
CHUTES_API_URL=https://api.chutes.ai
WORKER_NAME=autoppia-miner
WORKER_VERSION=0.1.0
LOG_LEVEL=INFO
```

---

## Quick Start Script

Create a simple test script:

```bash
#!/bin/bash
# test_worker.sh

WORKER_URL="${1:-http://localhost:8080}"

echo "Testing worker at: $WORKER_URL"
echo ""

echo "1. Health Check:"
curl -s "$WORKER_URL/health" | python3 -m json.tool
echo ""

echo "2. Metadata:"
curl -s "$WORKER_URL/metadata" | python3 -m json.tool
echo ""

echo "3. Process Task:"
curl -s -X POST "$WORKER_URL/process" \
  -H "Content-Type: application/json" \
  -d '{"task": "process", "input_data": {"data": ["test"]}}' \
  | python3 -m json.tool
```

Run it:
```bash
chmod +x test_worker.sh
./test_worker.sh http://localhost:8080
# Or with your deployed URL:
./test_worker.sh https://your-worker-url.com
```

---

## Next Steps

1. **Deploy now** - Don't wait for Autoppia Studio
2. **Use your worker** - Integrate it into projects
3. **Share it** - Let others use it
4. **Get feedback** - Improve based on usage
5. **Be ready** - When Autoppia Studio opens, you're prepared!

---

**Your worker is ready to deploy RIGHT NOW!** 🚀

