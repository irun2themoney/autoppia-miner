# Chutes API Model Selection

## Current Model

**Primary**: `Qwen/Qwen2.5-7B-Instruct` ⭐ **FREE!**
**Fallback**: Other Qwen models, then GPT models

## Why Qwen2.5-7B-Instruct?

- **FREE**: No cost per request! 🎉
- **Good quality**: 7B parameter model, well-suited for web automation
- **Fast**: Efficient inference
- **Open source**: Apache 2.0 license, community supported
- **Saves quota**: Free models don't count against paid quota limits

## Available Models

Chutes API supports both free open-source models and paid models:

### FREE Models (Recommended!):
- **`Qwen/Qwen2.5-7B-Instruct`** ⭐ (Current) - FREE, fast, good quality
- **`Qwen/Qwen3-32B`** - FREE, better quality, larger model
- **`Qwen/Qwen2.5-32B-Instruct`** - FREE, best quality Qwen

### Paid Models:
- **`gpt-4o-mini`** - Fast, cheap, good quality
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
| **Qwen/Qwen2.5-7B-Instruct** | ⚡⚡⚡ | ⭐⭐⭐ | **FREE** | **⭐ CURRENT - Best value!** |
| Qwen/Qwen3-32B | ⚡⚡ | ⭐⭐⭐⭐ | **FREE** | Better quality, still free |
| Qwen/Qwen2.5-32B-Instruct | ⚡⚡ | ⭐⭐⭐⭐ | **FREE** | Best free option |
| gpt-4o-mini | ⚡⚡⚡ | ⭐⭐⭐ | 💰 | Paid alternative |
| gpt-4o | ⚡⚡ | ⭐⭐⭐⭐ | 💰💰 | Better quality (paid) |
| gpt-4 | ⚡ | ⭐⭐⭐⭐⭐ | 💰💰💰 | Complex reasoning (paid) |
| gpt-3.5-turbo | ⚡⚡⚡ | ⭐⭐ | 💰 | Speed critical (paid) |

## Recommendations

- **Use `Qwen/Qwen2.5-7B-Instruct`** (current) - FREE and good quality! 🎉
- **Upgrade to `Qwen/Qwen3-32B`** if you need better quality (still FREE!)
- **Only use paid models** if free models don't meet your needs
- **Save money** - Free models don't count against quota limits

## Testing Different Models

1. Update `.env` with new model
2. Restart API: `systemctl restart autoppia-api`
3. Test on IWA Playground
4. Compare success rates
5. Monitor quota usage

