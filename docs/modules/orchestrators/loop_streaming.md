---
title: Loop Streaming Orchestrator
description: Token-level streaming orchestration with parallel tool execution and extended thinking support
---

# Loop Streaming Orchestrator

> **Repository**: [`amplifier-module-loop-streaming`](https://github.com/microsoft/amplifier-module-loop-streaming)

Token-level streaming orchestration that delivers LLM responses in real-time for interactive applications.

## Contract

| Field | Value |
|-------|-------|
| **Module Type** | `orchestrator` |
| **Mount Point** | `orchestrator` |
| **Entry Point** | `amplifier_module_loop_streaming:mount` |

## Behavior

- Token-level streaming from provider
- Real-time response delivery via hooks
- **Parallel tool execution** — multiple tool calls execute concurrently
- Deterministic context updates — results added in original call order
- Interruptible generation
- Extended thinking support for compatible providers

## Configuration

```toml
[[orchestrators]]
module = "loop-streaming"
name = "streaming"
config = {
    max_iterations = -1,               # Maximum loop iterations (-1 = unlimited)
    extended_thinking = false,         # Enable extended thinking mode for supported models
    min_delay_between_calls_ms = 0,    # Minimum delay between provider calls in ms (0 = disabled)
    stream_delay = 0.0                 # Delay between streamed tokens in seconds (0.0 = no delay)
}
```

## Config Reference

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `max_iterations` | integer | `-1` | Maximum loop iterations (`-1` = unlimited) |
| `extended_thinking` | boolean | `false` | Enable extended thinking mode for supported models |
| `min_delay_between_calls_ms` | integer | `0` | Minimum delay between provider calls in milliseconds (`0` = disabled) |
| `stream_delay` | float | `0.0` | Delay between streamed tokens in seconds (artificial pacing; `0.0` = no delay) |

## Events Emitted

| Event | Description |
|-------|-------------|
| `execution:start` | Orchestrator execution began |
| `execution:end` | Orchestrator execution finished |
| `orchestrator:complete` | Loop completed (final event per `execute()` call) |
| `content_block:start` | Streaming block started |
| `content_block:delta` | Streaming token delta |
| `content_block:end` | Streaming block finished |

## Usage

### In a Bundle

```yaml
session:
  orchestrator:
    module: loop-streaming
    config:
      max_iterations: -1
      extended_thinking: false
```

### Observing Streaming Tokens

```python
from amplifier_core.events import CONTENT_BLOCK_DELTA

@coordinator.hooks.on(CONTENT_BLOCK_DELTA)
async def on_token(event_name, data):
    print(data.get("delta", ""), end="", flush=True)
```

### Limiting Iterations

```yaml
session:
  orchestrator:
    module: loop-streaming
    config:
      max_iterations: 5  # Stop after 5 agentic loop iterations
```

### Extended Thinking

```yaml
session:
  orchestrator:
    module: loop-streaming
    config:
      extended_thinking: true  # Requires provider with thinking support
```

## Perfect For

- Interactive CLI applications
- Web UIs with progressive rendering
- Long-form content generation
- Agentic loops with parallel tool execution

## Installation

```bash
amplifier module install loop-streaming
```

Or in a bundle:

```yaml
session:
  orchestrator:
    module: loop-streaming
    source: git+https://github.com/microsoft/amplifier-module-loop-streaming@main
```
