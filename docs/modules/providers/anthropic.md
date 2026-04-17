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
| `enable_1m_context` | bool | `true` | Enable 1M token context window (Sonnet and Opus only) |
| `filtered` | bool | `true` | Filter to curated model list |
| `beta_headers` | string/list | (none) | Anthropic beta header(s) for experimental features |

### Rate Limit & Retry

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_retries` | int | 5 | Total retry attempts before failing |
| `retry_jitter` | bool/float | `true` | Jitter fraction (0.0–1.0). Also accepts `true` (→ 0.2) or `false` (→ 0.0) for backward compatibility |
| `max_retry_delay` | float | 60.0 | Maximum wait between retries (seconds) |
| `min_retry_delay` | float | 1.0 | Minimum delay if no retry-after header |
| `overloaded_delay_multiplier` | float | 10.0 | Multiplier applied to delays for 529 Overloaded errors |
| `throttle_threshold` | float | 0.02 | Pre-emptive throttle trigger (2% capacity remaining) |
| `throttle_delay` | float | 1.0 | Throttle delay when approaching limits (seconds) |
| `max_concurrent_requests` | int | 5 | Process-wide in-flight API call limit (0 to disable) |
| `rate_limit_state_path` | string | `~/.amplifier/rate-limit-state.json` | Path for cross-process rate-limit state sharing (empty string to disable) |

### Debug Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `raw` | bool | `false` | Include raw payload in provider events |

### Overload Fallback

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `fallback_on_overload` | bool | `false` | Temporarily downgrade to a lower-tier model when a higher-tier model stays overloaded |
| `fallback_retry_count` | int | 1 | Overload retries before triggering downgrade |
| `fallback_cooldown_seconds` | float | 1800.0 | Duration (seconds) the downgrade window stays active before retrying the higher model |
| `fallback_sonnet_model` | string | `claude-sonnet-4-6` | Model to use when Opus is overloaded |
| `fallback_haiku_model` | string | `claude-haiku-4-5` | Model to use when Sonnet is overloaded |
| `persist_fallback_state` | bool | `false` | Persist temporary downgrade state across separate Amplifier processes |
| `fallback_state_path` | string | `~/.amplifier/anthropic-fallback-state.json` | Path for cross-process fallback state file (only used when `persist_fallback_state` is `true`) |

## Supported Models

| Model | Description |
|-------|-------------|
| `claude-sonnet-4-5` | Claude Sonnet 4.5 (recommended, default) |
| `claude-opus-4-6` | Claude Opus 4.6 (most capable) |
| `claude-haiku-4-5` | Claude Haiku 4.5 (fastest, cheapest) |

## Extended Thinking

Enable extended thinking for complex reasoning tasks:

```yaml
providers:
  - module: provider-anthropic
    config:
      default_model: claude-sonnet-4-5
```

Then in your request:

```python
request = ChatRequest(
    model="claude-sonnet-4-5",
    messages=[...],
    enable_thinking=True
)
```

The response will include thinking blocks showing the model's reasoning process.

When extended thinking is requested alongside tools, the provider automatically adds the `interleaved-thinking-2025-05-14` beta header so thinking blocks and tool calls can appear in the same turn.

## Prompt Caching

Anthropic's prompt caching reduces costs by 90% for repeated content. Enable it:

```yaml
providers:
  - module: provider-anthropic
    config:
      enable_prompt_caching: true
```

The provider automatically marks eligible content for caching based on message structure.

## Web Search

Enable native web search (Claude 4+ models only):

```yaml
providers:
  - module: provider-anthropic
    config:
      enable_web_search: true
```

The model can then search the web directly during conversations.

## Beta Headers

Anthropic provides experimental features through beta headers. Enable these features by adding the `beta_headers` configuration field.

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

Notes:
- Beta features are experimental and subject to change
- Check [Anthropic's documentation](https://docs.anthropic.com) for available beta headers
- Invalid beta headers will cause API errors (fail fast)
- Beta header usage is logged at initialization for observability

## Rate Limit Management

The provider tracks rate limits from response headers and pre-emptively throttles when approaching limits:

```yaml
providers:
  - module: provider-anthropic
    config:
      throttle_threshold: 0.02  # Throttle at 2% capacity remaining
      throttle_delay: 1.0  # Fallback sleep when no reset timestamp available
```

Events:
- `provider:throttle` - Emitted when pre-emptive throttling occurs
- `provider:retry` - Emitted before each retry attempt

## Overload Fallback

When `fallback_on_overload` is enabled, the provider temporarily routes requests to a lower-tier model if the higher-tier model remains overloaded after `fallback_retry_count` attempts. The downgrade window stays active for `fallback_cooldown_seconds` before automatically retrying the higher model.

```yaml
providers:
  - module: provider-anthropic
    config:
      fallback_on_overload: true
      fallback_retry_count: 1
      fallback_cooldown_seconds: 1800
```

Events:
- `provider:fallback_open` - Emitted when a temporary downgrade window opens
- `provider:fallback_active` - Emitted on each request served through an active downgrade window

## Retry Configuration

```yaml
providers:
  - module: provider-anthropic
    config:
      max_retries: 5
      min_retry_delay: 1.0
      max_retry_delay: 60.0
      retry_jitter: 0.2
```

The provider uses exponential backoff with jitter and honors `retry-after` headers from the API.

## Error Handling

The provider translates Anthropic SDK exceptions to kernel errors:

| SDK Exception | Condition | Kernel Error | Retryable |
|--------------|-----------|--------------|-----------|
| `RateLimitError` | 429 | `RateLimitError` | Yes |
| `OverloadedError` | 529 | `ProviderUnavailableError` | Yes (10× backoff) |
| `APIStatusError` | 5xx (status >= 500) | `ProviderUnavailableError` | Yes |
| `AuthenticationError` | 401 | `AuthenticationError` | No |
| `BadRequestError` | context length / too many tokens | `ContextLengthError` | No |
| `BadRequestError` | safety / content filter / blocked | `ContentFilterError` | No |
| `BadRequestError` | other | `InvalidRequestError` | No |
| `APIStatusError` | 403 (Cloudflare HTML challenge) | `ProviderUnavailableError` | Yes |
| `APIStatusError` | 403 | `AccessDeniedError` | No |
| `APIStatusError` | 404 | `NotFoundError` | No |
| `APIStatusError` | other non-5xx | `LLMError` | No |
| `asyncio.TimeoutError` | — | `LLMTimeoutError` | Yes |
| Other | — | `LLMError` | Yes |

The provider distinguishes Cloudflare bot-challenge 403 responses (HTML body, no JSON) from real API 403s. Cloudflare challenges are treated as transient and retried; real 403s surface as `AccessDeniedError`.

Events:
- `provider:cloudflare_challenge` - Emitted when a Cloudflare bot challenge is detected on a 403 response

## Graceful Error Recovery

The provider automatically detects and repairs broken tool call sequences before sending requests to the API.

**The Problem**: If tool results are missing from conversation history (due to context compaction bugs, parsing errors, or state corruption), the Anthropic API rejects the entire request.

**The Solution**: The provider scans messages for tool calls that have no corresponding tool result. For each missing result it injects a synthetic error result before validation:

```python
{
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": "toolu_123",
        "content": "[SYSTEM ERROR: Tool result missing]\n\nTool: get_weather\n..."
    }]
}
```

The LLM receives a complete, valid message sequence, acknowledges the error, and can ask the user to retry the failed operation.

Events:
- `provider:tool_sequence_repaired` - Emitted when one or more synthetic tool results are injected, with details of the repaired tool IDs

## Debug Events

The provider emits events on every request and response. Enable the `raw` option to include the complete unmodified API payload in those events:

```yaml
providers:
  - module: provider-anthropic
    config:
      raw: true  # Include raw API payload in provider events
```

Events:
- `llm:request` - Request details (message counts, model, params; includes raw payload if `raw: true`)
- `llm:response` - Response details (usage, stop reason; includes raw payload if `raw: true`)

## Environment Variables

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
export ANTHROPIC_BASE_URL="https://api.anthropic.com"  # Optional: override API endpoint
```

## Example Configuration

```yaml
providers:
  - module: provider-anthropic
    source: git+https://github.com/microsoft/amplifier-module-provider-anthropic@main
    config:
      api_key: ${ANTHROPIC_API_KEY}
      default_model: claude-sonnet-4-5
      max_tokens: 8192
      temperature: 1.0
      enable_prompt_caching: true
      enable_web_search: false
      max_retries: 5
      retry_jitter: 0.2
```
