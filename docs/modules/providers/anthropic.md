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
| `throttle_threshold` | float | 0.02 | Capacity threshold for pre-emptive throttling (0.02 = 2%) |
| `throttle_delay` | float | 1.0 | Fallback delay when throttling without reset timestamp |

### Extended Thinking

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `thinking_type` | string | `adaptive` | Thinking mode: `adaptive` or `enabled` |
| `thinking_budget_tokens` | int | (model default) | Token budget for thinking (when type is `enabled`) |
| `thinking_budget_buffer` | int | 4096 | Buffer tokens for response after thinking |

### Web Search

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `web_search_max_uses` | int | (none) | Limit number of searches per request |
| `web_search_user_location` | object | (none) | User location for location-aware results |

### Beta Headers

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `beta_headers` | string or list | (none) | Anthropic beta feature headers |

**Example:**

```yaml
providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5
      beta_headers: "context-1m-2025-08-07"  # Single header
      # OR
      beta_headers:
        - "context-1m-2025-08-07"
        - "interleaved-thinking-2025-05-14"
```

**Note**: The `enable_1m_context` boolean automatically adds the `context-1m-2025-08-07` beta header.

### Debug & Observability

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `debug` | bool | `false` | Enable standard debug events (`llm:request:debug`, `llm:response:debug`) |
| `raw_debug` | bool | `false` | Enable ultra-verbose raw API I/O logging (`llm:request:raw`, `llm:response:raw`) |
| `debug_truncate_length` | int | 180 | Maximum string length in debug logs |

## Supported Models

- `claude-sonnet-4-5` - Claude Sonnet 4.5 (recommended, default)
- `claude-opus-4-6` - Claude Opus 4.6 (most capable, 128K output)
- `claude-haiku-4-5` - Claude Haiku 4.5 (fastest, cheapest)

### Model Capabilities

| Family | Context | Max Output | 1M Context | Thinking | Adaptive Thinking |
|--------|---------|------------|------------|----------|-------------------|
| Opus 4.6+ | 200K (1M with beta) | 128K | ✓ | ✓ | ✓ |
| Sonnet 4.5+ | 200K (1M with beta) | 64K | ✓ | ✓ | ✗ |
| Haiku 4.5+ | 200K | 64K | ✗ | ✓ | ✗ |

## Features

### Streaming Support

Uses streaming API by default to support large context windows. Anthropic requires streaming for operations that may take > 10 minutes (e.g., 300k+ token contexts).

### Tool Calling

Full support for function calling with automatic validation and repair of broken tool call sequences.

### Extended Thinking

Supports Anthropic's extended thinking mode (equivalent to OpenAI's reasoning):

- **Adaptive mode**: Model controls its own thinking budget (Opus 4.6+ only)
- **Enabled mode**: Explicit token budget for thinking
- **Interleaved thinking**: Automatically enabled when extended thinking is active

### Prompt Caching

When enabled (default), automatically adds cache control markers to:
- Last system message block
- Last tool definition
- Last message in conversation

Provides 90% cost reduction on cached tokens.

### Native Web Search

When `enable_web_search: true`, adds Anthropic's native `web_search_20250305` tool for current information retrieval.

### Graceful Error Recovery

Automatically detects and repairs missing tool results in conversation history by injecting synthetic error results. Emits `provider:tool_sequence_repaired` events for monitoring.

## Events

### Standard Events

- `llm:request` - API call initiated (summary)
- `llm:response` - API response received (with usage and rate limit info)
- `provider:retry` - Retry attempt (with delay and error details)
- `provider:throttle` - Pre-emptive throttling triggered
- `provider:tool_sequence_repaired` - Tool call sequence repaired

### Debug Events

When `debug: true`:
- `llm:request:debug` - Full request with truncated values
- `llm:response:debug` - Full response with truncated values

When `debug: true` and `raw_debug: true`:
- `llm:request:raw` - Complete untruncated request params
- `llm:response:raw` - Complete untruncated response object

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-provider-anthropic)**
