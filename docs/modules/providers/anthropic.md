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
| `default_model` | string | `claude-sonnet-4-5` | Default model |
| `max_tokens` | int | 64000 | Maximum response tokens |
| `temperature` | float | 0.7 | Sampling temperature |
| `timeout` | float | 300.0 | API timeout in seconds |
| `priority` | int | 100 | Provider priority for selection |

### Feature Toggles

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `use_streaming` | bool | `true` | Use streaming API (required for large contexts) |
| `enable_prompt_caching` | bool | `true` | Enable prompt caching (90% cost reduction on cached tokens) |
| `enable_web_search` | bool | `false` | Enable native web search tool |
| `enable_1m_context` | bool | `false` | Enable 1M token context window (Sonnet only) |
| `filtered` | bool | `true` | Filter to curated model list |

### Rate Limit & Retry

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_retries` | int | 5 | Total retry attempts before failing |
| `retry_jitter` | bool | `true` | Add ±20% randomness to delays |
| `max_retry_delay` | float | 60.0 | Maximum wait between retries (seconds) |
| `min_retry_delay` | float | 1.0 | Minimum delay if no retry-after header |

### Debug & Observability

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `debug` | bool | `false` | Enable request/response debug events |
| `raw_debug` | bool | `false` | Enable ultra-verbose raw API I/O logging |
| `debug_truncate_length` | int | 180 | Max string length in debug logs |

### Advanced

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `base_url` | string | `https://api.anthropic.com` | API base URL (for proxies/custom endpoints) |
| `beta_headers` | string/list | - | Beta feature headers to enable |

## Supported Models

| Model | Description |
|-------|-------------|
| `claude-opus-4-1` | Most capable |
| `claude-sonnet-4-5` | Balanced (recommended) |
| `claude-haiku-4-5` | Fastest |

### Model Capabilities

| Model | Tools | Thinking | Streaming | JSON Mode |
|-------|-------|----------|-----------|-----------|
| `claude-opus-4-1` | ✅ | ✅ | ✅ | ✅ |
| `claude-sonnet-4-5` | ✅ | ✅ | ✅ | ✅ |
| `claude-haiku-4-5` | ✅ | - | ✅ | ✅ |

## Features

### Extended Thinking

Claude Sonnet and Opus models support extended thinking for complex reasoning:

```yaml
providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5
      thinking_budget_tokens: 32000  # Token budget for thinking
      thinking_budget_buffer: 4096   # Buffer for response after thinking
```

When thinking is enabled, the provider automatically:
- Sets `temperature=1.0` (required by Anthropic)
- Adjusts `max_tokens` to accommodate thinking budget
- Enables interleaved thinking for multi-step tool use

### 1M Token Context Window

Claude Sonnet 4.5 supports extended context via beta header:

```yaml
providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5
      enable_1m_context: true  # Automatically sets beta header
```

Or manually with beta headers:

```yaml
providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5
      beta_headers: "context-1m-2025-08-07"
```

With 1M context enabled:
- **Context window**: Up to 1M tokens of input
- **Output tokens**: Controlled separately by `max_tokens`
- **Use case**: Large codebases, extensive documentation, long conversations

### Beta Headers

Enable experimental Anthropic features:

```yaml
# Single header
providers:
  - module: provider-anthropic
    config:
      beta_headers: "context-1m-2025-08-07"

# Multiple headers
providers:
  - module: provider-anthropic
    config:
      beta_headers:
        - "context-1m-2025-08-07"
        - "future-feature-header"
```

> **Note**: Beta features are experimental. Check [Anthropic's documentation](https://docs.anthropic.com) for available headers.

### Prompt Caching

Enabled by default. Reduces cost by up to 90% on repeated context:

```yaml
providers:
  - module: provider-anthropic
    config:
      enable_prompt_caching: true  # default
```

The provider automatically:
- Adds cache breakpoints to system messages
- Caches tool definitions
- Creates checkpoints at conversation history end

### Native Web Search

Enable Claude's built-in web search capability:

```yaml
providers:
  - module: provider-anthropic
    config:
      enable_web_search: true
      web_search_max_uses: 5        # Optional: limit searches per request
      web_search_user_location: ... # Optional: location-aware results
```

### Debug Logging

**Standard Debug** (`debug: true`):
- Emits `llm:request:debug` and `llm:response:debug` events
- Request/response summaries with message counts, model info, usage stats

**Raw Debug** (`debug: true, raw_debug: true`):
- Emits `llm:request:raw` and `llm:response:raw` events
- Complete, unmodified request params and response objects
- Use only for deep provider integration debugging

```yaml
providers:
  - module: provider-anthropic
    config:
      debug: true
      raw_debug: true  # Extreme verbosity
```

### Rate Limit Handling

The provider handles rate limits with configurable retry behavior:

```yaml
providers:
  - module: provider-anthropic
    config:
      max_retries: 5       # Retry attempts (default: 5)
      retry_jitter: true   # Spread load with ±20% delay variance
      max_retry_delay: 60  # Cap wait time at 60 seconds
```

**Behavior:**
- Honors `retry-after` headers from Anthropic
- Uses exponential backoff when header unavailable
- Emits `anthropic:rate_limit_retry` events during retries
- Emits `anthropic:rate_limited` when retries exhausted

### Graceful Error Recovery

The provider automatically repairs incomplete tool call sequences:

**Problem**: Missing tool results (from context compaction or parsing errors) cause API rejection.

**Solution**: Provider detects and injects synthetic error results:
1. Detects missing `tool_result` messages
2. Injects synthetic results with `[SYSTEM ERROR: Tool result missing]`
3. Maintains conversation validity
4. Emits `provider:tool_sequence_repaired` event for observability

## Observability Events

| Event | Description |
|-------|-------------|
| `llm:request` | Request summary (model, message count, thinking enabled) |
| `llm:response` | Response summary (usage, status, duration) |
| `llm:request:debug` | Full request payload (when debug=true) |
| `llm:response:debug` | Full response payload (when debug=true) |
| `llm:request:raw` | Raw API params (when raw_debug=true) |
| `llm:response:raw` | Raw API response (when raw_debug=true) |
| `anthropic:rate_limit_retry` | Rate limit retry attempt |
| `anthropic:rate_limited` | Rate limit exhausted after retries |
| `provider:tool_sequence_repaired` | Tool result repair performed |

## Usage

```bash
# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Use provider
amplifier provider use anthropic
amplifier run "Hello!"
```

## Provider Info

```python
# Capabilities returned by get_info()
capabilities = ["streaming", "tools", "thinking", "batch"]

# Default values
defaults = {
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 4096,
    "temperature": 0.7,
    "timeout": 300.0,
    "context_window": 200000,  # 1M when enable_1m_context=true
    "max_output_tokens": 64000,
}
```

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-provider-anthropic)**
