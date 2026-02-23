---
title: Events Orchestrator
description: Event-driven architecture with scheduler integration
---

# Events Orchestrator

Event-driven agent loop orchestrator with scheduler integration.

## Module ID

`loop-events`

## Installation

```yaml
session:
  orchestrator: {module: loop-events}

providers:
  - module: provider-anthropic
    source: git+https://github.com/microsoft/amplifier-module-provider-anthropic@main
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_iterations` | int | `-1` | Maximum iterations (-1 = unlimited) |
| `default_provider` | string | - | Default provider name to use |
| `extended_thinking` | bool | `false` | Enable extended thinking for compatible providers |
| `reasoning_effort` | string | - | Reasoning effort passed to ChatRequest (`low`/`medium`/`high`) |

## Behavior

Provides event-driven orchestration that:

- Trusts LLM decisions with optional scheduler veto/modification
- Emits events for observability and hook integration
- Falls back gracefully if schedulers veto tool calls
- Maintains all standard orchestrator functionality

## Execution Flow

1. Get user prompt
2. Loop while tool calls needed:
   - LLM selects tool to execute
   - Emit `tool:selecting` event (schedulers can veto or modify)
   - Execute selected tool (or modified tool if scheduler changed it)
   - Feed results back to LLM
3. Return final response

## Usage

```toml
[session]
orchestrator = "loop-events"
```

Perfect for:

- Advanced scheduling requirements
- Cost-optimized tool selection
- Custom decision-making pipelines

## Repository

**→ [GitHub](https://github.com/microsoft/amplifier-module-loop-events)**
