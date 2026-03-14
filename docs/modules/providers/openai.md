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
| `default_model` | string | `gpt-5.4` | Default model |
| `max_tokens` | integer | `4096` | Maximum output tokens |
| `temperature` | float | null | Sampling temperature; null = not sent (some models don't support it) |
| `reasoning` | string | null | Reasoning effort: `minimal\|low\|medium\|high`; null = not sent |
| `reasoning_summary` | string | `detailed` | Reasoning verbosity: `auto\|concise\|detailed` |
| `truncation` | string | `auto` | Automatic context management |
| `enable_state` | boolean | `false` | Enable stateful conversations |
| `debug` | boolean | `false` | Enable standard debug events |
| `raw_debug` | boolean | `false` | Enable ultra-verbose raw API I/O logging |
| `priority` | int | 100 | Provider priority for selection |
| `timeout` | float | 600.0 | API timeout in seconds |
| `max_retries` | int | 5 | Retry attempts before failing |
| `retry_jitter` | float | 0.2 | Randomness in retry delays (0.0-1.0) |
| `min_retry_delay` | float | 1.0 | Minimum delay between retries |
| `max_retry_delay` | float | 60.0 | Maximum delay between retries |

## Supported Models

| Model | Description |
|-------|-------------|
| `gpt-5.4` | GPT 5.4 (default) |
| `gpt-5.4-pro` | GPT 5.4 Pro |
| `gpt-5.1` | GPT 5.1 |
| `gpt-5.1-codex` | GPT-5.1 codex |
| `gpt-5-mini` | Smaller, faster GPT-5 |
| `gpt-5-nano` | Smallest GPT-5 variant |
| `o3-deep-research` | o3 Deep Research |
| `o4-mini-deep-research` | o4-mini Deep Research |

## Reasoning Configuration

Control the model's reasoning effort and output verbosity:

```yaml
providers:
  - module: provider-openai
    config:
      reasoning: "medium"  # minimal|low|medium|high
      reasoning_summary: "detailed"  # auto|concise|detailed
```

**Reasoning levels:**
- `minimal` - Quick responses, minimal reasoning
- `low` - Light reasoning for simple tasks
- `medium` - Balanced reasoning for most tasks
- `high` - Deep reasoning for complex problems

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

When set to `auto`, OpenAI automatically truncates older messages to fit within context limits.

## Tool Calling

The provider automatically detects and processes tool calls from the Responses API:

```yaml
providers:
  - module: provider-openai
    config:
      default_model: gpt-5.4
```

Tools declared in your configuration are available to the model automatically.

## Debug Events

Enable debug logging:

```yaml
providers:
  - module: provider-openai
    config:
      debug: true  # Standard debug events
      raw_debug: true  # Ultra-verbose raw API I/O
```

Events:
- `llm:request:debug` - Request summary
- `llm:response:debug` - Response summary
- `llm:request:raw` - Complete request params
- `llm:response:raw` - Complete response object

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
      default_model: gpt-5.4
      max_tokens: 4096
      temperature: 0.7
      reasoning: medium
      reasoning_summary: detailed
      truncation: auto
```
