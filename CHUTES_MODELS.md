# Chutes API Model Selection

## Current Model

**Primary**: `gpt-4o-mini`
**Fallback**: `gpt-4`, `gpt-3.5-turbo`

## Why gpt-4o-mini?

- **Fast**: Quick response times for real-time task processing
- **Cost-effective**: Lower cost per request (important with 5000/day quota)
- **Good enough**: Sufficient quality for web automation tasks
- **Reliable**: Stable and well-tested

## Available Models

Chutes API supports OpenAI-compatible models. Common options:

### Recommended for Web Automation:
- **`gpt-4o-mini`** ⭐ (Current) - Fast, cheap, good quality
- **`gpt-4o`** - Better quality, slightly slower
- **`gpt-4`** - Best quality, slower and more expensive
- **`gpt-3.5-turbo`** - Fastest, lower quality

### Other Options:
- **`claude-3-5-sonnet`** - Anthropic's Claude (if supported)
- **`claude-3-opus`** - Higher quality Claude (if supported)

## Changing the Model

Update `.env` file:

```env
CHUTES_MODEL=gpt-4o-mini  # Change to your preferred model
```

Or set environment variable:
```bash
export CHUTES_MODEL=gpt-4o
```

## Model Comparison

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| gpt-4o-mini | ⚡⚡⚡ | ⭐⭐⭐ | 💰 | **Current choice - balanced** |
| gpt-4o | ⚡⚡ | ⭐⭐⭐⭐ | 💰💰 | Better quality needed |
| gpt-4 | ⚡ | ⭐⭐⭐⭐⭐ | 💰💰💰 | Complex reasoning tasks |
| gpt-3.5-turbo | ⚡⚡⚡ | ⭐⭐ | 💰 | Speed critical, quality less important |

## Recommendations

- **Start with `gpt-4o-mini`** (current) - Good balance
- **Upgrade to `gpt-4o`** if you need better task understanding
- **Use `gpt-4`** only for complex tasks that require deep reasoning
- **Monitor quota usage** - Better models use more quota

## Testing Different Models

1. Update `.env` with new model
2. Restart API: `systemctl restart autoppia-api`
3. Test on IWA Playground
4. Compare success rates
5. Monitor quota usage

