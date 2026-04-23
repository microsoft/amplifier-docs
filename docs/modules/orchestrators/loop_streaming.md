---
title: loop-streaming
description: Streaming orchestration for real-time response delivery
---

# loop-streaming Orchestrator

Streaming orchestration for real-time response delivery with parallel tool execution.

## Overview

The `loop-streaming` orchestrator provides progressive response rendering by streaming tokens as they arrive from the LLM. Tool calls execute in parallel for improved performance.

## Configuration

```yaml
session:
  orchestrator: loop-streaming

orchestrators:
  - module: loop-streaming
    source: git+https://github.com/microsoft/amplifier-module-loop-streaming@main
    config:
      max_iterations: -1              # Maximum iterations (-1 = unlimited)
      extended_thinking: false        # Enable extended thinking mode (default: false)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_iterations` | integer | `-1` | Maximum loop iterations (`-1` = unlimited) |
| `extended_thinking` | boolean | `false` | Enable extended thinking mode for supported models |
| `min_delay_between_calls_ms` | integer | `0` | Minimum delay between provider calls in milliseconds (`0` = disabled) |
| `stream_delay` | float | `0.01` | Delay between streamed tokens in seconds (artificial pacing) |
| `reasoning_effort` | string | `null` | Reasoning effort level passed to the provider (provider-specific) |

## Behavior

### Streaming Flow

```
1. Receive user prompt
2. Add to context
3. Loop:
   a. Get messages from context
   b. Call provider.stream() (or provider.complete() fallback)
   c. For each chunk:
      - Stream token to output
   d. Parse tool calls from streamed response
   e. If tool calls → execute in parallel
   f. Add results to context (deterministic order)
   g. Repeat from step 3
4. Return final response
```

### Parallel Tool Execution

Multiple tool calls execute **concurrently**:

```
tool_call_1 ──┐
tool_call_2 ──┼─ await gather() → all complete
tool_call_3 ──┘
```

Results are added to context in **original order** (deterministic):

```
[tool_result_1, tool_result_2, tool_result_3]  # Always same order
```

This ensures:
- Fast execution (parallel)
- Deterministic context (ordered results)
- Reproducible behavior

## Events

### Streaming-Specific Events

- `content_block:start` - Content block begins
  ```python
  {
      "block_type": "text",  # or "thinking", "tool_use"
      "block_index": 0,
      "total_blocks": 3,
      "metadata": {...}  # Raw block metadata if available
  }
  ```

- `content_block:end` - Content block completes
  ```python
  {
      "block_index": 0,
      "total_blocks": 3,
      "block": {...},  # Complete block data
      "usage": {...}   # Token usage (if available)
  }
  ```

### Execution Events

- `execution:start` - Streaming execution begins
- `execution:end` - Streaming execution ends
- `orchestrator:rate_limit_delay` - Rate limit delay applied between provider calls
  ```python
  {
      "delay_ms": 150.0,       # Actual delay applied (ms)
      "configured_ms": 200,    # Configured minimum (ms)
      "elapsed_ms": 50.0,      # Elapsed since last call (ms)
      "iteration": 2           # Current iteration
  }
  ```

### Standard Events

Also emits standard orchestrator events:
- `tool:pre`, `tool:post`, `tool:error`
- `provider:request`, `provider:error`
- `prompt:submit`
- `orchestrator:complete`
- `cancel:requested`, `cancel:completed`

## Extended Thinking

When `extended_thinking: true`:

```python
response = await provider.complete(chat_request, extended_thinking=True)
```

Providers supporting extended thinking (Anthropic Claude) will include thinking blocks:

```
content_block:start → type="thinking"
content_block:end   → complete thinking block
```

Hooks (e.g., `hooks-streaming-ui`) can display thinking blocks progressively.

## Comparison with Other Orchestrators

| Feature | loop-basic | loop-streaming |
|---------|------------|----------------|
| Tool execution | — | **Parallel** |
| Response delivery | — | **Streaming** |
| Streaming delivery | — | **Yes** |
| Best for | — | **Interactive UIs** |

## Use Cases

### 1. Interactive CLI

```yaml
session:
  orchestrator: loop-streaming

hooks:
  - module: hooks-streaming-ui
```

Configure display settings in your profile's `[ui]` section:

```toml
[ui]
show_thinking_stream = true
show_tool_lines = 5
```

User sees tokens appear in real-time with progressive tool output.

### 2. Web UIs

Stream tokens to browser for progressive rendering via async iteration over the streaming output.

### 3. Long-Form Content

Stream tokens to render long-form content progressively - articles, documentation, stories.

## Best Practices

### 1. Monitor Streaming Performance

Monitor token delivery and network latency for optimal user experience.

### 2. Use Streaming-Aware Hooks

```yaml
hooks:
  - module: hooks-streaming-ui  # Designed for streaming
```

### 3. Set Iteration Limits

```yaml
config:
  max_iterations: 20  # Prevent infinite loops
```

### 4. Handle Interrupts

Streaming responses can be interrupted mid-stream. Ensure your application handles partial responses gracefully.

## Performance Considerations

### Parallel Tool Execution

Parallel execution significantly improves multi-tool performance:

```
Sequential (no parallelism):
  tool1 (2s) + tool2 (3s) + tool3 (2s) = 7s total

Parallel (loop-streaming):
  max(2s, 3s, 2s) = 3s total
```

### Network Streaming

When streaming over network (WebSocket, SSE):
- Consider network latency
- Implement client-side buffering
- Handle connection drops gracefully

## Implementation Notes

- Uses async generators for streaming responses
- Tool results added in deterministic order despite parallel execution
- Context compaction handled automatically
- Supports cancellation mid-stream (graceful and immediate)
- Provider selection: uses `provider.stream()` if available, falls back to `provider.complete()` with simulated token streaming

## Error Handling

### Provider Errors

On provider error:
1. Emit `provider:error` event
2. Raise exception (error propagated to caller)
3. Exit loop

### Tool Errors

On tool execution error (during parallel batch):
1. Other tools continue executing
2. Error added as tool result
3. Loop continues (LLM sees error)

### Stream Interruption

If stream interrupted via cancellation:
- Partial response added to context
- Synthetic assistant message written to close turn
- Cancel events emitted (`cancel:requested`, `cancel:completed`)
- Session remains valid for next turn

## See Also

- [loop-basic](loop_basic.md) - Parallel execution with complete events
- [loop-events](loop_events.md) - Event-driven with scheduler integration
- [hooks-streaming-ui](../hooks/streaming_ui.md) - Streaming display hook
- [Orchestrator Contract](../../reference/contracts/orchestrator.md) - Interface specification
