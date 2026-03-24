---
title: loop-basic
description: Basic orchestrator with complete event emissions
---

# loop-basic Orchestrator

Reference implementation of sequential agent loop orchestration with complete event emissions.

## Overview

The `loop-basic` orchestrator provides a straightforward request-response loop:

1. Receive user prompt
2. Get LLM completion
3. Execute tool calls sequentially
4. Repeat until final response

This orchestrator emits all canonical events for full observability.

## Configuration

```yaml
session:
  orchestrator: loop-basic

orchestrators:
  - module: loop-basic
    source: git+https://github.com/microsoft/amplifier-module-loop-basic@main
    config:
      max_iterations: -1              # Maximum iterations (-1 = unlimited)
      extended_thinking: false        # Enable extended thinking mode (default: false)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_iterations` | integer | `-1` | Maximum loop iterations (`-1` = unlimited) |
| `extended_thinking` | boolean | `false` | Enable extended thinking mode for supported models |

## Behavior

### Standard Loop

```
1. Receive user prompt
2. Add to context as user message
3. Loop:
   a. Get messages from context
   b. Call provider.complete(messages, tools)
   c. If no tool calls → return response
   d. Execute tool calls sequentially
   e. Add tool results to context
   f. Repeat from step 3
4. Return final response
```

### Tool Execution

Tools execute **sequentially** (one at a time):

```
tool_call_1 → execute → add result
tool_call_2 → execute → add result
tool_call_3 → execute → add result
```

This ensures predictable execution order and clear event sequence.

### Iteration Limit

When `max_iterations` is reached without final response:

1. Inject system reminder to agent
2. Request final response summarizing progress
3. Return whatever agent provides

Example reminder:

```
<system-reminder source="orchestrator-loop-limit">
You have reached the maximum number of iterations for this turn.
Please provide a response to the user now, summarizing your progress
and noting what remains to be done. You can continue in the next turn
if needed.

DO NOT mention this iteration limit or reminder to the user explicitly.
Simply wrap up naturally.
</system-reminder>
```

## Events

The orchestrator emits complete event streams for observability:

### Execution Events

- `execution:start` - Loop begins
  ```python
  {"prompt": "user prompt"}
  ```

- `execution:end` - Loop completes
  ```python
  {"response": "final response text"}
  ```

### Provider Events

- `provider:request` - Before LLM call
  ```python
  {
      "provider": "AnthropicProvider",
      "iteration": 3,
      "message_count": 12
  }
  ```

- `provider:response` - After LLM call
  ```python
  {
      "provider": "AnthropicProvider",
      "model": "claude-sonnet-4-5",
      "usage": {...}
  }
  ```

- `provider:error` - On LLM error
  ```python
  {
      "error_type": "completion_failed",
      "error_message": "...",
      "severity": "high"
  }
  ```

### Tool Events

- `tool:pre` - Before tool execution
  ```python
  {
      "tool_name": "bash",
      "tool_input": {"command": "ls"}
  }
  ```

- `tool:post` - After tool execution
  ```python
  {
      "tool_name": "bash",
      "result": {...}
  }
  ```

- `tool:error` - On tool error
  ```python
  {
      "error_type": "execution_failed",
      "tool": "bash",
      "error_message": "...",
      "severity": "high"
  }
  ```

### Prompt Events

- `prompt:submit` - User prompt received
  ```python
  {"prompt": "user input"}
  ```

- `prompt:complete` - Final response ready
  ```python
  {
      "response_preview": "first 200 chars...",
      "length": 1234
  }
  ```

### Orchestrator Event

- `orchestrator:complete` - Execution finished
  ```python
  {
      "orchestrator": "loop-basic",
      "turn_count": 5,
      "status": "success"
  }
  ```

## Extended Thinking

When `extended_thinking: true`, the orchestrator passes an extended thinking flag to the provider:

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
2. Add error as tool result to context
3. Continue loop (LLM sees the error)

### Timeout

If `timeout` expires:
1. Current operation completes
2. Return whatever response is available
3. Session may end gracefully

## Comparison with Other Orchestrators

| Feature | loop-basic | loop-streaming | loop-events |
|---------|------------|----------------|-------------|
| Tool execution | Sequential | Parallel | Sequential |
| Response delivery | Buffered | Streaming | Buffered |
| Event emissions | Complete | Partial | Complete |
| Scheduler integration | No | No | Yes |
| Best for | Testing, debugging | Interactive UIs | Multi-agent systems |

## Use Cases

### 1. Testing and Debugging

Complete event emissions make it easy to trace execution:

```yaml
session:
  orchestrator: loop-basic

hooks:
  - module: hooks-logging
    config:
      log_events: true  # Every event captured
```

### 2. Predictable Tool Execution

Sequential tool execution ensures deterministic order:

```
Agent calls: [read_file, edit_file, bash]
Execution:   read → edit → bash (always this order)
```

### 3. Simple Deployments

Minimal complexity for straightforward use cases:

```yaml
# Simple configuration, predictable behavior
session:
  orchestrator: loop-basic
```

## Best Practices

### 1. Set Iteration Limits for Safety

```yaml
config:
  max_iterations: 20  # Prevent infinite loops
```

### 2. Use Appropriate Timeout

```yaml
config:
  timeout: 600  # 10 minutes for complex tasks
```

### 3. Monitor Events

```yaml
hooks:
  - module: hooks-logging  # Capture all events
```

### 4. Switch to Streaming for UX

For interactive applications:

```yaml
session:
  orchestrator: loop-streaming  # Better user experience
```

## Implementation Notes

- Tool results added to context in execution order
- Context compaction handled automatically by context manager
- Provider selection uses `default_provider` from config or first available
- Cleanup functions called on session end

## See Also

- [loop-streaming](loop_streaming.md) - Streaming responses with parallel tools
- [loop-events](loop_events.md) - Event-driven with scheduler integration
- [Orchestrator Contract](../../reference/contracts/orchestrator.md) - Interface specification
