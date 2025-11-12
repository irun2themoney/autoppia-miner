# Autoppia Miner - AI Worker

An Autoppia AI Worker for mining and processing tasks. This worker follows the Autoppia SDK patterns for framework-agnostic, privacy-preserving AI workers.

## Overview

This worker is built according to the [Autoppia Documentation](https://luxit.gitbook.io/autoppia-docs) and implements:

- **Framework-agnostic design**: Works with any AI framework
- **Privacy-preserving**: No data retention, encrypted data handling
- **Modular architecture**: Easy to extend and customize
- **Autoppia SDK compliant**: Ready for deployment on Autoppia marketplace

## Features

- **Data Mining**: Extract and process data from various sources
- **Data Processing**: Transform and analyze data
- **AI Generation**: Generate content using AI models
- **Health Monitoring**: Built-in health checks and metrics
- **RESTful API**: HTTP API for integration with Autoppia infrastructure

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/irun2themoney/autoppia-miner.git
cd autoppia-miner
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp env.example .env
# Edit .env with your configuration
```

## Configuration

The worker can be configured through:

1. **Environment variables** (`.env` file)
2. **Configuration file** (`config.yaml`)
3. **Template metadata** (`template.json`)

### Required Configuration

- `WORKER_NAME`: Name of your worker
- `WORKER_VERSION`: Version of your worker

### Optional Configuration

- `AUTOPPIA_API_KEY`: Your Autoppia API key (for Autoppia marketplace integration)
- `CHUTES_API_KEY`: Chutes API key for AI generation (recommended)
- `CHUTES_API_URL`: Chutes API base URL (default: "https://api.chutes.ai")
- `MODEL`: AI model to use (default: "gpt-4")
- `MAX_TOKENS`: Maximum tokens for responses (default: 1000)
- `TEMPERATURE`: Temperature for AI generation (default: 0.7)
- `LOG_LEVEL`: Logging level (default: "INFO")

**Note**: The worker uses Chutes API for AI generation tasks. Make sure to set `CHUTES_API_KEY` in your `.env` file for full functionality.

## Usage

### Running the Worker

**Direct execution**:
```bash
python worker.py
```

**API server mode**:
```bash
python api.py
# Or using uvicorn directly:
uvicorn api:app --host 0.0.0.0 --port 8080
```

### Using the Worker Programmatically

```python
from worker import AutoppiaWorker, WorkerRequest

# Initialize worker
worker = AutoppiaWorker()

# Create a request
request = WorkerRequest(
    task="mine",
    input_data={
        "source": "example_source",
        "pattern": "example_pattern"
    }
)

# Process the request
import asyncio
response = asyncio.run(worker.process(request))
print(response.result)
```

### API Endpoints

When running in API server mode:

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /metadata` - Worker metadata
- `POST /process` - Process a worker request
- `GET /metrics` - Worker metrics

**Example API request**:
```bash
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d '{
    "task": "mine",
    "input_data": {
      "source": "example_source",
      "pattern": "example_pattern"
    }
  }'
```

## Supported Tasks

### 1. Mine Task
Extract and mine data from sources.

```python
request = WorkerRequest(
    task="mine",
    input_data={
        "source": "data_source",
        "pattern": "extraction_pattern"
    }
)
```

### 2. Process Task
Process and transform data.

```python
request = WorkerRequest(
    task="process",
    input_data={
        "data": ["item1", "item2", "item3"]
    }
)
```

### 3. Generate Task
Generate content using AI via Chutes API.

```python
request = WorkerRequest(
    task="generate",
    input_data={
        "prompt": "Generate a summary",
        "model": "gpt-4",  # Optional, defaults to config
        "max_tokens": 1000,  # Optional
        "temperature": 0.7  # Optional
    }
)
```

**Using Chat Messages Format**:
```python
request = WorkerRequest(
    task="generate",
    input_data={
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Generate a summary"}
        ],
        "model": "gpt-4"
    }
)
```

The worker automatically uses Chutes API when `CHUTES_API_KEY` is configured. If not configured, it falls back to a placeholder response.

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run specific tests:

```bash
pytest tests/test_worker.py::TestAutoppiaWorker::test_mine_task -v
```

## Deployment

### Publishing to Autoppia Marketplace

1. **Prepare your template**:
   - Ensure `template.json` is properly configured
   - Update metadata and description
   - Add examples and documentation

2. **Test locally**:
   ```bash
   python worker.py
   pytest tests/ -v
   ```

3. **Publish via Autoppia Developer Studio**:
   - Log in to [Autoppia Developer Studio](https://app.autoppia.com)
   - Navigate to "Publish a Template"
   - Upload your template.json and worker files
   - Follow the publishing workflow

### Deployment Configuration

The `deployment.yaml` file defines:
- Resource requirements (CPU, memory)
- Scaling configuration
- Health check settings
- Network configuration
- Privacy and security settings

## Project Structure

```
autoppia-miner/
├── worker.py              # Main worker implementation
├── api.py                 # HTTP API server
├── utils.py               # Utility functions
├── config.yaml            # Worker configuration
├── template.json          # Template metadata for marketplace
├── deployment.yaml        # Deployment configuration
├── requirements.txt       # Python dependencies
├── setup.py               # Package setup
├── pytest.ini            # Pytest configuration
├── env.example           # Environment variables example
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── tests/                # Test suite
    ├── __init__.py
    ├── conftest.py
    └── test_worker.py
```

## Development

### Adding New Tasks

1. Add a new handler method in `AutoppiaWorker`:
```python
async def _handle_new_task(self, request: WorkerRequest) -> Dict[str, Any]:
    # Your implementation
    pass
```

2. Update the `process` method to route to your handler:
```python
elif request.task == "new_task":
    result = await self._handle_new_task(request)
```

3. Update `template.json` to include the new task in capabilities

4. Add tests in `tests/test_worker.py`

### Extending Configuration

1. Update `WorkerConfig` in `worker.py`
2. Update `config.yaml` schema
3. Update `template.json` configuration schema

## Privacy & Security

This worker is designed with privacy in mind:

- **No data retention**: Data is processed and not stored
- **Encrypted communication**: All API communication is encrypted
- **Privacy-preserving**: User data is handled according to Autoppia privacy standards
- **Configurable logging**: Log levels can be adjusted to minimize data exposure

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Resources

- [Autoppia Documentation](https://luxit.gitbook.io/autoppia-docs)
- [Autoppia Studio](https://app.autoppia.com)
- [Autoppia SDK](https://github.com/autoppia/autoppia-sdk)
- [IWA Benchmark](https://github.com/autoppia/autoppia_iwa)

## Support

- **Documentation**: [Autoppia Docs](https://luxit.gitbook.io/autoppia-docs)
- **Community**: Join Autoppia social networks
  - [Twitter](https://twitter.com/autoppia)
  - [GitHub](https://github.com/autoppia)
  - [Telegram](https://t.me/autoppia)

## Changelog

### v0.1.0
- Initial release
- Basic mining, processing, and generation tasks
- HTTP API server
- Health checks and metrics
- Test suite
