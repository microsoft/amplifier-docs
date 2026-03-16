---
title: Ollama Provider
description: Local model integration
---

# Ollama Provider

Integrates locally-running Ollama models into Amplifier.

## Module ID

`provider-ollama`

## Installation

```yaml
providers:
  - module: provider-ollama
    source: git+https://github.com/microsoft/amplifier-module-provider-ollama@main
```

## Prerequisites

1. Install Ollama: `brew install ollama` (macOS)
2. Start server: `ollama serve`
3. Pull model: `ollama pull llama3.2:3b`

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `host` | string | `http://localhost:11434` | Ollama server URL |
| `default_model` | string | `llama3.2:3b` | Default model |
| `max_tokens` | int | `4096` | Maximum tokens to generate |
| `temperature` | float | `0.7` | Generation temperature |
| `timeout` | float | `600.0` | Request timeout in seconds |
| `debug` | boolean | `false` | Enable standard debug events |
| `raw_debug` | boolean | `false` | Enable ultra-verbose raw API I/O logging |
| `auto_pull` | boolean | `false` | Automatically pull missing models |

### Debug Configuration

**Standard Debug** (`debug: true`):
- Emits `llm:request:debug` and `llm:response:debug` events
- Contains request/response summaries with message counts, model info, usage stats
- Long values automatically truncated for readability
- Moderate log volume, suitable for development

**Raw Debug** (`debug: true, raw_debug: true`):
- Emits `llm:request:raw` and `llm:response:raw` events
- Contains complete, unmodified request params and response objects
- Extreme log volume, use only for deep provider integration debugging
- Captures the exact data sent to/from Ollama API before any processing

**Example**:
```yaml
providers:
  - module: provider-ollama
    config:
      debug: true      # Enable debug events
      raw_debug: true  # Enable raw API I/O capture
      default_model: llama3.2:3b
```

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

## Error Handling

The provider handles common scenarios gracefully:

- **Server offline**: Mounts successfully, fails on use with clear error
- **Model not found**: Pulls automatically (if auto_pull=true) or provides helpful error
- **Connection issues**: Clear error messages with troubleshooting hints
- **Timeout**: Configurable timeout with clear error when exceeded

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-provider-ollama)**
