---
title: vLLM Provider
description: Self-hosted LLMs via Responses API
---

# vLLM Provider

Integrates vLLM's OpenAI-compatible Responses API for local/self-hosted LLMs.

## Module ID

`provider-vllm`

## Installation

```yaml
providers:
  - module: provider-vllm
    source: git+https://github.com/microsoft/amplifier-module-provider-vllm@main
    config:
      base_url: "http://192.168.128.5:8000/v1"
      default_model: openai/gpt-oss-20b
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `base_url` | string | (required) | vLLM server URL |
| `default_model` | string | `openai/gpt-oss-20b` | Model name from vLLM |
| `max_tokens` | int | `4096` | Maximum output tokens |
| `temperature` | float | null | Sampling temperature; null = not sent (some models don't support it) |
| `reasoning` | string | null | Reasoning effort: `minimal\|low\|medium\|high`; null = not sent |
| `reasoning_summary` | string | `detailed` | Summary verbosity: `auto\|concise\|detailed` |
| `truncation` | string | `auto` | Automatic context management |
| `enable_state` | boolean | `false` | Enable stateful conversations (requires vLLM config) |
| `timeout` | float | `600.0` | API timeout (seconds) |
| `priority` | int | 100 | Provider priority for selection |
| `debug` | boolean | `false` | Enable standard debug events |
| `raw_debug` | boolean | `false` | Enable ultra-verbose raw API I/O logging |
| `debug_truncate_length` | int | 180 | Max string length in debug logs |
| `max_retries` | int | 5 | Retry attempts before failing |
| `retry_jitter` | float | 0.2 | Randomness in retry delays (0.0-1.0) |
| `min_retry_delay` | float | 1.0 | Minimum delay between retries |
| `max_retry_delay` | float | 60.0 | Maximum delay between retries |

## Features

- **Responses API only** - Optimized for reasoning models
- **Full reasoning support** - Automatic reasoning block separation
- **Tool calling** - Complete tool integration
- **No API key required** - Works with local vLLM servers
- **OpenAI-compatible** - Uses OpenAI SDK under the hood

## vLLM Server Setup

```bash
# Start vLLM server
vllm serve openai/gpt-oss-20b \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 2
```

**Requirements:**

- vLLM version: ≥0.10.1
- Any model compatible with vLLM (gpt-oss, Llama, Qwen, etc.)

## Usage

```bash
# Configure in profile
providers:
  - module: provider-vllm
    config:
      base_url: "http://localhost:8000/v1"
      default_model: "openai/gpt-oss-20b"
      reasoning: "high"
```

## Debugging

```yaml
config:
  debug: true        # Summary logging
  raw_debug: true    # Complete API I/O
```

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-provider-vllm)**
