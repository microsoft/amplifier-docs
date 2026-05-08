---
title: OpenAI Provider
description: GPT model integration
---

# OpenAI Provider

Integrates OpenAI's GPT models into Amplifier.

## Module ID

`provider-openai`

## Installation

```yaml
providers:
  - module: provider-openai
    source: git+https://github.com/microsoft/amplifier-module-provider-openai@main
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | string | `$OPENAI_API_KEY` | API key |
| `base_url` | string | null | Optional custom endpoint (`$OPENAI_BASE_URL`); null = OpenAI default |
| `default_model` | string | `gpt-5.5` | Default model |
| `max_tokens` | integer | `4096` | Maximum output tokens |
| `temperature` | float | null | Sampling temperature; null = not sent (some models don't support it) |
| `reasoning` | string | null | Reasoning effort: `none\|low\|medium\|high\|xhigh`; null = not sent |
| `reasoning_summary` | string | `detailed` | Reasoning verbosity: `auto\|concise\|detailed` |
| `truncation` | string | null | Automatic context management; null = omit field (use `"auto"` for legacy auto-drop behavior) |
| `enable_state` | boolean | `false` | Enable stateful conversations |
| `filtered` | boolean | `true` | Filter to curated model list by default |
| `enable_long_context` | boolean | `false` | Enable full context window (>272K tokens, 2x input / 1.5x output pricing) |
| `use_streaming` | boolean | `true` | Use streaming HTTP transport (prevents timeouts on large context requests) |
| `prompt_cache_key` | string | null | Per-conversation cache routing key for prompt caching |
| `prompt_cache_retention` | string | `"24h"` | Cache retention: `in_memory` (5-10 min) or `24h` (extended GPU-local KV storage) |
| `enable_response_chaining` | string/bool | `"auto"` | Response chaining for reasoning models: `auto`\|`true`\|`false` |
| `raw` | boolean | `false` | Include raw API payload in provider events |
| `priority` | int | 100 | Provider priority for selection |
| `timeout` | float | 600.0 | API timeout in seconds |
| `max_retries` | int | 5 | Retry attempts before failing |
| `retry_jitter` | bool | `true` | Add randomness to retry delays |
| `min_retry_delay` | float | 1.0 | Minimum delay between retries |
| `max_retry_delay` | float | 60.0 | Maximum delay between retries |
| `poll_interval` | float | 5.0 | Status check interval for background tasks in seconds (deep research) |
| `background_timeout` | float | 1800.0 | Maximum wait time for background tasks in seconds |

## Supported Models

| Model | Description |
|-------|-------------|
| `gpt-5.5` | GPT 5.5 (default) |
| `gpt-5.5-pro` | GPT 5.5 Pro |
| `gpt-5.4` | GPT 5.4 |
| `gpt-5.4-pro` | GPT 5.4 Pro |
| `gpt-5.3-codex` | GPT-5.3 codex |
| `gpt-5.2` | GPT 5.2 |
| `gpt-5.2-pro` | GPT 5.2 Pro |
| `gpt-5.1` | GPT 5.1 |
| `gpt-5.1-codex` | GPT-5.1 codex |
| `gpt-5-mini` | Smaller, faster GPT-5 |
| `o3-deep-research` | o3 Deep Research |
| `o4-mini-deep-research` | o4-mini Deep Research |

## Reasoning Configuration

Control the model's reasoning effort and output verbosity:

```yaml
providers:
  - module: provider-openai
    config:
      reasoning: "medium"  # none|low|medium|high|xhigh
      reasoning_summary: "detailed"  # auto|concise|detailed
```

**Reasoning levels:**
- `none` - No reasoning
- `low` - Light reasoning for simple tasks
- `medium` - Balanced reasoning for most tasks
- `high` - Deep reasoning for complex problems
- `xhigh` - Maximum reasoning effort (gpt-5.5-pro: medium/high/xhigh only)

**Summary verbosity:**
- `auto` - Model decides appropriate detail level
- `concise` - Brief reasoning summaries
- `detailed` - Verbose reasoning output (similar to Anthropic's thinking blocks)

## Stateful Conversations

Enable conversation persistence across requests:

```yaml
providers:
  - module: provider-openai
    config:
      enable_state: true
```

With state enabled, the provider tracks conversation history server-side.

## Truncation

Automatic context management to handle token limits:

```yaml
providers:
  - module: provider-openai
    config:
      truncation: "auto"  # auto|none
```

By default (`null`), the truncation field is omitted and OpenAI returns an explicit error when the context fills, allowing you to handle it explicitly. Set to `"auto"` to opt into OpenAI's legacy auto-drop behavior.

## Tool Calling

The provider automatically detects and processes tool calls from the Responses API:

```yaml
providers:
  - module: provider-openai
    config:
      default_model: gpt-5.5
```

Tools declared in your configuration are available to the model automatically.

## Debug Events

Enable raw payload logging:

```yaml
providers:
  - module: provider-openai
    config:
      raw: true  # Include raw API payload in provider events
```

Events:
- `llm:request` - Request details (includes raw payload when `raw: true`)
- `llm:response` - Response details (includes raw payload when `raw: true`)

## Environment Variables

```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_BASE_URL="https://custom-endpoint.com"  # Optional
```

## Example Configuration

```yaml
providers:
  - module: provider-openai
    source: git+https://github.com/microsoft/amplifier-module-provider-openai@main
    config:
      api_key: ${OPENAI_API_KEY}
      default_model: gpt-5.5
      max_tokens: 4096
      temperature: 0.7
      reasoning: medium
      reasoning_summary: detailed
```
