---
title: loop-basic
description: Basic orchestrator with parallel tool execution and complete event emissions
---

# loop-basic Orchestrator

Basic agent loop orchestrator that provides the foundation for all Amplifier orchestration. Supports parallel tool execution and complete event emissions.

## Overview

The `loop-basic` orchestrator:

- Receives user prompts
- Calls the LLM provider
- Executes tool calls in parallel
- Adds results back to context
- Repeats until no more tool calls
- Returns final response

## Configuration

```yaml
session:
  orchestrator: loop-basic

orchestrators:
  - module: loop-basic
    source: git+https://github.com/microsoft/amplifier-module-loop-basic@main
    config:
      max_iterations: -1              # Maximum iterations (-1 = unlimited)
      default_provider: null          # Default provider name (optional)
      extended_thinking: false        # Enable extended thinking mode (default: false)
      reasoning_effort: null          # Reasoning effort level passed to the provider (optional)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_iterations` | integer | `-1` | Maximum loop iterations (`-1` = unlimited) |
| `default_provider` | string | `null` | Default provider name (uses first available if not set) |
| `extended_thinking` | boolean | `false` | Enable extended thinking mode for supported models |
| `reasoning_effort` | string | `null` | Reasoning effort level passed to the provider (provider-specific) |

## Behavior

### Agent Loop

```
1. Receive user prompt
2. Emit prompt:submit event (allows context injection)
3. Loop:
   a. Get messages from context
   b. Call provider.complete()
   c. Parse tool calls from response
   d. Execute all tool calls in parallel
   e. Add results to context
   f. Repeat from step 3
4. Emit prompt:complete event
5. Return final response
```

### Parallel Tool Execution

All tool calls from a single LLM response execute concurrently:

```python
# All tool calls execute at the same time
results = await asyncio.gather(*[
    execute_tool(call) for call in tool_calls
])
```

This reduces latency when the LLM requests multiple independent tools.

### Provider Selection

The orchestrator selects a provider using priority ordering:

```python
# Provider selected by priority (default_provider preference, then first available)
provider = self._select_provider(providers)
```

If `default_provider` is set, that provider is preferred. Otherwise, the first registered provider is used.

### Context Management

Messages flow through the context module:

```python
# Add user message
await context.add_message({"role": "user", "content": prompt})

# Get all messages for LLM
messages = await context.get_messages()

# Add assistant response
await context.add_message({"role": "assistant", "content": response})

# Add tool result
await context.add_tool_result(tool_id, result)
```

## Events

Emits all standard orchestrator events:

### Prompt Lifecycle
- `prompt:submit` - Before processing (hooks can inject context)
- `prompt:complete` - After final response

### Provider Lifecycle
- `provider:request` - Before LLM call
- `provider:response` - After LLM response
- `provider:error` - On LLM error

### Tool Lifecycle
- `tool:pre` - Before tool execution
- `tool:post` - After tool execution
- `tool:error` - On tool error

### Orchestrator Lifecycle
- `orchestrator:complete` - Orchestration finished

## Extended Thinking

When `extended_thinking: true`:

```python
response = await provider.complete(chat_request, extended_thinking=True)
```

Providers that support extended thinking (e.g., Anthropic Claude with thinking blocks) will use it. Others ignore the flag.

## Error Handling

### Provider Errors

On LLM error:
1. Emit `provider:error` event
2. Return error message to user
3. Exit loop

### Tool Errors

On tool execution error:
1. Emit `tool:error` event
2. Add error as tool result
3. Continue loop (LLM sees error and can recover)

### Iteration Limit

When `max_iterations` reached:
1. Stop loop
2. Return current response
3. Log warning

## Use Cases

### 1. Development and Testing

```yaml
session:
  orchestrator: loop-basic

orchestrators:
  - module: loop-basic
    config:
      max_iterations: 10  # Limit for safety during testing
```

Simple, predictable behavior for testing.

### 2. Production Workloads

```yaml
session:
  orchestrator: loop-basic

orchestrators:
  - module: loop-basic
    config:
      max_iterations: -1  # Unlimited
      extended_thinking: false
```

### 3. Extended Reasoning

```yaml
session:
  orchestrator: loop-basic

orchestrators:
  - module: loop-basic
    config:
      extended_thinking: true
      reasoning_effort: "high"
```

## Comparison with Other Orchestrators

| Feature | loop-basic | loop-streaming | loop-events |
|---------|------------|----------------|-------------|
| Tool execution | **Parallel** | Parallel | Sequential |
| Streaming output | No | **Yes** | No |
| Scheduler integration | No | No | **Yes** |
| Best for | **Testing/Production** | Interactive UIs | Multi-agent |

## Implementation Notes

- Tool calls execute in parallel using `asyncio.gather()`
- Provider selected by priority (default_provider preference, then first available)
- Context compaction handled automatically by context module
- Ephemeral injections cleared after each iteration
- Cancellation checked after each provider response

## See Also

- [loop-streaming](loop_streaming.md) - Streaming variant
- [loop-events](loop_events.md) - Event-driven variant with scheduler support
- [Event System](../../architecture/events/) - Canonical events reference
