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
| `throttle_threshold` | float | 0.02 | Pre-emptive throttle threshold (2% remaining capacity) |
| `throttle_delay` | float | 1.0 | Fallback throttle delay (seconds) |
| `overloaded_delay_multiplier` | float | 10.0 | Multiplier for 529 Overloaded errors |

### Debug Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `debug` | bool | `false` | Enable standard debug events |
| `raw_debug` | bool | `false` | Enable ultra-verbose raw API I/O logging |
| `debug_truncate_length` | int | 180 | Max string length in debug logs |

**Standard Debug** (`debug: true`):
- Emits `llm:request:debug` and `llm:response:debug` events
- Contains request/response summaries with message counts, model info, usage stats
- Moderate log volume, suitable for development

**Raw Debug** (`debug: true, raw_debug: true`):
- Emits `llm:request:raw` and `llm:response:raw` events
- Contains complete, unmodified request params and response objects
- Extreme log volume, use only for deep provider integration debugging
- Captures the exact data sent to/from Anthropic API before any processing

## Retry and Error Handling

The provider disables SDK built-in retries (`max_retries=0`) and manages retries itself via `amplifier_core.utils.retry.retry_with_backoff()`. This gives the provider full control over backoff timing, retry-after header honoring, and per-error-class delay scaling.

### Error Translation

SDK exceptions are translated to kernel errors before the retry loop sees them. All translations preserve the original exception as `__cause__` for debugging.

| SDK Exception | Condition | Kernel Error | Status | Retryable |
| --- | --- | --- | --- | --- |
| `RateLimitError` | 429 | `RateLimitError` | 429 | Yes |
| `OverloadedError` | 529 | `ProviderUnavailableError` | 529 | Yes (10× backoff) |
| `InternalServerError` | 5xx | `ProviderUnavailableError` | 5xx | Yes |
| `AuthenticationError` | 401 | `AuthenticationError` | 401 | No |
| `BadRequestError` | context length / too many tokens | `ContextLengthError` | 400 | No |
| `BadRequestError` | safety / content filter / blocked | `ContentFilterError` | 400 | No |
| `BadRequestError` | other | `InvalidRequestError` | 400 | No |
| `APIStatusError` | 403 | `AccessDeniedError` | 403 | No |
| `APIStatusError` | 404 | `NotFoundError` | 404 | No |
| `APIStatusError` | other non-5xx | `LLMError` | — | No |
| `asyncio.TimeoutError` | — | `LLMTimeoutError` | — | Yes |
| Other | — | `LLMError` | — | Yes |

### Backoff Formula

Each retry delay is computed as follows:

```
base_delay   = min_retry_delay × 2^(attempt - 1)
capped_delay = min(base_delay, max_retry_delay)
scaled_delay = capped_delay × delay_multiplier          # 1.0 for most errors, 10.0 for 529
final_delay  = max(scaled_delay, retry_after)            # server retry-after as floor
sleep        = final_delay ± (final_delay × jitter)      # randomised ± jitter fraction
```

**Example: 529 Overloaded (10× multiplier, defaults)**

| Attempt | base_delay | capped | ×10 | Sleep |
| --- | --- | --- | --- | --- |
| 1 | 1s | 1s | 10s | 10s |
| 2 | 2s | 2s | 20s | 20s |
| 3 | 4s | 4s | 40s | 40s |
| 4 | 8s | 8s | 80s | 80s |
| 5 | 16s | 16s | 160s | 160s |

Total wait ≈ 310s (~5 min) before the request is abandoned.

### Retry Configuration

```yaml
providers:
  - module: provider-anthropic
    config:
      max_retries: 5
      min_retry_delay: 1.0
      max_retry_delay: 60.0
      retry_jitter: 0.2
      overloaded_delay_multiplier: 10.0
```

### Events

A `provider:retry` event is emitted before each retry sleep with the following fields:

| Field | Description |
| --- | --- |
| `provider` | Provider name (`"anthropic"`) |
| `model` | Model being called |
| `attempt` | Current retry attempt number |
| `max_retries` | Configured maximum retries |
| `delay` | Computed sleep duration in seconds |
| `retry_after` | Server retry-after value (or `null`) |
| `error_type` | Kernel error class name |
| `error_message` | Error description |

## Beta Headers

Anthropic provides experimental features through beta headers. Enable these features by adding the `beta_headers` configuration field.

### Configuration

**Single beta header:**
```yaml
providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5
      beta_headers: "context-1m-2025-08-07"  # Enable 1M token context window
```

**Multiple beta headers:**
```yaml
providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5
      beta_headers:
        - "context-1m-2025-08-07"
        - "future-feature-header"
```

### 1M Token Context Window

Claude Sonnet 4.5 supports a 1M token context window when the `context-1m-2025-08-07` beta header is enabled:

```yaml
providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5
      beta_headers: "context-1m-2025-08-07"
      max_tokens: 8192  # Output tokens remain separate from context window
```

With this configuration:
- **Context window**: Up to 1M tokens of input (messages, tools, system prompt)
- **Output tokens**: Controlled by `max_tokens` (separate from context window)
- **Use case**: Process large codebases, extensive documentation, or long conversation histories

### Notes

- Beta features are experimental and subject to change
- Check [Anthropic's documentation](https://docs.anthropic.com) for available beta headers
- Beta headers are optional - existing configurations work unchanged
- Invalid beta headers will cause API errors (fail fast)
- Beta header usage is logged at initialization for observability

## Graceful Error Recovery

The provider implements automatic repair for incomplete tool call sequences:

**The Problem**: If tool results are missing from conversation history (due to context compaction bugs, parsing errors, or state corruption), the Anthropic API rejects the entire request, breaking the user's session.

**The Solution**: The provider automatically detects and repairs missing tool_results by injecting synthetic results:

1. **Repair before validation** - Detects missing tool_results and injects synthetic ones
2. **Make failures visible** - Synthetic results contain `[SYSTEM ERROR: Tool result missing]` messages
3. **Maintain conversation validity** - API accepts repaired messages, session continues
4. **Enable recovery** - LLM acknowledges error and can ask user to retry
5. **Provide observability** - Emits `provider:tool_sequence_repaired` event with repair details
6. **Validate remaining** - After repair, strict validation catches any remaining inconsistencies

**Example**:
```python
# Anthropic format (after _convert_messages)
messages = [
    {
        "role": "assistant",
        "content": [
            {"type": "tool_use", "id": "toolu_123", "name": "get_weather", "input": {...}}
        ]
    },
    # MISSING: {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_123", ...}]}
    {"role": "user", "content": "Thanks"}
]

# Provider repairs by injecting synthetic result:
# Either appends to existing user message or inserts new one
{
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": "toolu_123",
        "content": "[SYSTEM ERROR: Tool result missing]\n\nTool: get_weather\n..."
    }]
}
```

**Observability**: Repairs are logged as warnings and emit `provider:tool_sequence_repaired` events for monitoring.

**Philosophy**: This is **graceful degradation** following kernel philosophy - errors in other modules (context management) don't crash the provider or kill the user's session.

## Features

- Streaming support
- Tool use (function calling)
- Vision capabilities (on supported models)
- Token counting and management
- Message validation before API calls (defense in depth)

## Supported Models

- `claude-sonnet-4-5` - Claude Sonnet 4.5 (recommended, default)
- `claude-opus-4-6` - Claude Opus 4.6 (most capable)
- `claude-haiku-4-5` - Claude Haiku 4.5 (fastest, cheapest)

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-provider-anthropic)**
