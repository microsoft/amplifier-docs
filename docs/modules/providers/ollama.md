---
title: Ollama Provider
description: Local and cloud model integration via Ollama
---

# Ollama Provider

Integrates Ollama models (local or cloud) into Amplifier.

## Module ID

`provider-ollama`

## Installation

```yaml
providers:
  - module: provider-ollama
    source: git+https://github.com/microsoft/amplifier-module-provider-ollama@main
```

## Prerequisites

**Local Ollama:**
1. Install Ollama: `brew install ollama` (macOS) or `curl -fsSL https://ollama.com/install.sh | sh` (Linux)
2. Start server: `ollama serve`
3. Pull model: `ollama pull llama3.2:3b`

**Ollama Cloud:**
Set `host: https://ollama.com` and provide an API key via `OLLAMA_API_KEY`.

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `host` | string | `http://localhost:11434` | Ollama server URL; use `https://ollama.com` for Ollama Cloud |
| `api_key` | string | null | API key for Ollama Cloud (`$OLLAMA_API_KEY`); Bearer auth attached when set |
| `default_model` | string | auto | Default model; `gpt-oss:120b` for Ollama Cloud, `llama3.2:3b` for local |
| `max_tokens` | int | `4096` | Maximum tokens to generate |
| `temperature` | float | `0.7` | Generation temperature |
| `timeout` | float | `600.0` | Request timeout in seconds |
| `auto_pull` | boolean | `false` | Automatically pull missing models (local only; ignored for Ollama Cloud) |
| `raw` | boolean | `false` | Include raw API response data in output |
| `enable_thinking` | boolean | `true` | Enable thinking/reasoning for supported models |
| `num_ctx` | integer | `0` | Context window size override (0 = auto-detect from model) |
| `keep_alive` | string | — | Duration to keep model loaded in memory (e.g., `5m`, `-1` for indefinite) |

## Authentication

The provider uses a single, simple convention:

- **Local Ollama** (`host = "http://localhost:11434"`): no auth required.
- **Ollama Cloud** (`host = "https://ollama.com"`): set `api_key` or `OLLAMA_API_KEY`. Bearer auth is attached to every request.
- **Custom auth proxy** (any other URL with `api_key` set): the same `Authorization: Bearer <key>` header is attached.

```yaml
# Ollama Cloud
providers:
  - module: provider-ollama
    config:
      host: https://ollama.com
      api_key: ${OLLAMA_API_KEY}
```

Environment variables:
- `OLLAMA_HOST` - Override default Ollama server URL
- `OLLAMA_API_KEY` - API key for Ollama Cloud

## Supported Models

Any model available in Ollama:

- `llama3.2:3b` (small, fast)
- `llama3.2:1b` (tiny, fastest)
- `mistral` (7B)
- `mixtral` (8x7B)
- `codellama` (code generation)
- `deepseek-r1` (reasoning/thinking)
- `qwen3` (reasoning + tools)
- And more...

See: https://ollama.ai/library

## Features

### Thinking/Reasoning Support

The provider supports thinking/reasoning for compatible models like DeepSeek R1 and Qwen 3. When enabled, the model's internal reasoning is captured separately from the final response.

**Compatible models**:
- `deepseek-r1` - DeepSeek's reasoning model
- `qwen3` - Alibaba's Qwen 3 (with `think` parameter)
- `qwq` - Alibaba's QwQ reasoning model
- `phi4-reasoning` - Microsoft's Phi-4 reasoning variant

### Streaming

The provider supports streaming responses for real-time token delivery. When streaming is enabled, events are emitted as tokens arrive.

**Stream events**:
- `llm:stream:chunk` - Emitted for each content token
- `llm:stream:thinking` - Emitted for thinking tokens (when thinking enabled)

### Structured Output

The provider supports structured output using JSON schemas. This ensures the model's response conforms to a specific format.

### Tool Calling

Supports tool calling with compatible models. Tools are automatically formatted in Ollama's expected format (OpenAI-compatible).

**Automatic validation**: The provider validates tool call sequences and repairs broken chains. If a tool call is missing its result, a synthetic error result is inserted to maintain conversation integrity.

**Compatible models**:
- Llama 3.1+ (8B, 70B, 405B)
- Llama 3.2 (1B, 3B)
- Qwen 3
- Mistral Nemo
- And others with tool support

## Mixed local + cloud (multi-instance)

To use **both** local Ollama and Ollama Cloud in the same session, configure two provider instances using `instance_id`:

```toml
# Default local instance — keeps the natural mount name "ollama"
[[providers]]
module = "amplifier-module-provider-ollama"
[providers.config]
host = "http://localhost:11434"
auto_pull = true

# Second instance — explicit `instance_id` makes it addressable as "ollama-cloud"
[[providers]]
module = "amplifier-module-provider-ollama"
instance_id = "ollama-cloud"
[providers.config]
host = "https://ollama.com"
api_key = "${OLLAMA_API_KEY}"
```

A routing matrix can then target each independently:

```yaml
roles:
  reasoning:
    candidates:
      - provider: ollama-cloud
        model: gpt-oss:120b
      - provider: ollama
        model: "deepseek-r1:*"
  fast:
    candidates:
      - provider: ollama
        model: "llama3.2:*"
```

## Error Handling

The provider handles common scenarios gracefully:

- **Server offline**: Mounts successfully, fails on use with clear error
- **Model not found**: Pulls automatically (if auto_pull=true) or provides helpful error
- **Connection issues**: Clear error messages with troubleshooting hints
- **Timeout**: Configurable timeout with clear error when exceeded

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-provider-ollama)**
