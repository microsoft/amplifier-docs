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

### Debug & Observability

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `debug` | bool | `false` | Enable standard debug events |
| `raw_debug` | bool | `false` | Enable ultra-verbose raw API I/O logging |
| `debug_truncate_length` | int | 180 | Max string length in debug logs |

### Advanced

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `base_url` | string | `null` | Custom API endpoint (for proxies) |
| `beta_headers` | string or list | `null` | Beta feature headers (e.g., `context-1m-2025-08-07`) |

## Supported Models

| Model ID | Description | Context | Output |
|----------|-------------|---------|--------|
| `claude-sonnet-4-5` | Balanced performance (default) | 200K / 1M* | 64K |
| `claude-opus-4-6` | Most capable | 200K / 1M* | 128K |
| `claude-haiku-4-5` | Fastest, cheapest | 200K | 64K |

\* 1M context requires `enable_1m_context: true`

## Extended Thinking

Claude Sonnet and Opus support extended thinking (similar to OpenAI's reasoning):

```yaml
providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5
      # Extended thinking configured via ChatRequest.reasoning_effort or kwargs
```

**Via ChatRequest (portable):**
```python
ChatRequest(
    messages=[...],
    reasoning_effort="high"  # low, medium, or high
)
```

**Via kwargs (provider-specific):**
```python
provider.complete(
    request,
    extended_thinking=True,
    thinking_budget_tokens=32000
)
```

**Thinking modes:**
- `"enabled"`: Explicit budget (all models)
- `"adaptive"`: Model-controlled budget (Opus 4.6+ only)

**Temperature:** Automatically set to 1.0 when thinking enabled (required by API).

## Interleaved Thinking

When extended thinking is enabled, the provider automatically enables interleaved thinking (beta header: `interleaved-thinking-2025-05-14`). This allows Claude to think between tool calls, improving reasoning on complex multi-step tasks.

## Prompt Caching

Enabled by default for 90% cost reduction on cached tokens:

```yaml
config:
  enable_prompt_caching: true  # Default
```

Cache breakpoints automatically placed on:
- Last system message block
- Last tool definition
- Last message in conversation

## Native Web Search

Enable Anthropic's built-in web search tool:

```yaml
config:
  enable_web_search: true
  web_search_max_uses: 5  # Optional: limit searches per request
```

The web search tool appears as a native capability alongside your custom tools.

## Beta Features

Enable experimental features via beta headers:

```yaml
config:
  beta_headers: "context-1m-2025-08-07"  # Single header
  # OR
  beta_headers:
    - "context-1m-2025-08-07"
    - "future-feature-header"  # Multiple headers
```

**1M Context Window:**
```yaml
config:
  default_model: claude-sonnet-4-5
  enable_1m_context: true  # Automatically adds beta header
```

## Graceful Error Recovery

The provider automatically repairs incomplete tool call sequences:

**The Problem:** If tool results are missing from conversation history (due to context compaction bugs, parsing errors, or state corruption), the API rejects the request.

**The Solution:** The provider detects missing tool results and injects synthetic error results:

```python
# Broken: tool_use without matching tool_result
messages = [
    {"role": "assistant", "content": [{"type": "tool_use", "id": "toolu_123", ...}]},
    # MISSING: tool_result for toolu_123
    {"role": "user", "content": "Thanks"}
]

# Provider injects:
{
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": "toolu_123",
        "content": "[SYSTEM ERROR: Tool result missing]..."
    }]
}
```

This maintains session continuity and emits `provider:tool_sequence_repaired` events for monitoring.

## Debug Logging

**Standard debug** (`debug: true`):
- Emits `llm:request:debug` and `llm:response:debug` events
- Request/response summaries with message counts, usage stats
- Long values truncated to `debug_truncate_length`

**Raw debug** (`debug: true, raw_debug: true`):
- Emits `llm:request:raw` and `llm:response:raw` events
- Complete unmodified request/response objects
- Extreme log volume - use only for deep debugging

## Usage Metadata

Response metadata includes:

```python
{
    "input_tokens": 1234,
    "output_tokens": 567,
    "cache_read_tokens": 5000,      # Tokens read from cache
    "cache_write_tokens": 1234      # Tokens written to cache
}
```

## Environment Variables

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export ANTHROPIC_BASE_URL="https://api.anthropic.com"  # Optional: custom endpoint
```

## Examples

### Basic Usage

```yaml
providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5
      max_tokens: 4096
      temperature: 0.7
```

### High-Performance Configuration

```yaml
providers:
  - module: provider-anthropic
    config:
      default_model: claude-opus-4-6
      enable_1m_context: true
      enable_prompt_caching: true
      use_streaming: true
      max_retries: 5
      timeout: 600.0
```

### Debug Configuration

```yaml
providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5
      debug: true
      raw_debug: false  # Set true for raw API I/O
      debug_truncate_length: 180
```

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-provider-anthropic)**
