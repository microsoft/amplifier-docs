---
title: Basic Orchestrator
description: Sequential agent loop orchestration
---

# Basic Orchestrator

Reference implementation of sequential agent loop orchestration. This is the default orchestrator.

## Module ID

`loop-basic`

## Installation

```yaml
orchestrators:
  - module: loop-basic
    source: git+https://github.com/microsoft/amplifier-module-loop-basic@main
    config:
      max_iterations: -1
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_iterations` | int | `-1` | Maximum iterations (-1 = unlimited) |
| `extended_thinking` | bool | `false` | Enable extended thinking for compatible providers |
| `reasoning_effort` | string | - | Reasoning effort passed to ChatRequest (`low`/`medium`/`high`) |

## Behavior

- **Parallel tool execution**: Multiple tool calls execute concurrently
- **Deterministic context updates**: Results added in original order
- **Robust error handling**: Failures return error results, never crash
- **Event correlation**: `parallel_group_id` tracks related executions
- No streaming (see [loop-streaming](loop_streaming.md) for that)

## Usage

```toml
[session]
orchestrator = "loop-basic"
```

Perfect for:

- Development and testing
- Simple request/response workflows
- Batch processing

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-loop-basic)**
