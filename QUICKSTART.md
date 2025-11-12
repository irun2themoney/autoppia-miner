# Quick Start Guide

Get your Autoppia Worker up and running in minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) Docker and Docker Compose

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure

```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
# At minimum, set AUTOPPIA_API_KEY
```

## Step 3: Test

```bash
# Run tests to verify everything works
pytest tests/ -v

# Or run the worker directly
python worker.py
```

## Step 4: Run

### Option A: Direct Execution
```bash
python worker.py
```

### Option B: API Server
```bash
python api.py
# Server will start on http://localhost:8080
```

### Option C: Docker
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t autoppia-miner .
docker run -p 8080:8080 --env-file .env autoppia-miner
```

## Step 5: Test the API

Once the API server is running:

```bash
# Health check
curl http://localhost:8080/health

# Get metadata
curl http://localhost:8080/metadata

# Process a request
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d '{
    "task": "mine",
    "input_data": {
      "source": "test_source",
      "pattern": "test_pattern"
    }
  }'
```

## Next Steps

1. **Customize the worker**: Edit `worker.py` to add your specific logic
2. **Update configuration**: Modify `config.yaml` and `template.json`
3. **Add tests**: Extend `tests/test_worker.py` with your test cases
4. **Publish to Autoppia**: Follow the deployment guide in README.md

## Troubleshooting

### Import Errors
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### API Key Issues
- Verify `.env` file exists and contains `AUTOPPIA_API_KEY`
- Check that the API key is valid

### Port Already in Use
- Change the port in `api.py` or use `--port` flag with uvicorn
- Or stop the existing service on port 8080

### Docker Issues
- Ensure Docker is running
- Check Docker logs: `docker-compose logs`

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Visit [Autoppia Documentation](https://luxit.gitbook.io/autoppia-docs)
- Join Autoppia community channels

