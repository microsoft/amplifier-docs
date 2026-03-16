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

## vLLM Server Setup

This provider requires a running vLLM server:

```bash
# Start vLLM server (basic)
vllm serve openai/gpt-oss-20b \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 2

# For production (recommended - full config in /etc/vllm/model.env)
sudo systemctl start vllm
```

**Server requirements:**
- vLLM version: ≥0.10.1 (tested with 0.10.1.1)
- Responses API: Automatically available (no special flags needed)
- Model: Any model compatible with vLLM (gpt-oss, Llama, Qwen, etc.)

## Architecture

This provider uses the **OpenAI SDK** with a custom `base_url` pointing to your vLLM server. Since vLLM implements the OpenAI-compatible Responses API, the integration is clean and direct.

**Response flow:**
```
ChatRequest → VLLMProvider.complete() → AsyncOpenAI.responses.create() →
→ vLLM Server → Response → Content blocks (Thinking + Text + ToolCall) → ChatResponse
```

## Token Accounting

**For GPT-OSS models**: Token accounting is automatic but requires vocab files.

**How it works**:
- First use: Automatically downloads vocab files to `~/.amplifier/cache/vocab/`
- Subsequent uses: Uses cached files
- No manual setup needed if you have internet access

**What's computed**:
- **Input tokens**: Accurate count using Harmony's tokenization (matches model training format)
- **Output tokens**: Approximate count based on visible output text
- **Limitation**: Output count doesn't include hidden reasoning channels (REST API limitation)

**If auto-download fails** (offline/air-gapped):

```bash
# Manual setup for offline environments
mkdir -p ~/.amplifier/cache/vocab

# Download vocab files (on a machine with internet)
curl -sS -o ~/.amplifier/cache/vocab/o200k_base.tiktoken \
  https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken

curl -sS -o ~/.amplifier/cache/vocab/cl100k_base.tiktoken \
  https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken

# Transfer ~/.amplifier/cache/vocab/ directory to offline machine
# Then set environment variable:
export TIKTOKEN_ENCODINGS_BASE=~/.amplifier/cache/vocab
```

## Troubleshooting

### Connection refused

**Problem**: Cannot connect to vLLM server

**Solution**:
```bash
# Check vLLM service status
sudo systemctl status vllm

# Verify server is listening
curl http://192.168.128.5:8000/health

# Check logs
sudo journalctl -u vllm -n 50
```

### Tool calling not working

**Problem**: Model responds with text instead of calling tools

**Verification**:
- ✅ vLLM version ≥0.10.1
- ✅ Using Responses API (not Chat Completions)
- ✅ Tools defined in request

**Note**: Tool calling works via Responses API without special vLLM flags. If it's not working, check the model supports tool calling.

### No reasoning blocks

**Problem**: Responses don't include reasoning/thinking

**Check**:
- Is `reasoning` parameter set in config? (`minimal|low|medium|high`)
- Is the model a reasoning model? (gpt-oss supports reasoning)
- Check raw debug logs to see if reasoning is in API response

### Token usage shows zeros

**Check logs for**:
- `[TOKEN_ACCOUNTING] Downloading Harmony vocab files to ~/.amplifier/cache/vocab/...` (first use)
- `[TOKEN_ACCOUNTING] Loaded Harmony GPT-OSS encoder` (success)
- `[TOKEN_ACCOUNTING] Injected usage: input=X, output=Y` (active)

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-provider-vllm)**
