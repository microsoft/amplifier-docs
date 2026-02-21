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
orchestrators:
  - module: loop-events
    source: git+https://github.com/microsoft/amplifier-module-loop-events@main
```

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

## Configuration

```toml
[session]
orchestrator = "loop-events"
context = "context-simple"

[[providers]]
module = "provider-anthropic"
name = "claude"

[[hooks]]
module = "hooks-scheduler-heuristic"

[[hooks]]
module = "hooks-scheduler-cost-aware"
config = { cost_weight = 0.6, latency_weight = 0.4 }
```

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
