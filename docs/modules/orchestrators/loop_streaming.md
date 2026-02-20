---
title: Streaming Orchestrator
description: Token-level streaming for real-time response delivery
---

# Streaming Orchestrator

Token-level streaming orchestration for real-time response delivery.

## Module ID

`loop-streaming`

## Installation

```yaml
orchestrators:
  - module: loop-streaming
    source: git+https://github.com/microsoft/amplifier-module-loop-streaming@main
    config:
      buffer_size: 10
      max_iterations: -1
      timeout: 300
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `buffer_size` | int | `10` | Tokens to buffer before flush |
| `max_iterations` | int | `-1` | Maximum iterations (-1 = unlimited) |
| `timeout` | int | `300` | Timeout in seconds |
| `extended_thinking` | bool | `false` | Enable extended thinking for compatible providers |
| `min_delay_between_calls_ms` | int | `0` | Minimum delay between provider API calls (ms) |
| `reasoning_effort` | string | - | Reasoning effort passed to ChatRequest (`low`/`medium`/`high`) |

## Behavior

- **Token-level streaming** from provider
- **Real-time response delivery**
- **Parallel tool execution**: Multiple tool calls execute concurrently
- **Deterministic context updates**: Results added in original order
- **Progressive rendering**
- **Interruptible generation**

## Usage

```toml
[session]
orchestrator = "loop-streaming"
```

Perfect for:

- Interactive CLI applications
- Web UIs with progressive rendering
- Long-form content generation

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-loop-streaming)**
