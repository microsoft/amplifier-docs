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
| `base_url` | string | `http://localhost:8000/v1` | vLLM server URL (`$VLLM_BASE_URL`) |
| `api_key` | string | `EMPTY` | API key for remote vLLM servers (`$VLLM_API_KEY`); ignored for local |
| `default_model` | string | `openai/gpt-oss-20b` | Model name from vLLM |
| `max_tokens` | int | `4096` | Maximum output tokens |
| `temperature` | float | null | Sampling temperature; null = not sent (some models don't support it) |
| `reasoning` | string | null | Reasoning effort: `minimal\|low\|medium\|high`; null = not sent |
| `reasoning_summary` | string | `detailed` | Summary verbosity: `auto\|concise\|detailed` |
| `truncation` | string | `auto` | Automatic context management |
| `enable_state` | boolean | `false` | Enable stateful conversations (requires vLLM config) |
| `timeout` | float | `600.0` | API timeout (seconds) |
| `priority` | int | 100 | Provider priority for selection |
| `raw` | boolean | `false` | Include raw API I/O in provider events |
| `max_retries` | int | 5 | Retry attempts before failing |
| `retry_jitter` | bool | `true` | Add randomness to retry delays |
| `min_retry_delay` | float | 1.0 | Minimum delay between retries |
| `max_retry_delay` | float | 60.0 | Maximum delay between retries |

## Features

- **Responses API only** - Optimized for reasoning models
- **Full reasoning support** - Automatic reasoning block separation
- **Tool calling** - Complete tool integration
- **Optional API key** - Bearer auth for remote vLLM servers; ignored for local

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

## Local vs remote

`base_url` is the **single source of truth** for whether this provider instance is local or remote. The provider URL-parses it once at construction; everything downstream (`is_remote` property, capability tagging) flows from that decision.

- **Local** — `base_url` resolves to `localhost`, `127.0.0.1`, `::1`, or `0.0.0.0`. Capability tag: `local`. No auth required (`api_key` is ignored if it is the placeholder `"EMPTY"`).
- **Remote** — anything else (LAN IP, public hostname, RunPod / Modal / Anyscale / Lambda Labs URL, or a vLLM-backed proxy). Capability tag: `remote`. Bearer auth is attached when `api_key` is set.

## Mixed local + remote (multi-instance)

To use **both** a local vLLM and a remote vLLM in the same session, configure two provider instances using `instance_id`:

```toml
# Default LOCAL instance — keeps the natural mount name "vllm"
[[providers]]
module = "amplifier-module-provider-vllm"
[providers.config]
base_url = "http://localhost:8000/v1"
default_model = "openai/gpt-oss-20b"

# Second instance — explicit `instance_id` makes it addressable as "vllm-remote"
[[providers]]
module = "amplifier-module-provider-vllm"
instance_id = "vllm-remote"
[providers.config]
base_url = "https://api.endpoints.anyscale.com/v1"
api_key = "${VLLM_API_KEY}"
default_model = "meta-llama/Llama-3.3-70B-Instruct"
```

A routing matrix can then target each independently:

```yaml
roles:
  reasoning:
    candidates:
      - provider: vllm-remote
        model: "meta-llama/Llama-3.3-70B-Instruct"
      - provider: vllm
        model: "openai/gpt-oss-20b"
  fast:
    candidates:
      - provider: vllm
        model: "openai/gpt-oss-20b"
```

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
