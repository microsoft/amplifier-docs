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
| `default_model` | string | `gpt-5.1-codex` | Default model |
| `max_tokens` | integer | `4096` | Maximum output tokens |
| `temperature` | float | null | Sampling temperature; null = not sent (some models don't support it) |
| `reasoning` | string | null | Reasoning effort: `minimal\|low\|medium\|high`; null = not sent |
| `reasoning_summary` | string | `detailed` | Reasoning verbosity: `auto\|concise\|detailed` |
| `truncation` | string | `auto` | Automatic context management |
| `enable_state` | boolean | `false` | Enable stateful conversations |
| `debug` | boolean | `false` | Enable standard debug events |
| `raw_debug` | boolean | `false` | Enable ultra-verbose raw API I/O logging |

## Supported Models

| Model | Description |
|-------|-------------|
| `gpt-5.1-codex` | GPT-5 optimized for code (default) |
| `gpt-5.1` | Latest GPT-5 model |
| `gpt-5-mini` | Smaller, faster GPT-5 |
| `gpt-5-nano` | Smallest GPT-5 variant |
| `o3-deep-research` | o3 Deep Research |
| `o4-mini-deep-research` | o4-mini Deep Research |

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-provider-openai)**
