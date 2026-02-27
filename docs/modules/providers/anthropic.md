---
title: Anthropic Provider
description: Claude model integration
---

# Anthropic Provider

Integrates Anthropic's Claude models into Amplifier. Supports streaming, tool calling, extended thinking, and ChatRequest format.

## Module ID

`provider-anthropic`

## Installation

```yaml
providers:
  - module: provider-anthropic
    source: git+https://github.com/microsoft/amplifier-module-provider-anthropic@main
    config:
      default_model: claude-sonnet-4-5
```

## Configuration

### Core Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | string | `$ANTHROPIC_API_KEY` | API authentication key |
| `base_url` | string | (none) | Custom API endpoint (for proxies, local APIs) |
| `default_model` | string | `claude-sonnet-4-5` | Default model |
| `max_tokens` | int | 64000 | Maximum response tokens |
| `temperature` | float | 0.7 | Sampling temperature |
| `timeout` | float | 600.0 | API timeout in seconds |
| `priority` | int | 100 | Provider priority for selection |

### Feature Toggles

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `use_streaming` | bool | `true` | Use streaming API (required for large contexts) |
| `enable_prompt_caching` | bool | `true` | Enable prompt caching (90% cost reduction on cached tokens) |
| `enable_web_search` | bool | `false` | Enable native web search tool |
| `enable_1m_context` | bool | `false` | Enable 1M token context window (Sonnet and Opus only) |
| `filtered` | bool | `true` | Filter to curated model list |

### Rate Limit & Retry

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_retries` | int | 5 | Total retry attempts before failing |
| `retry_jitter` | float | 0.2 | Randomness to add to delays (0.0-1.0) |
| `max_retry_delay` | float | 60.0 | Maximum wait between retries (seconds) |
| `min_retry_delay` | float | 1.0 | Minimum delay if no retry-after header |
| `throttle_threshold` | float | 0.02 | Capacity threshold for pre-emptive throttling (2%) |
| `throttle_delay` | float | 1.0 | Fallback delay when no reset timestamp |

### Debug Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `debug` | bool | `false` | Enable standard debug events |
| `raw_debug` | bool | `false` | Enable ultra-verbose raw API I/O logging |
| `debug_truncate_length` | int | 180 | Max string length in debug logs |

### Beta Headers

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `beta_headers` | string or list | (none) | Anthropic beta feature headers |

## Supported Models

- `claude-sonnet-4-5` - Claude Sonnet 4.5 (recommended, default)
- `claude-opus-4-6` - Claude Opus 4.6 (most capable)
- `claude-haiku-4-5` - Claude Haiku 4.5 (fastest, cheapest)

## Features

### Streaming Support

Streaming is enabled by default (`use_streaming: true`) and is required for large context windows. Anthropic requires streaming for operations that may take > 10 minutes.

### Prompt Caching

Enabled by default (`enable_prompt_caching: true`). Reduces cost by 90% on cached tokens.

**How it works:**
- Cache breakpoints added to last system message and last tool definition
- Subsequent requests with identical prefixes reuse cached tokens
- Automatic cache management by Anthropic API

### Native Web Search

Enable Claude's built-in web search capability:

```yaml
config:
  enable_web_search: true
  web_search_max_uses: 5  # Optional: limit searches per request
```

### 1M Context Window

Enable 1M token context window for Sonnet 4.5 and Opus 4.6:

```yaml
config:
  enable_1m_context: true
  # Automatically sets beta_headers: "context-1m-2025-08-07"
```

**Note:** This uses Anthropic's beta header `context-1m-2025-08-07`.

### Extended Thinking

Support for Claude's extended thinking (reasoning) mode:

```yaml
# Via config
config:
  thinking_type: "adaptive"  # or "enabled"
  thinking_budget_tokens: 32000

# Or via runtime request
request = ChatRequest(
    messages=[...],
    reasoning_effort="high"  # Portable interface
)
```

### Beta Headers

Enable experimental Anthropic features:

```yaml
# Single header
config:
  beta_headers: "context-1m-2025-08-07"

# Multiple headers
config:
  beta_headers:
    - "context-1m-2025-08-07"
    - "interleaved-thinking-2025-05-14"
```

Available beta headers:
- `context-1m-2025-08-07` - 1M token context window
- `interleaved-thinking-2025-05-14` - Thinking between tool calls

## Rate Limiting

### Automatic Retry

The provider uses exponential backoff with jitter for rate limit (429) and server (5xx) errors:

```yaml
config:
  max_retries: 5           # Retry attempts (default: 5)
  retry_jitter: 0.2        # Randomness in delays (default: 0.2)
  min_retry_delay: 1.0     # Minimum delay (default: 1.0s)
  max_retry_delay: 60.0    # Maximum delay (default: 60.0s)
```

### Pre-emptive Throttling

When rate limit capacity falls below threshold, the provider automatically throttles requests:

```yaml
config:
  throttle_threshold: 0.02  # Throttle at 2% remaining (default)
  throttle_delay: 1.0       # Fallback delay if no reset time
```

**How it works:**
- Tracks rate limit headers from every response
- Monitors three dimensions: requests, input tokens, output tokens
- Injects delay when most constrained dimension falls below threshold
- Emits `provider:throttle` event for observability

## Debugging

### Standard Debug

Enable summary logging with moderate detail:

```yaml
config:
  debug: true
```

Emits:
- `llm:request:debug` - Request summaries with truncated values
- `llm:response:debug` - Response summaries with usage stats

### Raw Debug

Enable complete API I/O logging:

```yaml
config:
  debug: true
  raw_debug: true
```

Emits:
- `llm:request:raw` - Complete unmodified request params
- `llm:response:raw` - Complete unmodified response objects

**Warning:** Extreme log volume. Use only for deep debugging.

## Graceful Error Recovery

The provider automatically repairs incomplete tool call sequences:

**The Problem**: Missing tool results (from context bugs) cause API rejection.

**The Solution**: Automatic detection and synthetic result injection.

**How it works:**
1. Detects missing tool_results before API call
2. Injects synthetic results with `[SYSTEM ERROR: Tool result missing]` message
3. API accepts repaired messages, session continues
4. LLM acknowledges error and can ask user to retry
5. Emits `provider:tool_sequence_repaired` event

**Observability**: Repairs logged as warnings with tool call IDs.

## Environment Variables

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Usage Example

```python
from amplifier_core import AmplifierSession

config = {
    "session": {
        "orchestrator": "loop-basic",
        "context": "context-simple"
    },
    "providers": [{
        "module": "provider-anthropic",
        "config": {
            "api_key": "your-key",
            "default_model": "claude-sonnet-4-5",
            "enable_prompt_caching": True
        }
    }]
}

async with AmplifierSession(config=config) as session:
    response = await session.execute("Hello!")
    print(response)
```

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-provider-anthropic)**
